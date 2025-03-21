from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import DictCursor
from enum import Enum

# Security configurations
SECRET_KEY = "your-secret-key-stored-securely"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database connection
DB_CONFIG = {
    "dbname": "your_db_name",
    "user": "your_user",
    "password": "your_password",
    "host": "your_host",
    "port": "your_port"
}

class Role(str, Enum):
    ADMIN = "admin"
    AUTOMATION = "automation"
    VIEWER = "viewer"

class Token(BaseModel):
    access_token: str
    token_type: str

class UserInDB(BaseModel):
    username: str
    email: str
    role: Role
    disabled: Optional[bool] = False

class DBConnection:
    def __init__(self):
        self.conn_params = DB_CONFIG

    def __enter__(self):
        self.conn = psycopg2.connect(**self.conn_params)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

def get_user(username: str):
    """Fetch user from database"""
    with DBConnection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                """
                SELECT username, email, role, hashed_password 
                FROM users 
                WHERE username = %s
                """,
                (username,)
            )
            user = cur.fetchone()
            if user:
                return {
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"],
                    "hashed_password": user["hashed_password"]
                }

def verify_password(plain_password: str, hashed_password: str):
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validate JWT token and return current user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

def require_role(required_roles: list[Role]):
    """Decorator to check if user has required role"""
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of these roles: {required_roles}"
            )
        return current_user
    return role_checker

# FastAPI route handlers
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login route handler"""
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Helper function to create new users (admin only)
@require_role([Role.ADMIN])
async def create_user(
    username: str,
    email: str,
    password: str,
    role: Role,
    current_user: dict = Depends(get_current_user)
):
    """Create new user (admin only)"""
    hashed_password = pwd_context.hash(password)
    
    with DBConnection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    INSERT INTO users (username, email, hashed_password, role)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (username, email, hashed_password, role)
                )
                conn.commit()
                return {"message": "User created successfully"}
            except psycopg2.IntegrityError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username or email already exists"
                )

# Example protected route
@require_role([Role.ADMIN, Role.AUTOMATION])
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {
        "message": "This is a protected route",
        "user": current_user["username"],
        "role": current_user["role"]
    }

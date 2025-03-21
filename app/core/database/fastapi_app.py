from fastapi import FastAPI
from .db_auth_sys import login, create_user, protected_route

app = FastAPI()

# Add routes
app.post("/token")(login)
app.post("/users")(create_user)
app.get("/protected")(protected_route)

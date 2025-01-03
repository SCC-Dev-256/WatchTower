from flask_socketio import SocketIO
from app.core.config.websocket_config import Config
import jwt
from jwt.exceptions import InvalidTokenError
from app.core.error_handling.decorators import handle_errors

class WebSocketAuthenticator:
    """Handles authentication for WebSocket connections using JWT.

    Attributes:
        socketio (SocketIO): The SocketIO instance for managing connections.
        config (Config): The configuration instance for accessing settings.
    """

    def __init__(self, socketio: SocketIO):
        """Initialize the WebSocketAuthenticator with the given SocketIO instance."""
        self.socketio = socketio
        self.config = Config()

    @handle_errors()
    def authenticate(self, token: str) -> bool:
        """Authenticate WebSocket connection using JWT.

        Args:
            token (str): The JWT token provided by the client.

        Returns:
            bool: True if authentication is successful, False otherwise.

        Raises:
            InvalidTokenError: If the token is invalid or expired.
        """
        try:
            payload = jwt.decode(token, self.config.SECRET_KEY, algorithms=["HS256"])
            return True
        except InvalidTokenError:
            return False

    @handle_errors()
    def on_connect(self, token: str):
        """Handle new WebSocket connection.

        Args:
            token (str): The JWT token provided by the client.

        Raises:
            ConnectionRefusedError: If authentication fails.
        """
        if not self.authenticate(token):
            raise ConnectionRefusedError("Unauthorized") 
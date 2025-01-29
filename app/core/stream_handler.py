from app.core.error_handling.decorators import handle_errors
from app.core.aja import AJAHELOClient
from app.core.error_handling.error_logging import ErrorLogger
from typing import Dict

class StreamHandler:
    def __init__(self, app):
        self.app = app
        self.logger = ErrorLogger(app)
        self.aja_client = AJAHELOClient(ip_address="192.168.1.100")

    @handle_errors(operation="start_stream", error_type="streaming", severity="critical")
    async def start_stream(self, config: Dict):
        try:
            # Validate and configure stream
            await self.aja_client.configure_stream(config)
            # Start streaming
            response = await self.aja_client.start_stream()
            self.logger.log_info("Stream started successfully", response)
        except Exception as e:
            self.logger.log_error({"service": "streaming", "error": str(e)})
            raise
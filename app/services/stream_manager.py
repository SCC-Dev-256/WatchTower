from typing import Dict, Optional
from app.core.base_service import BaseService
from app.core.error_handling import handle_errors
from app.core.error_handling.exceptions import EncoderStreamError

class StreamManager(BaseService):
    def __init__(self):
        super().__init__()
        self.retry_attempts = self.config.get('STREAM_RETRY_ATTEMPTS', 3)

    @handle_errors()
    async def start_stream(self, encoder_id: str, stream_config: Dict) -> Dict:
        """Start streaming on an encoder"""
        await self._validate_input(stream_config, ['bitrate', 'resolution'])
        
        try:
            encoder = await self.get_encoder(encoder_id)
            await self._configure_stream(encoder, stream_config)
            await self._start_streaming(encoder)
            
            return {
                "status": "success",
                "message": "Stream started successfully",
                "stream_info": await self._get_stream_info(encoder)
            }
        except Exception as e:
            raise EncoderStreamError(
                f"Failed to start stream: {str(e)}",
                encoder_id=encoder_id
            )

    @handle_errors()
    async def stop_stream(self, encoder_id: str) -> Dict:
        """Stop streaming on an encoder"""
        try:
            encoder = await self.get_encoder(encoder_id)
            await self._stop_streaming(encoder)
            
            return {
                "status": "success",
                "message": "Stream stopped successfully"
            }
        except Exception as e:
            raise EncoderStreamError(
                f"Failed to stop stream: {str(e)}",
                encoder_id=encoder_id
            ) 
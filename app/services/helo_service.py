from typing import Dict
from app.core.connection.helo_pool_manager import HeloPoolManager

class HeloService:
    def __init__(self, helo_pool_manager: HeloPoolManager):
        self.pool_manager = helo_pool_manager

    async def start_stream(self, encoder_id: str, stream_config: Dict):
        async with self.pool_manager.get_helo_connection(encoder_id) as session:
            # Start stream using existing encoder manager
            await self.pool_manager.encoder_manager.start_stream(encoder_id, stream_config)
            # Start health monitoring
            await self.pool_manager.start_health_monitoring(encoder_id) 
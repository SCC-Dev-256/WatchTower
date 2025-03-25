from typing import Dict
from app.core.connection.helo_pool_manager import HeloPoolManager
from WatchTower.app.core.auth.auth import require_api_key, roles_required
from app.core.error_handling.decorators import handle_errors



class HeloService:
    def __init__(self, helo_pool_manager: HeloPoolManager):
        self.pool_manager = helo_pool_manager

    @roles_required('admin', 'editor')
    @require_api_key
    @handle_errors()
    async def start_stream(self, encoder_id: str, stream_config: Dict):
        async with self.pool_manager.get_helo_connection(encoder_id) as session:
            # Start stream using existing encoder manager
            await self.pool_manager.encoder_manager.start_stream(encoder_id, stream_config)
            # Start health monitoring
            await self.pool_manager.start_health_monitoring(encoder_id) 
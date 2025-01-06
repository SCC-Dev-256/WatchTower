from typing import List, Dict, Optional
from app.core.database.models.encoder import HeloEncoder
from app.core.error_handling import handle_errors
from app.core.error_handling.errors.exceptions import EncoderError
from app.core.error_handling.errors.error_types import ErrorType
from app.core.rest_API_client import AJADevice
from app.core.metrics.base_metrics import BaseMetricsService
from app.core.aja.aja_client import AJAHELOClient
from app.core.aja.aja_constants import ReplicatorCommands, MediaState, AJAParameters
from app.core.aja.aja_helo_parameter_service import AJAParameterManager
from app.core.aja.aja_remediation_service import AJARemediationService
import asyncio
from app.core.auth import require_api_key, roles_required
from app.core.error_handling.decorators import handle_errors

class EncoderManager(BaseMetricsService):
    def __init__(self, db):
        super().__init__('encoder_manager')
        self.db = db
        self.device_cache = {}
        self.clients = {}
        self.param_manager = AJAParameterManager()
        self.remediation_service = AJARemediationService(self)

    @handle_errors()
    @roles_required('admin', 'editor')
    @require_api_key
    async def get_encoder(self, encoder_id: str) -> HeloEncoder:
        """Get encoder by ID with error handling"""
        await self.increment_operation('get_encoder')
        
        encoder = HeloEncoder.query.get(encoder_id)
        if not encoder:
            await self.record_error(ErrorType.RESOURCE_NOT_FOUND)
            raise EncoderError(f"Encoder {encoder_id} not found", encoder_id=encoder_id)
        return encoder

    @handle_errors()
    @roles_required('admin', 'editor')
    @require_api_key
    async def get_device(self, encoder: HeloEncoder) -> AJADevice:
        """Get or create AJA device instance"""
        await self.increment_operation('get_device')
        
        if encoder.id not in self.device_cache:
            self.device_cache[encoder.id] = AJADevice(f"http://{encoder.ip_address}")
        return self.device_cache[encoder.id]

    @handle_errors()
    @roles_required('admin', 'editor')
    @require_api_key
    async def execute_command(self, encoder_id: str, command_id: int) -> Dict:
        """Execute basic encoder command"""
        await self.log_and_track(
            f"Executing command {command_id}",
            'execute_command',
            tags={'encoder_id': encoder_id, 'command_id': command_id}
        )
        
        encoder = await self.get_encoder(encoder_id)
        device = await self.get_device(encoder)
        
        await device.set_param("eParamID_ReplicatorCommand", command_id)
        return {"status": "success", "command_id": command_id}

    @handle_errors()
    @roles_required('admin', 'editor')
    @require_api_key
    async def get_client(self, encoder_id: str) -> AJAHELOClient:
        if encoder_id not in self.clients:
            encoder = await self.get_encoder(encoder_id)
            self.clients[encoder_id] = AJAHELOClient(encoder.ip_address)
        return self.clients[encoder_id]

    @handle_errors()
    @roles_required('admin', 'editor')
    @require_api_key
    async def start_stream(self, encoder_id: str, config: Dict) -> Dict:
        client = await self.get_client(encoder_id)
        
        # Set to Record-Stream mode
        await client.set_parameter(
            AJAParameters.MEDIA_STATE, 
            MediaState.RECORD_STREAM.value
        )
        
        # Configure and start stream
        await client.configure_stream(config)
        await client.set_parameter(
            AJAParameters.REPLICATOR_COMMAND,
            ReplicatorCommands.START_STREAMING.value
        )

    async def handle_error(self, error_type: ErrorType, encoder_id: str) -> Dict:
        """Handle encoder errors through remediation service"""
        return await self.remediation_service.attempt_remediation({
            'error_type': error_type,
            'encoder_id': encoder_id
        })

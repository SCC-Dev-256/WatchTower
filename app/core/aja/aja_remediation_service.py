from typing import Dict
import logging
import sys
from app.core.error_handling.decorators import HandleErrors
from app.core.error_handling.errors.error_types import ErrorType
from app.core.error_handling import MetricsService
from app.core.error_handling.errors.exceptions import EncoderError
from app.core.aja.aja_helo_parameter_service import AJAParameterManager
from app.core.aja.machine_logic.helo_params import HeloParameters, MediaState

class AJARemediationService(MetricsService):
    """Centralized AJA device remediation service"""
    
    def __init__(self, encoder_service):
        super().__init__('aja_remediation')
        self.encoder_service = encoder_service
        self.param_manager = AJAParameterManager()
        self.logger = logging.getLogger(__name__)

    @HandleErrors()
    async def AttemptRemediation(self, error_data: Dict) -> Dict:
        """Unified remediation entry point"""
        await self.increment_operation('AttemptRemediation')
        
        encoder_id = error_data.get('encoder_id')
        error_type = error_data.get('error_type')
        helo_params = HeloParameters().device_parameters  # Load current parameters

        if not encoder_id or not error_type:
            raise EncoderError(
                "Missing encoder_id or error_type for remediation",
                error_type="remediation_invalid"
            )

        remediation_map = {
            ErrorType.STREAM_START: self.HandleStreamIssues,
            ErrorType.STREAM_QUALITY: self.HandleStreamQuality,
            ErrorType.CONNECTION_LOST: self.HandleConnectionIssues,
            ErrorType.STORAGE_FULL: self.HandleStorageIssues,
            ErrorType.MEDIA_STATE: self.HandleMediaStateError
        }
        
        handler = remediation_map.get(error_type)
        if not handler:
            return {'success': False, 'message': f'No handler for {error_type}'}
            
        result = await handler(encoder_id)
        await self._log_remediation_attempt(encoder_id, error_type, result)
        return result

    @HandleErrors()
    async def HandleMediaStateError(self, encoder_id: str) -> Dict:
        """Handle media state transition errors"""
        try:
            await self.set_media_state(encoder_id, MediaState.RECORD_STREAM)
            current_state = await self.get_media_state(encoder_id)
            return {
                'success': current_state == MediaState.RECORD_STREAM,
                'action': 'reset_media_state'
            }
        except Exception as e:
            self.logger.error(f"Media state recovery failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    @HandleErrors()
    async def HandleStreamIssues(self, encoder_id: str) -> Dict:
        # Implementation for _handle_stream_issues
        #AJA devices will restart the stream automatically when the stream is lost.
        #It does this up to 3 times before stopping. 
        #We can add a subroutine here to check the stream status and report it to the log.
        pass

    @HandleErrors()
    async def HandleStreamQuality(self, encoder_id: str) -> Dict:
        # Implementation for _handle_stream_quality
        pass

    @HandleErrors()
    async def HandleConnectionIssues(self, encoder_id: str) -> Dict:
        # Implementation for _handle_connection_issues
        #AJA Devices already have network reconnection logic built in
        #We could add subroutine here to document the network event via pings, but this is not necessary.
        #We could also add subroutine here to check the network status and report it to the log.
        
        pass

    @HandleErrors()
    async def HandleStorageIssues(self, encoder_id: str) -> Dict:
        # Implementation for _handle_storage_issues
        pass

    @HandleErrors()
    async def RemountStorage(self, encoder_id: str) -> Dict:
        # Implementation for _remount_storage
        #AJA Devices will not remount storage automatically. 
        #We need to add a subroutine to swap to another storage path if the current path is full or unavailable.
        #damaged storage devices will result in repeated restarts and few error messages. 
        #We can add a subroutine to check the storage status and report it to the log.
        pass
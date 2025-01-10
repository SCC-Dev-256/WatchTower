from typing import Dict, Optional
from dataclasses import dataclass
from app.core.aja.machine_logic.helo_params import (
    HeloDeviceParameters,
    HeloParameters,
    VideoSource,
    AudioSource,
    MediaState,
    RecordingMediaType
)
from app.core.error_handling.analysis.aja_metric_collector import MetricsCollector
import logging

logger = logging.getLogger(__name__)

@dataclass 
class IntegratedEncoderParameters:
    """
    Provides a unified interface for encoder parameters and metrics collection.
    Acts as an intermediary between raw device parameters and system integrations.
    """
    device_params: HeloDeviceParameters
    metrics_collector: MetricsCollector
    encoder_id: str

    def __init__(self, encoder_id: str):
        self.encoder_id = encoder_id
        self.device_params = HeloParameters().device_parameters
        self.metrics_collector = MetricsCollector()

    async def get_current_state(self) -> Dict:
        """Get the current state of the encoder including metrics"""
        try:
            metrics = await self.metrics_collector.collect_metrics(
                self.encoder_id,
                self.device_params
            )
            return {
                'status': 'active',
                'metrics': metrics,
                'parameters': {
                    'video_source': self.device_params.video_source.value,
                    'audio_source': self.device_params.audio_source.value,
                    'media_state': self.device_params.media_state.value,
                    'recording_media': self.device_params.recording_media_type.value
                }
            }
        except Exception as e:
            logger.error(f"Failed to get encoder state for {self.encoder_id}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def update_parameters(self, new_params: Dict) -> None:
        """Update device parameters with new values"""
        try:
            for key, value in new_params.items():
                if hasattr(self.device_params, key):
                    setattr(self.device_params, key, value)
            logger.info(f"Updated parameters for encoder {self.encoder_id}")
        except Exception as e:
            logger.error(f"Failed to update parameters for {self.encoder_id}: {str(e)}")
            raise

    async def get_health_status(self) -> Dict:
        """Get encoder health metrics"""
        try:
            metrics = await self.metrics_collector.collect_metrics(
                self.encoder_id,
                self.device_params
            )
            return {
                'network_status': metrics['network']['connected'],
                'link_errors': metrics['network']['error_count'],
                'system_temp': self.device_params.system_temperature,
                'streaming_active': self.device_params.media_state == MediaState.RECORD_STREAM
            }
        except Exception as e:
            logger.error(f"Failed to get health status for {self.encoder_id}: {str(e)}")
            return {'status': 'error', 'error': str(e)}

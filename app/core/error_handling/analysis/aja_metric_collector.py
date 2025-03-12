from typing import Dict, Optional
from app.core.aja import HeloDeviceParameters, HeloParameters
from app.core.aja import AJAParameterManager, AJAMediaState
from app.core.error_handling import BaseMetricsService
import logging

# This file contains the MetricsCollector class, which is used to collect metrics from AJA HELO devices.
# The MetricsCollector class has the following methods:
# - collect_metrics: Collects metrics for a given encoder.

# The following areas are blank and require input from the user:
# - Additional error handling logic for specific error types or logging requirements that are not yet defined.
# - Configuration details for retry logic, such as exponential backoff or jitter, that may need customization.
# - Any additional metrics or logging categories that the user might want to track.
# - Specific logic for handling different error types in the `collect_metrics` method.
# - Detailed implementation for methods like `collect_metrics`.

# Levels of abstraction that need to be made specific:
# 1. Error Handling Logic: Define specific logic for handling different types of errors (e.g., network, streaming, recording).
# 2. Retry Logic: Customize and add any additional retry mechanisms, such as exponential backoff or jitter.
# 3. Metrics: Customize and add any additional metrics that need to be tracked.
# 4. Logging: Configure log formatting and output destinations as per the application's requirements.
# 5. Error Analysis: Implement detailed logic for analyzing errors and providing insights.
# 6. Error Entry Creation: Ensure the error data captures all necessary details for each error type.
# 7. Error Processing: Define the specific steps to process and handle each error type in the `collect_metrics` method.



logger = logging.getLogger(__name__)

class MetricsCollector(BaseMetricsService):
    """Collects metrics for analysis from AJA HELO devices."""
    
    def __init__(self):
        super().__init__(service_name="AJA_HELO")
        self.parameter_manager = AJAParameterManager()
        self.media_states = {
            AJAMediaState.RECORD_STREAM: "Record-Stream",
            AJAMediaState.DATA_LAN: "Data-LAN"
        }

    async def collect_metrics(self, encoder_id: str, helo_params: Optional[HeloDeviceParameters] = None) -> Dict:
        """Collect metrics for a given encoder.
        
        Args:
            encoder_id: ID of the encoder to collect metrics from
            helo_params: Optional HeloDeviceParameters instance with current device state
            
        Returns:
            Dict containing collected metrics
        """
        try:
            if not helo_params:
                helo_params = HeloParameters().device_parameters

            # Collect streaming metrics
            streaming_metrics = {
                'state': helo_params.media_state.value,
                'format': helo_params.streaming_format,
                'duration': helo_params.streaming_duration,
                'url': helo_params.stream_url,
                'video_bitrate': helo_params.video_bit_rate,
                'audio_bitrate': helo_params.audio_bit_rate.value,
                'resolution': f"{helo_params.width}x{helo_params.height}"
            }

            # Collect network metrics
            network_metrics = {
                'connected': helo_params.network_connected,
                'link_state': helo_params.link_state,
                'error_count': helo_params.network_link_error_count,
                'interface_state': helo_params.ethernet_interface_setup_state
            }

            # Collect storage metrics
            storage_metrics = {
                'recording_media': helo_params.recording_media_type.value,
                'recording_format': helo_params.recording_format,
                'recording_duration': helo_params.recording_duration,
                'file_duration': helo_params.file_duration,
                'paths': {
                    'sd': helo_params.sd_card_record_path,
                    'usb': helo_params.usb_record_path,
                    'smb': helo_params.smb_network_record_path,
                    'nfs': helo_params.nfs_network_record_path
                }
            }

            # Log and track metrics
            await self.log_and_track(
                message=f"Collected metrics for encoder {encoder_id}",
                operation="collect_metrics",
                metrics={
                    'streaming': streaming_metrics,
                    'network': network_metrics,
                    'storage': storage_metrics
                }
            )

            return {
                'streaming': streaming_metrics,
                'network': network_metrics, 
                'storage': storage_metrics,
                'system': {
                    'name': helo_params.system_name,
                    'power_state': helo_params.power_up_state
                }
            }

        except Exception as e:
            logger.error(f"Error collecting metrics for encoder {encoder_id}: {str(e)}")
            await self.record_error(error_type="collection_error")
            raise
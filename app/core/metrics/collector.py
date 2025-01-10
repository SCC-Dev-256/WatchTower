from typing import Dict, Optional
from app.core.aja.machine_logic.helo_params import HeloDeviceParameters
from app.core.aja.aja_helo_parameter_service import AJAParameterManager, AJAMediaState
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects metrics for analysis from AJA HELO devices."""
    
    def __init__(self):
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
                helo_params = HeloDeviceParameters()

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
            raise
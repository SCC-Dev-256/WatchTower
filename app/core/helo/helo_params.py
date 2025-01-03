from app.core.aja.aja_parameters import AJAParameterManager
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# Define Enums for specific parameter types if needed
class VideoSource(Enum):
    HDMI = "HDMI"
    SDI = "SDI"
    TEST_PATTERN = "Test Pattern"

class AudioSource(Enum):
    HDMI = "HDMI"
    SDI = "SDI"
    ANALOG = "Analog"
    NONE = "None"

class AudioInputLevel(Enum):
    DB_0 = "0dB"
    DB_6 = "+6dB" 
    DB_12 = "+12dB"

class ClosedCaptioningSource(Enum):
    NONE = "None"
    AUTO = "Auto"
    ANCILLARY = "Ancillary data"
    LINE_21 = "Line 21"

class AVMute(Enum):
    OFF = "Off"
    ON = "On"

class MediaState(Enum):
    RECORD_STREAM = "Record-Stream"
    DATA_LAN = "Data-LAN"

class EncodeType(Enum):
    H264 = "H.264"

class DroppedFramesBehavior(Enum):
    CONTINUE = "Continue"
    STOP = "Stop"

class LossOfVideoBehavior(Enum):
    STOP = "Stop"
    RECORD_TEST_PATTERN = "Record Test Pattern"

class SDI2KInputProcessing(Enum):
    CENTER_CUT = "Center cut"
    DOWNSCALE = "Downscale"

class StreamType(Enum):
    RTMP = "RTMP"
    RTSP = "RTSP"
    RTP_UDP_TS = "RTP / UDP-TS"
    HLS = "HLS"

class RTSPAuthentication(Enum):
    NONE = "None"
    BASIC = "Basic"
    DIGEST = "Digest"

class VideoGeometry(Enum):
    USE_SELECTED_INPUT = "Use Selected Input"
    MANUAL = "Manual"

class AspectRatio(Enum):
    AUTO = "Auto"
    RATIO_4_3 = "4:3"
    RATIO_16_9 = "16:9"
    RATIO_17_9 = "17:9"

class RecordingFileType(Enum):
    MOV = "MOV"
    TS = "TS"
    MP4 = "MP4"

class RecordingMediaType(Enum):
    SD = "SD"
    USB = "USB"
    SMB = "SMB Network Share"
    NFS = "NFS Network Share"

class SMBDialect(Enum):
    AUTO = "Auto"
    SMB_3_0 = "SMB 3.0"
    SMB_2_1 = "SMB 2.1"
    SMB_2_0 = "SMB 2.0"
    SMB_1_0 = "SMB 1.0"

class AudioBitRate(Enum):
    KBPS_32 = "32 kbps"
    KBPS_64 = "64 kbps"
    KBPS_96 = "96 kbps"
    KBPS_128 = "128 kbps"
    KBPS_192 = "192 kbps"
    KBPS_256 = "256 kbps"

@dataclass
class HeloDeviceParameters:
    # Video/Audio Parameters
    video_source: VideoSource = VideoSource.SDI
    audio_source: AudioSource = AudioSource.SDI
    audio_input_level: AudioInputLevel = AudioInputLevel.DB_0
    audio_delay: int = 0
    closed_captioning_source: ClosedCaptioningSource = ClosedCaptioningSource.NONE
    av_mute: AVMute = AVMute.OFF
    media_state: MediaState = MediaState.RECORD_STREAM
    stream_url: Optional[str] = None
    streaming_duration: str = "00:00:00:00"
    streaming_format: Optional[str] = None
    recording_duration: str = "00:00:00:00"
    recording_format: Optional[str] = None
    recording_filename: Optional[str] = None
    file_duration: str = "00:00:00:00"
    encode_type: str = "H.264"
    width: int = 1280
    height: int = 720
    video_bit_rate: int = 20000
    audio_bit_rate: AudioBitRate = AudioBitRate.KBPS_128
    rtsp_authentication: RTSPAuthentication = RTSPAuthentication.NONE
    rtsp_username: Optional[str] = None
    rtsp_password: Optional[str] = None
    recording_file_type: RecordingFileType = RecordingFileType.MOV
    recording_media_type: RecordingMediaType = RecordingMediaType.SD
    smb_dialect: SMBDialect = SMBDialect.AUTO
    
    # Network/Connection Parameters
    ip_address_type: str = "DHCP"
    ip_address: str = "192.168.0.2"
    subnet_mask: str = "255.255.255.0"
    default_gateway: str = "192.168.0.1"
    mac_address: str = "00:0C:17:3A:26:D0"
    ip_address_offered: Optional[str] = None
    dhcp_commit: int = 0
    dhcp_state: str = "None"
    network_connected: bool = False
    dns_search: Optional[str] = None
    dns_search_path: Optional[str] = None
    primary_dns_server: Optional[str] = None
    secondary_dns_server: Optional[str] = None

    # Error States and Monitoring
    link_state: Optional[str] = None
    network_link_error_count: int = 0
    ethernet_interface_setup_state: str = "Uninitialized"
    dropped_frames_record_behavior: str = "Continue"
    dropped_frames_stream_behavior: str = "Continue"
    loss_of_video_behavior: str = "Record Test Pattern"

    # Media Storage Paths
    sd_card_record_path: Optional[str] = None
    usb_record_path: Optional[str] = None
    smb_server_address: Optional[str] = None
    smb_network_record_path: Optional[str] = None
    nfs_server_address: Optional[str] = None
    nfs_network_record_path: Optional[str] = None

    # Authentication Parameters
    domain: Optional[str] = None
    domain_username: Optional[str] = None
    domain_password: Optional[str] = None
    rtmp_username: Optional[str] = None
    rtmp_password: Optional[str] = None
    rtmp_handshake_mode: str = "Auto"
    rtmp_server_url: Optional[str] = None
    rtmp_stream_key: Optional[str] = None

    # Stream Configuration
    rtsp_stream_name: str = "Stream"
    rtsp_port: int = 554
    rtp_udp_ts_destination_url: Optional[str] = None
    pcap_stream_diagnostic: bool = False
    rtp_udp_traffic_shaping: bool = False
    auto_recover_streaming: bool = True

    # System Settings
    system_name: str = "aja-helo-1HE010186"
    front_panel_button_lock: bool = False
    power_up_state: str = "Idle"
    user_authentication: bool = False

class HeloParameters:
    """Encapsulates HELO device parameters for analysis"""

    def __init__(self):
        self.parameter_manager = AJAParameterManager()
        self.device_parameters = HeloDeviceParameters()
        self._load_parameters()

    def _load_parameters(self):
        """Load specific parameters for HELO device"""
        params = self.parameter_manager.parameters
        for name, param in params.items():
            formatted_name = self._format_param_name(name)
            if hasattr(self.device_parameters, formatted_name):
                setattr(self.device_parameters, formatted_name, param.default_value)

    def _format_param_name(self, name: str) -> str:
        """Format parameter name to a valid attribute name"""
        return name.lower().replace(" ", "_").replace("/", "_").replace("-", "_")

# Example usage
helo_params = HeloParameters()
print(helo_params.device_parameters.ip_address)  # Access a specific parameter

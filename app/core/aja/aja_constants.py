from enum import Enum

class ReplicatorCommands(Enum):
    START_RECORDING = 1
    STOP_RECORDING = 2
    START_STREAMING = 3
    STOP_STREAMING = 4
    SHUTDOWN = 5

class MediaState(Enum):
    RECORD_STREAM = 0
    DATA_LAN = 1

class AJAParameters:
    # From Parameter_Configuration_Table.csv
    REPLICATOR_COMMAND = "eParamID_ReplicatorCommand"
    MEDIA_STATE = "eParamID_MediaState"
    RECORDING_PROFILE = "eParamID_RecordingProfileSel"
    STREAMING_PROFILE = "eParamID_StreamingProfileSel"
    STREAM_HEALTH = "eParamID_StreamHealth"
    NETWORK_BANDWIDTH = "eParamID_NetworkBandwidth"
    DROPPED_FRAMES = "eParamID_DroppedFrames"

class AJAStreamParams:
    """AJA Stream Parameters"""
    STREAM_URL = "streamUrl"
    BITRATE = "bitrate"
    RESOLUTION = "resolution"
    FRAME_RATE = "frameRate"
    AUDIO_CHANNELS = "audioChannels"
    AUDIO_BITRATE = "audioBitrate"
    PROTOCOL = "protocol"
    ENCODING = "encoding"
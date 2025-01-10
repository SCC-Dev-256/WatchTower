import requests
import logging

logger = logging.getLogger(__name__)

def recall_preset(device_url, preset_num):
    """Recall a preset on the HELO device."""
    param_id = "eParamID_RegisterRecall"
    stream_url = f"{device_url}/config?action=set&paramid={param_id}&value={preset_num}"
    response = requests.get(stream_url)
    if response.status_code == requests.codes.ok:
        logger.info(f"Preset {preset_num} recall requested.")
        return True
    logger.error(f"Failed to request preset {preset_num} recall.")
    return False

def set_recording_name(device_url, filename_prefix):
    """Set the recording filename prefix on the HELO device."""
    param_id = "eParamID_FilenamePrefix"
    legalized_prefix = requests.utils.quote(filename_prefix)
    name_url = f"{device_url}/config?action=set&paramid={param_id}&value={legalized_prefix}"
    response = requests.get(name_url)
    if response.status_code == requests.codes.ok:
        logger.info(f"Recording name set to {legalized_prefix}.")
        return True
    logger.error(f"Failed to set recording name to {legalized_prefix}.")
    return False

def start_recording(device_url):
    """Start recording on the HELO device."""
    param_id = "eParamID_ReplicatorCommand"
    value = 1  # START_RECORDING
    record_url = f"{device_url}/config?action=set&paramid={param_id}&value={value}"
    response = requests.get(record_url)
    if response.status_code == requests.codes.ok:
        logger.info("Recording started.")
        return True
    logger.error("Failed to start recording.")
    return False

def stop_recording(device_url):
    """Stop recording on the HELO device."""
    param_id = "eParamID_ReplicatorCommand"
    value = 2  # STOP_RECORDING
    stop_url = f"{device_url}/config?action=set&paramid={param_id}&value={value}"
    response = requests.get(stop_url)
    if response.status_code == requests.codes.ok:
        logger.info("Recording stopped.")
        return True
    logger.error("Failed to stop recording.")
    return False

def start_streaming(device_url):
    """Start streaming on the HELO device."""
    param_id = "eParamID_ReplicatorCommand"
    value = 3  # START_STREAMING
    stream_url = f"{device_url}/config?action=set&paramid={param_id}&value={value}"
    response = requests.get(stream_url)
    if response.status_code == requests.codes.ok:
        logger.info("Streaming started.")
        return True
    logger.error("Failed to start streaming.")
    return False

def stop_streaming(device_url):
    """Stop streaming on the HELO device."""
    param_id = "eParamID_ReplicatorCommand"
    value = 4  # STOP_STREAMING
    stop_url = f"{device_url}/config?action=set&paramid={param_id}&value={value}"
    response = requests.get(stop_url)
    if response.status_code == requests.codes.ok:
        logger.info("Streaming stopped.")
        return True
    logger.error("Failed to stop streaming.")
    return False

def verify_streaming(device_url):
    """Verify if streaming is active on the HELO device."""
    param_id = "eParamID_StreamingState"
    verify_url = f"{device_url}/config?action=get&paramid={param_id}"
    response = requests.get(verify_url)
    if response.status_code == requests.codes.ok:
        streaming_state = response.json().get('value')
        if streaming_state == 'active':
            logger.info("Streaming is active.")
            return True
        else:
            logger.info("Streaming is not active.")
            return False
    logger.error("Failed to verify streaming state.")
    return False

def verify_recording(device_url):
    """Verify if recording is active on the HELO device."""
    param_id = "eParamID_RecordingState"
    verify_url = f"{device_url}/config?action=get&paramid={param_id}"
    response = requests.get(verify_url)
    if response.status_code == requests.codes.ok:
        recording_state = response.json().get('value')
        if recording_state == 'active':
            logger.info("Recording is active.")
            return True
        else:
            logger.info("Recording is not active.")
            return False
    logger.error("Failed to verify recording state.")
    return False

# Add more functions as needed for other HELO device commands. 
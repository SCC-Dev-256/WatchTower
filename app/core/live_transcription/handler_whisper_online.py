from .whisper_streaming.whisper_online import audio_has_not_ended, lan, OnlineASRProcessor, WhisperTimestampedASR
import ffmpeg

src_lan = "en"  # source language
tgt_lan = "en"  # target language  -- same as source for ASR, "en" if translate task is used

# Initialize WhisperTimestampedASR
asr = WhisperTimestampedASR(lan, "large-v2")  # loads and wraps Whisper model

# Set options if needed
asr.set_translate_task()  # it will translate from lan into English
asr.use_vad()  # Enable VAD

# Create processing object with default buffer trimming option
online = OnlineASRProcessor(asr)

# Define the source URL for the live stream
src = 'Spacefiller' #'https://reflect-vod-scctv.cablecast.tv/live-63/live/live.m3u8'

#__________________________________________________________________________________________


def convert_to_wav(src, start_time, duration):
    out, _ = (
        ffmpeg
        .input(src, ss=start_time, t=duration)
        .output('pipe:', format='wav')
        .run(capture_stdout=True, capture_stderr=True)
    )
    return out

# Define the buffer size and duration for each chunk
buffer_size = 16000  # 1 second buffer size for 16kHz audio
chunk_duration = 1  # 1 second duration

# Initialize the start time
start_time = 0

while audio_has_not_ended:   # processing loop:
    # Convert the live stream to wav chunk
    audio_chunk = convert_to_wav(src, start_time, chunk_duration)
    
    # Insert the audio chunk into the ASR processor
    online.insert_audio_chunk(audio_chunk)
    
    # Process the audio chunk and get the transcription
    transcription = online.process_iter()
    
    # Print the transcription
    print(transcription)  # do something with current partial output
    
    # Increment the start time for the next chunk
    start_time += chunk_duration

# At the end of this audio processing
final_transcription = online.finish()
print(final_transcription)  # do something with the last output



online.init()  # refresh if you're going to re-use the object for the next audio

def format_to_srt(transcription):
    srt_content = []
    for i, (start, end, text) in enumerate(transcription, start=1):
        start_time = format_time_srt(start)
        end_time = format_time_srt(end)
        srt_content.append(f"{i}\n{start_time} --> {end_time}\n{text}\n")
    return "\n".join(srt_content)

def format_time_srt(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = (seconds - int(seconds)) * 1000
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds):03}"

srt_content = format_to_srt(final_transcription)
with open("subtitles.srt", "w") as srt_file:
    srt_file.write(srt_content)

import subprocess

def merge_subtitles_with_stream(src_stream_url, srt_file_path, output_stream_url):
    """
    Merges subtitles with the live stream using ffmpeg.
    
    :param src_stream_url: URL of the input live stream
    :param srt_file_path: Path to the SRT file
    :param output_stream_url: URL of the output stream with subtitles
    """
    command = [
        'ffmpeg',
        '-i', src_stream_url,
        '-vf', f"subtitles={srt_file_path}",
        '-c:a', 'copy',
        '-f', 'flv',  # Assuming the output stream is in FLV format
        output_stream_url
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Subtitles merged successfully into the stream at {output_stream_url}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while merging subtitles: {e}")

# Example usage
src_stream_url = "https://example.com/live/stream"
output_stream_url = "rtmp://example.com/live/output_stream"
#obviously this is not the actual stream url, and the output stream url is not a real one either
#this is just an example to show how to merge subtitles with the stream
#we need to create a system to input stream urls and output stream urls.
#ideally based on each city, we have a different stream url and output stream url...

merge_subtitles_with_stream(src_stream_url, srt_content, output_stream_url)



# ffmpeg -i input_video.mp4 -vf "subtitles=subtitles.srt" -c:a copy output_video_with_subtitles.mp4
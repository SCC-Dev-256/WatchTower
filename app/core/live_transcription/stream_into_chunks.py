import torchaudio
import numpy as np
import requests
import io
import ffmpeg
import sounddevice as sd

# Define the source URL for the live stream
src = 'https://reflect-vod-scctv.cablecast.tv/live-63/live/live.m3u8'

# Initialize the StreamReader
stream_reader = torchaudio.io.StreamReader(src, format='m3u8', option=None, buffer_size=4096)

# Set the output format for the audio stream
stream_reader.add_basic_audio_stream(frames_per_chunk=16000, sample_rate=16000)

# Function to process audio chunks
def receive_audio_stream():
    # Use ffmpeg to convert the live stream into wav chunks
    process = (
        ffmpeg
        .input(src)
        .output('pipe:', format='wav', acodec='pcm_s16le', ac=1, ar='16000')
        .run_async(pipe_stdout=True)
    )

    while True:
        in_bytes = process.stdout.read(4096)
        if not in_bytes:
            break
        audio_chunk = np.frombuffer(in_bytes, np.int16)
        yield audio_chunk


def process_audio_chunks():
    for audio_chunk in receive_audio_stream():
        # Convert the chunk to a numpy array
        working_audio_chunk = audio_chunk[0].numpy()

        # Pass the audio chunk to the whisper_online module
        # This is a placeholder for the actual function call
        # You need to implement the function to handle the audio chunk
        transcribe_audio_chunk(working_audio_chunk)

# Placeholder function to transcribe audio chunks
def transcribe_audio_chunk(working_audio_chunk):
    # Here you would call the transcription function from whisper_online.py
    # For example, you might have a function like:
    # result = whisper_online.transcribe(audio_chunk)
    # print(result)
    pass

# Start processing the audio stream
process_audio_chunks()





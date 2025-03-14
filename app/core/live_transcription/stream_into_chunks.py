import sys
import argparse
import torchaudio
import numpy as np
import requests
import io
import ffmpeg
import sounddevice as sd

from WatchTower.app.core.live_transcription.whisper_streaming.whisper_online import asr_factory, output_transcript

# Define the source URL for the live stream
src = 'https://reflect-vod-scctv.cablecast.tv/live-63/live/live.m3u8'

# Initialize the StreamReader
stream_reader = torchaudio.io.StreamReader(src, format='m3u8', option=None, buffer_size=4096)

# Set the output format for the audio stream
stream_reader.add_basic_audio_stream(frames_per_chunk=16000, sample_rate=16000)

# Set up argument parser
parser = argparse.ArgumentParser(description="Process live audio stream into text.")
parser.add_argument('--model', type=str, default='large-v2', help='Whisper model size to use')
parser.add_argument('--lan', type=str, default='en', help='Language code for transcription')
parser.add_argument('--min-chunk-size', type=float, default=1.0, help='Minimum audio chunk size in seconds')
args = parser.parse_args()

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
        print(f"audio_chunk created: {audio_chunk}")
        yield audio_chunk

def process_audio_chunks():
    # Initialize ASR and online processor
    asr, online = asr_factory(args, logfile=sys.stderr)
    
    # Buffer to store audio chunks
    audio_buffer = []

    # Process each audio chunk from the stream
    for audio_chunk in receive_audio_stream():
        # Append the audio chunk to the buffer
        audio_buffer.append(audio_chunk)

        # Convert the buffer to a numpy array for processing
        working_audio_chunk_array = np.concatenate(audio_buffer)

        # Insert the audio chunk into the online processor
        online.insert_audio_chunk(working_audio_chunk_array)

        # Process the audio chunk and get the result
        result = online.process_iter()

        # Output the transcription result
        output_transcript(result)

        # Clear the buffer after processing
        audio_buffer.clear()

# Placeholder function to transcribe audio chunks
def transcribe_audio_chunk(working_audio_chunk_array):
    # Here you would call the transcription function from whisper_online.py
    # For example, you might have a function like:
    # result = whisper_online.transcribe(audio_chunk)
    # print(result)
    pass

# Start processing the audio stream
process_audio_chunks()





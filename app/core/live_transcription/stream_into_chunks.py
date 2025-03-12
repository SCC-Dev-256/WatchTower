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
        yield audio_chunk

def process_audio_chunks():
    asr, online = asr_factory(args, logfile=sys.stderr)
    for audio_chunk in receive_audio_stream():
        # Transcribe the audio chunk using whisper_online module
        online.insert_audio_chunk(audio_chunk)
        result = online.process_iter()
        output_transcript(result)
        pass

# Placeholder function to transcribe audio chunks
def transcribe_audio_chunk(working_audio_chunk_array):
    # Here you would call the transcription function from whisper_online.py
    # For example, you might have a function like:
    # result = whisper_online.transcribe(audio_chunk)
    # print(result)
    pass

# Start processing the audio stream
process_audio_chunks()





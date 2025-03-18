import asyncio
import logging
from typing import Optional
from dataclasses import dataclass
import numpy as np
import ffmpeg
import argparse

from app.core.live_transcription.whisper_streaming.whisper_online import asr_factory, OnlineASRProcessor, WhisperTimestampedASR, online_processor
from app.core.aja.client import AJAHELOClient, AJAClientError

logger = logging.getLogger(__name__)

@dataclass
class StreamConfig:
    """Configuration for stream processing"""
    ip_address: str
    stream_url: str
    model: str = "large-v2"
    language: str = "en"
    min_chunk_size: float = 1.0
    chunk_size: int = 4096

class LiveCaptioningService:
    """Service to handle live captioning of AJA device streams.
    This is a non-critical service that adds captions to streams.
    If transcription fails, the service will gracefully degrade without
    affecting the main stream flow between input and output stream keys.
    """
    
    def __init__(self, config: StreamConfig):
        self.config = config
        self.asr = None
        self.online_processor = None
        self._initialize_asr()
        self._transcription_failed = False

    def _initialize_asr(self):
        """Initialize the ASR processor with configuration"""
        args = argparse.Namespace(
            model=self.config.model,
            lan=self.config.language,
            min_chunk_size=self.config.min_chunk_size
        )
        self.asr, self.online_processor = asr_factory(args)
        logger.info(f"ASR initialized with model {self.config.model}")

    async def _process_audio_chunk(self, chunk: np.ndarray) -> Optional[str]:
        """Process a single audio chunk and return transcription"""
        self.online_processor.insert_audio_chunk(chunk)
        result = self.online_processor.process_iter()
        if result[0] is not None:
            return result[2]  # Return transcribed text
        return None

    async def process_stream(self):
        """Main stream processing loop. Handles transcription failures gracefully
        without disrupting the main stream flow."""
        async with AJAHELOClient(self.config.ip_address) as aja_client:
            try:
                await aja_client.start_stream()
                logger.info("Stream started successfully")

                process = (
                    ffmpeg
                    .input(self.config.stream_url, f='m3u8')
                    .output('pipe:', 
                           format='wav',
                           acodec='pcm_s16le',
                           ac=1,
                           ar='16000')
                    .run_async(pipe_stdout=True)
                )

                while True:
                    try:
                        in_bytes = process.stdout.read(self.config.chunk_size)
                        if not in_bytes:
                            break
                            
                        audio_chunk = np.frombuffer(in_bytes, np.int16).astype(np.float32) / 32768.0
                        transcription = await self._process_audio_chunk(audio_chunk)
                        
                        if transcription and not self._transcription_failed:
                            await self._handle_transcription(transcription, aja_client)
                            
                    except Exception as e:
                        logger.error(f"Transcription error (non-critical): {e}")
                        self._transcription_failed = True
                        # Continue stream processing even if transcription fails
                        continue
                        
            except AJAClientError as e:
                logger.error(f"AJA client error: {e}")
                raise
            finally:
                try:
                    await aja_client.stop_stream()
                except Exception as e:
                    logger.error(f"Error stopping stream: {e}")

    async def _handle_transcription(self, transcription: str, aja_client: AJAHELOClient):
        """Handle the transcription result. If this fails, it only affects captions,
        not the main stream flow."""
        try:
            logger.info(f"New transcription: {transcription}")
            # Implement caption overlay logic here
            pass
        except Exception as e:
            logger.error(f"Caption handling error (non-critical): {e}")
            self._transcription_failed = True

# Usage example
async def main():
    config = StreamConfig(
        ip_address="192.168.1.100",
        stream_url="http://example.com/stream.m3u8"
    )
    
    service = LiveCaptioningService(config)
    await service.process_stream()

if __name__ == "__main__":
    asyncio.run(main())

# At the end of this audio processing
final_transcription = online_processor.finish()
print(final_transcription)  # do something with the last output

online_processor.init()  # refresh if you're going to re-use the object for the next audio

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
    
    #the code beneath here is rough. there is confusion around the input and output stream keys, names, and urls. 
    #this will need to be cleaned up in the future.
    #Need to make more cetrainty on how to properly interface with the database.
    #Need to make more cetrainty on how to properly interface with the ffmpeg command relative to the inputs and outputs.
        
import subprocess

def merge_subtitles_with_stream(src_stream_url, srt_file_path, output_stream_url):
    """
    Merges subtitles with the live stream using ffmpeg.
    
    :param src_stream_url: URL of the input live stream ---- This is essentially a place holder for the input stream key
    :param srt_file_path: Path to the SRT file
    :param output_stream_url: URL of the output stream with subtitles
    """
    command = [
        'ffmpeg',
        '-i', src_stream_url, #
        '-vf', f"subtitles={srt_file_path}", 
        '-c:a', 'copy',
        '-m', 'm3u8',  # Assuming the output stream is in m3u8 format
        output_stream_url
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Subtitles merged successfully into the stream at {output_stream_url}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while merging subtitles: {e}")

import psycopg2

def get_stream_keys(stream_key_name):
    """
    Fetches the input and output stream keys from the database based on the stream key name.
    
    :param stream_key_name: The stream key name
    :return: Tuple containing the input stream key and the output stream key
    """
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            dbname="your_db_name",
            user="your_db_user",
            password="your_db_password",
            host="your_db_host",
            port="your_db_port"
        )
        cursor = connection.cursor()
        
        # Query to fetch the stream keys based on the stream key name
        query = """
        SELECT input_stream_key, output_stream_key
        FROM stream_keys
        WHERE stream_key_name = %s
        """
        cursor.execute(query, (stream_key_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0], result[1]
        else:
            raise ValueError(f"No stream keys found for stream key name: {stream_key_name}")
    
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error fetching stream keys: {error}")
        raise
    
    finally:
        if connection:
            cursor.close()
            connection.close()

# Example usage
stream_key_name = "example_stream_key_name"
input_stream_key, output_stream_key = get_stream_keys(stream_key_name)

merge_subtitles_with_stream(input_stream_key, srt_content, output_stream_key)

#we need to make an error system that will check if the stream is working, and if it is not, the AJA device will be provided with the original connection.
#this will be a table in the database that will have the stream url, the output stream url, and the error message.
#the error message will be a description of the error that will be used to determine the action to take.
#the failover action to take will be to provide the AJA device with the original connection.
#the original connection will be the stream url that is provided by the user.

# ffmpeg -i input_video.mp4 -vf "subtitles=subtitles.srt" -c:a copy output_video_with_subtitles.mp4
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
    """Configuration for stream processing.
    
    This configuration bridges the AJA device streaming system with the Whisper
    transcription service. It contains parameters needed for both stream handling
    and transcription processing.
    
    Attributes:
        ip_address: IP address of the AJA device
        stream_url: HLS stream URL from the AJA device
        model: Whisper model size (default: "large-v2")
        language: Source language for transcription (default: "en")
        min_chunk_size: Minimum audio chunk size for processing
        chunk_size: Size of audio chunks for ffmpeg processing
    """
    ip_address: str
    stream_url: str
    model: str = "large-v2"
    language: str = "en"
    min_chunk_size: float = 1.0
    chunk_size: int = 4096

class LiveCaptioningService:
    """Service to handle live captioning of AJA device streams.
    Designed for minimal resource usage:
    - Only extracts audio stream when transcription is active
    - No video re-encoding
    - Automatic bypass on transcription failure
    """
    
    def __init__(self, config: StreamConfig):
        """Initialize the captioning service.
        
        Args:
            config: StreamConfig object containing all necessary parameters
                   for both AJA device streaming and Whisper transcription
        """
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
        """Main stream processing loop with minimal encoding overhead.
        On transcription failure, bypasses all audio processing
        and returns to direct stream passthrough."""
        async with AJAHELOClient(self.config.ip_address) as aja_client:
            try:
                # Start with direct stream passthrough
                await aja_client.start_stream()
                logger.info("Stream started successfully")

                if not self._transcription_failed:
                    # Only extract audio stream, ignore video
                    process = (
                        ffmpeg
                        .input(self.config.stream_url, f='m3u8')
                        .output('pipe:', 
                               format='wav',
                               acodec='pcm_s16le',
                               ac=1,
                               ar='16000',
                               vn=True)  # Skip video processing
                        .run_async(pipe_stdout=True)
                    )

                    while not self._transcription_failed:
                        try:
                            in_bytes = process.stdout.read(self.config.chunk_size)
                            if not in_bytes:
                                break
                                
                            audio_chunk = np.frombuffer(in_bytes, np.int16).astype(np.float32) / 32768.0
                            transcription = await self._process_audio_chunk(audio_chunk)
                            
                            if transcription:
                                await self._handle_transcription(transcription, aja_client)
                                
                        except Exception as e:
                            logger.error(f"Transcription error (non-critical): {e}")
                            self._transcription_failed = True
                            # Stop audio processing
                            process.kill()
                            break

            except AJAClientError as e:
                logger.error(f"AJA client error: {e}")
                raise
            finally:
                # Ensure stream continues or stops as needed
                if not self._transcription_failed:
                    try:
                        await aja_client.stop_stream()
                    except Exception as e:
                        logger.error(f"Error stopping stream: {e}")

    async def _handle_transcription(self, transcription: str, aja_client: AJAHELOClient):
        """Handle the transcription result and integrate with AJA device.
        
        This method bridges the Whisper transcription output with the AJA
        device's streaming capabilities. It handles:
        1. Formatting transcriptions into captions
        2. Integrating captions with the stream
        3. Managing caption overlay failures
        
        Failures in this method only affect caption generation and do not
        impact the main stream flow between input and output stream keys matrix. However, it will 
        
        Args:
            transcription: Transcribed text from Whisper
            aja_client: AJA device client for stream management
        """
        try:
            logger.info(f"New transcription: {transcription}")
            # Implement caption overlay logic here
            pass
        except Exception as e:
            logger.error(f"Caption handling error (non-critical): {e}")
            self._transcription_failed = True

# Usage example. In real life this will connect to the URL from Youtube. which is a static URL I believe. 
#The things that matter are the input and output stream keys. 

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

#Written - 3/17/2025 
#we need to make an error system that will check if the stream is working, and if it is not, the AJA device will be provided with the original connection.
#this will be a table in the database that will have the stream url, the output stream url, and the error message.
#the error message will be a description of the error that will be used to determine the action to take.
#the failover action to take will be to provide the AJA device with the original connection.
#the original connection will be the stream url that is provided by the user.

# ffmpeg -i input_video.mp4 -vf "subtitles=subtitles.srt" -c:a copy output_video_with_subtitles.mp4
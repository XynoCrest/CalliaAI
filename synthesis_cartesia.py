from cartesia import Cartesia
import base64
import shutil
import subprocess
import threading
from key_retriever import get_cartesia_key

def synthesize_audio(input: str, stop_event):
    audio_stream = audio_generator(input)
    stream(audio_stream, stop_event)

def audio_generator(input: str):
    client = Cartesia(
        api_key = get_cartesia_key(),
    )
    
    # Stream response from Cartesia
    audio_stream = client.tts.sse(
        model_id = "sonic-turbo",
        transcript = input,
        voice={
            "mode": "id",
            # Voice IDs
            # Savannah        - "78ab82d5-25be-4f7d-82b3-7ad64e5b85b2"
            # Madison         - "e73ba10d-6340-4815-8b5d-cdac46680857"
            # Joan of Ark     - "c9440d34-5641-427b-bbb7-80ef7462576d"
            # Joan            - "5abd2130-146a-41b1-bcdb-974ea8e19f56"
            # Connie          - "8d8ce8c9-44a4-46c4-b10f-9a927b99a853"
            # Cathy (British) - "031851ba-cc34-422d-bfdb-cdbb7f4651ee"
            # Jacqueline      - "9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"
            "id": "e73ba10d-6340-4815-8b5d-cdac46680857",
        },
        language="en",
        output_format={
            "container": "raw",
            "sample_rate": 44100,
            "encoding": "pcm_f32le",
        },
    )

    audio_chunks = []
    for chunk in audio_stream:
        audio_chunks.append(chunk)

    return audio_chunks

def is_installed(lib_name: str) -> bool:
    return shutil.which(lib_name) is not None

def stream(audio_stream, stop_event: threading.Event) -> bytes:
    if not is_installed("mpv"):
        message = (
            "mpv not found, necessary to stream audio. "
            "On mac you can install it with 'brew install mpv'. "
            "On linux and windows you can install it from https://mpv.io/"
        )
        raise ValueError(message)

    mpv_command = [
        "mpv", 
        "--no-cache", 
        "--no-terminal",
        "--demuxer=rawaudio", 
        "--demuxer-rawaudio-rate=44100",
        "--demuxer-rawaudio-format=float",  
        "--demuxer-rawaudio-channels=1",
        "--", 
        "fd://0"
    ]
    mpv_process = subprocess.Popen(
        mpv_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    audio = b"" 
    for chunk in audio_stream:
        if stop_event.is_set():
            break
        if chunk is not None:
            decoded_chunk = base64.b64decode(chunk.data)
            mpv_process.stdin.write(decoded_chunk)  
            mpv_process.stdin.flush()
            audio += decoded_chunk
    if mpv_process.stdin:
        mpv_process.stdin.close()
    mpv_process.wait()

    return audio

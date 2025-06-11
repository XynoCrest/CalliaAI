from elevenlabs.client import ElevenLabs
from elevenlabs.core.api_error import ApiError
from key_retriever import get_elevenlabs_key
import shutil
import subprocess
from typing import Iterator

mpv_process = None

def synthesize_audio(input: str):
    # Initialize the Eleven Labs client
    client = ElevenLabs(
      api_key = get_elevenlabs_key(),
    )

    # Create an audio stream object
    audio_stream = client.text_to_speech.stream(
        text = input,
        # Voice IDs
        # Brittney - "kPzsL2i3teMYv0FxEYQ6"
        # Juniper  - "aMSt68OGf4xUZAnLpTU8"
        voice_id = "aMSt68OGf4xUZAnLpTU8",
        model_id = "eleven_flash_v2"
    )

    # Cache the input incase of API Error
    global cached_input 
    cached_input = input

    # Generate and Stream speech from the input text
    stream(audio_stream)
    return

def is_installed(lib_name: str) -> bool:
    return shutil.which(lib_name) is not None

def stream(audio_stream: Iterator[bytes]) -> bytes:
    if not is_installed("mpv"):
        message = (
            "mpv not found, necessary to stream audio. "
            "On mac you can install it with 'brew install mpv'. "
            "On linux and windows you can install it from https://mpv.io/"
        )
        raise ValueError(message)

    mpv_command = ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"]
    global mpv_process
    mpv_process = subprocess.Popen(
        mpv_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    audio = b""
    try:
        for chunk in audio_stream:
            if chunk:
                try:
                    mpv_process.stdin.write(chunk)
                    mpv_process.stdin.flush()
                except:
                    break
                audio += chunk
    except ApiError as e:
        print(f"API Error: {e.body['detail']['message']}. Retrying with different key!\n")
        synthesize_audio(cached_input)
    finally:
        if mpv_process.stdin:
            try:
                mpv_process.stdin.close()
            except:
                pass
        mpv_process.wait()
        mpv_process = None

    return audio

from groq import Groq
import time
import io
import soundfile as sf
import sounddevice as sd
from key_retriever import get_groq_key

def synthesize_audio(input: str, stop_event):
    # Initialize the Groq client
    client = Groq(
        api_key = get_groq_key()
    )

    # Generate speech from the input text
    api_call_latency_start = time.time()
    
    speech = client.audio.speech.create(
        model = "playai-tts",
        voice = "Arista-PlayAI",
        input = input,
        response_format = "wav"
    )
    
    api_call_latency_end = time.time()

    # Play the Audio
    speech_bytes = b"".join(speech.iter_bytes())
    speech_array, sample_rate = sf.read(io.BytesIO(speech_bytes))
    sd.play(speech_array, sample_rate+1000)
    
    # Keep checking if playback is done or stop_event is set
    while sd.get_stream().active:
        if stop_event.is_set():
            sd.stop()
            break
        time.sleep(0.1)
    
    print(f"Latency - {round((api_call_latency_end - api_call_latency_start) * 1000)} ms")
    return

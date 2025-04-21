import time
from groq import Groq
from inference import brain
from key_retriever import get_groq_key
from config import speech_synthesizer
match speech_synthesizer:
    case "elevenlabs":
        from synthesis_elevenlabs import synthesize_audio
    case "cartesia":
        from synthesis_cartesia import synthesize_audio
    case "groq":
        from synthesis_groq import synthesize_audio

def transcribe_audio(audio_bytes, stop_event):
    # Initialize the Groq client
    client = Groq(api_key = get_groq_key())

    # Ensures the pointer is at the beginning of the buffer
    audio_bytes.seek(0)

    # Generate the transcription of the audio
    api_call_latency_start = time.time()
    transcription = client.audio.transcriptions.create(
        file = audio_bytes,
        # Available models - "whisper-large-v3", "whisper-large-v3-turbo", "distil-whisper-large-v3-en"
        model = "distil-whisper-large-v3-en",
        prompt = "Generate transcription in English",
        response_format = "text",
        language = "en",
        temperature = 0.0
    )
    api_call_latency_end = time.time()

    # Print the Transcription
    user_input = transcription.strip()
    print()
    print(f"Human: {user_input}")
    print(f"Latency - {round((api_call_latency_end - api_call_latency_start) * 1000)} ms")
    print()

    # Generate Reponse
    response = brain(user_input)
    print(f"AI: {response}")
    print()

    # Generate Speech
    synthesize_audio(response, stop_event)
    return

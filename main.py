import time
import threading
import sounddevice as sd
from vad import process_audio, input_queue

# Initialize Threads
processing_thread = threading.Thread(target=process_audio, daemon=True)

# Audio Stream Callback
def callback(indata, outdata, frames, time, status):
    if status:
        print("Audio stream warning: ", status)
    input_queue.put(indata.copy())

# Start the Audio Stream
print("\nListening for audio input... Speak into the microphone!\n")
with sd.Stream(samplerate=16000, dtype="float32", channels=1, callback=callback, blocksize=512):
    processing_thread.start()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopped recording.")

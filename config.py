# -----------------------------
# Fine-Tuneable Parameters
# -----------------------------
voice_activity_threshold = 0.8 # Probabilities above this value is considered speech
min_silence_duration = 800     # In miliseconds, Speech get segmented if the silence duration is greater than this value
min_speech_duration = 400      # In miliseconds, audio captured under this length is dicarded
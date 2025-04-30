# Callia - Real Time Voice Assistant

[![Silero](https://img.shields.io/badge/Silero-black?style=plastic&logo=photon&logoColor=black&labelColor=fff7a1&color=black)](https://github.com/snakers4/silero-vad)
[![Whisper](https://img.shields.io/badge/Whisper-red?style=plastic&logo=openai&logoColor=black&labelColor=crimson&color=black)](https://huggingface.co/distil-whisper/distil-large-v3)
[![Gemma](https://img.shields.io/badge/Gemma-black?style=plastic&logo=google&logoColor=black&labelColor=ffd9d9&color=black)](https://huggingface.co/google/gemma-2-9b)
[![LangChain](https://img.shields.io/badge/LangChain-black?style=plastic&logo=langchain&logoColor=black&labelColor=63baaa&color=black)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-black?style=plastic&logo=langchain&logoColor=black&labelColor=50f036&color=black)](https://www.langchain.com/langgraph)

Callia is a modular real-time voice assistant that is attuned to your every word! It listens on the microphone, detects when you're speaking, transcribes your speech, and synthesizes a spoken response. The following is an illustration of the pipeline - 

<img src="https://imgur.com/VP9u7RD.png" />

## 🛠️ Installation

**Please proceed with the following steps:** 

1. &nbsp;**Clone the repository**
   
   ```sh
   git clone https://github.com/techstartucalgary/CalliaAI
   ```
   ```sh
   cd CalliaAI
   ```
2. &nbsp;**Create and activate a virtual environment (example using anaconda)**

   ```sh
   conda create -p venv python=3.10
   ```
   ```sh
   conda activate venv/
   ```
4. &nbsp;**Install Dependencies**

   ```sh
   pip install -r requirements.txt
   ```
5. &nbsp;**Install MPV**
   - Download and Install [MPV](https://mpv.io/)
   - Add the folder containing `mpv.exe` to your PATH environment variable.
   - MPV is required to play the stream output audio.
<br>

## 🔑 API Keys
Please insert your API keys in `key_retriever.py`

[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-black?style=flat-square&logo=elevenlabs&labelColor=black&color=gray)](https://elevenlabs.io/)
[![Groq](https://img.shields.io/badge/Groq-black?style=flat-square&logo=grocy&labelColor=black&color=cd393a)](https://groq.com/)

```python
def get_elevenlabs_key():
    # List of ElevenLabs Keys
    keys = []   <- Add your key as a list item
```
- At least one **GROQ** API Key is required!
<br>

## ▶️ Running Callia
Once you have installed everything perfectly, simply run - 
```python
python main.py
```
You can finally start taking to **Callia**! Once input is detected the pipeline will:
1. Transcribe your speech
2. Generate a spoken response
3. Play it back to you! Pretty neat huh?
<br>

## 📁 Project Structure
Here's what each file in this repository is for:
```sh
Callia/
├── main.py                      # Entry point
├── config.py                    # Configuration
├── vad.py                       # Voice Activity Detection
├── vad_utils.py                 # VAD model utilities
├── vad_model.jit                # TorchScript compiled AI model
├── transcriber.py               # Speech-to-text handler
├── inference.py                 # Generates Text-to-Text Response
├── synthesis.py                 # TTS using ElevenLabs
├── key_retriever.py             # Your API key(s) retriever
├── requirements.txt             # Dependencies
├── .gitignore                   # Tells git what to ignore
└── README.md                    # You're reading this
```
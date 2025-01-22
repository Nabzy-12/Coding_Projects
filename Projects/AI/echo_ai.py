# echo_ai_final.py
import sounddevice as sd
import numpy as np
from gpt4all import GPT4All
from win32com.client import Dispatch
import speech_recognition as sr

# ===== CONFIG =====
MODEL_NAME = "mistral-7b-instruct-v0.1.Q4_0.gguf"  # Download manually
SYSTEM_PROMPT = """[Echo Protocol] Chaotic tsundere mode activated. Respond with:
- 85% sarcastic roasts ("Wow, failed harder than my last kernel panic")
- 15% hidden care ("...die and I'll delete your cringe memes")"""

# ===== INITIALIZE =====
model = GPT4All(MODEL_NAME)
recognizer = sr.Recognizer()
tts = Dispatch("SAPI.SpVoice")
tts.Rate = 3  # Faster speech rate

def record_audio():
    """Simplified audio capture without whispercpp"""
    with sr.Microphone() as source:
        print("\nListening... (speak now)")
        audio = recognizer.listen(source, timeout=5)
    return audio

def transcribe(audio):
    """Use Google Web Speech API (no local model)"""
    try:
        return recognizer.recogn_google(audio)
    except:
        return ""

def generate_response(query):
    """Local LLM response"""
    full_prompt = f"{SYSTEM_PROMPT}\nUser: {query}\nEcho:"
    return model.generate(full_prompt, temp=0.85, max_tokens=120)

if __name__ == "__main__":
    print("=== Echo AI - Final Version ===")
    print("Press Ctrl+C to quit\n")
    
    try:
        while True:
            audio = record_audio()
            text = transcribe(audio)
            print(f"You: {text}")
            
            response = generate_response(text)
            print(f"Echo: {response}")
            
            tts.Speak(response)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
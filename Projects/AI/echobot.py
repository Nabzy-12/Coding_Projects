import customtkinter as ctk
from whispercpp import Whisper
from piper import PiperTTS
import sounddevice as sd
import numpy as np

class EchoUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Configure modern UI
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("Echo v0.1")
        self.geometry("800x600")
        
        # GUI Elements
        self.chat_frame = ctk.CTkTextbox(self, wrap="word", font=("Segoe UI", 14))
        self.input_entry = ctk.CTkEntry(self, placeholder_text="Speak or type...")
        self.voice_button = ctk.CTkButton(self, text="🎤", command=self.voice_input)
        
        # Layout
        self.chat_frame.pack(expand=True, fill="both")
        self.input_entry.pack(side="left", fill="x", expand=True)
        self.voice_button.pack(side="right")
        
        # AI Components
        self.stt = Whisper("tiny.en")
        self.tts = PiperTTS(voice="neuro-style", config_path="./voices/")
        self.model = LlamaCpp(model_path="mistral-7b-instruct-q4.gguf", n_gpu_layers=33)
        
    def voice_input(self):
        # Audio capture & STT
        print("Listening...")
        audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1)
        sd.wait()
        text = self.stt.transcribe(np.squeeze(audio))
        self.process_input(text)
        
    def process_input(self, text):
        # Generate response
        prompt = f"[INST] {text} [/INST]"
        response = self.model(prompt, max_tokens=150, temperature=0.7)
        
        # Display & speak
        self.chat_frame.insert("end", f"\nYou: {text}\nEcho: {response}")
        audio = self.tts.synthesize(response)
        sd.play(audio, samplerate=22050)
        
if __name__ == "__main__":
    app = EchoUI()
    app.mainloop()
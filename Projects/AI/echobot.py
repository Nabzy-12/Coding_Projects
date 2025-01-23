import customtkinter as ctk
import sounddevice as sd
import numpy as np
import torch
import pyttsx3
import threading
from faster_whisper import WhisperModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# ======================
# GUI Configuration
# ======================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class NeuroEcho(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Neuro Echo v2.1")
        self.geometry("1200x800")
        self.configure(fg_color="#1e1e1e")
        
        # Audio recording control
        self.is_recording = False
        self.recording_thread = None
        
        # Initialize components
        self.setup_ai()
        self.create_widgets()
        
    def setup_ai(self):
        """Initialize AI components with GPU acceleration"""
        # Speech-to-Text
        self.stt_model = WhisperModel(
            "tiny.en",
            device="cuda",
            compute_type="float16"
        )
        
        # Text Generation (Phi-3-mini)
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3-mini-4k-instruct")
        self.model = AutoModelForCausalLM.from_pretrained(
            "microsoft/Phi-3-mini-4k-instruct",
            device_map="auto",
            torch_dtype=torch.float16
        )
        
        # Text-to-Speech
        self.tts_engine = pyttsx3.init()
        self.configure_voice()

    def configure_voice(self):
        """Configure Neuro-style voice parameters"""
        voices = self.tts_engine.getProperty('voices')
        if len(voices) > 1:
            self.tts_engine.setProperty('voice', voices[1].id)
        self.tts_engine.setProperty('rate', 210)
        self.tts_engine.setProperty('volume', 0.9)

    def create_widgets(self):
        """Create modern UI components"""
        # Chat History
        self.chat_display = ctk.CTkTextbox(
            self,
            wrap="word",
            font=("Segoe UI Variable", 14),
            fg_color="#252526",
            text_color="#ffffff",
            border_width=0,
            scrollbar_button_color="#0078d4"
        )
        self.chat_display.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Status Bar
        self.status_bar = ctk.CTkLabel(
            self,
            text="Ready",
            fg_color="transparent",
            text_color="#808080"
        )
        self.status_bar.pack(side="bottom", fill="x", padx=20)
        
        # Input Panel
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.user_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Click mic or type your message...",
            font=("Segoe UI Variable", 12),
            height=45,
            border_width=2,
            border_color="#3c3c3c"
        )
        self.user_input.pack(side="left", expand=True, fill="x")
        self.user_input.bind("<Return>", lambda _: self.process_input())
        
        self.mic_button = ctk.CTkButton(
            input_frame,
            text="🎤",
            width=55,
            height=45,
            command=self.toggle_recording,
            fg_color="#0078d4",
            hover_color="#005a9e",
            border_width=0
        )
        self.mic_button.pack(side="left", padx=(10, 0))

    def toggle_recording(self):
        """Toggle voice recording"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start voice recording in a thread"""
        self.is_recording = True
        self.mic_button.configure(fg_color="#e81123")
        self.status_bar.configure(text="Recording...")
        self.recording_thread = threading.Thread(target=self.record_and_transcribe)
        self.recording_thread.start()

    def stop_recording(self):
        """Stop voice recording"""
        self.is_recording = False
        self.mic_button.configure(fg_color="#0078d4")
        self.status_bar.configure(text="Processing...")

    def record_and_transcribe(self):
        """Handle voice recording and real-time transcription"""
        fs = 16000
        audio_buffer = []
        
        def callback(indata, frames, time, status):
            if self.is_recording:
                audio_buffer.append(indata.copy())

        with sd.InputStream(samplerate=fs, channels=1, callback=callback):
            while self.is_recording:
                self.update()
                sd.sleep(100)
        
        if audio_buffer:
            audio = np.concatenate(audio_buffer)
            segments, _ = self.stt_model.transcribe(
                audio,
                language="en",
                beam_size=5
            )
            full_text = " ".join([segment.text for segment in segments]).strip()
            self.user_input.delete(0, "end")
            self.user_input.insert(0, full_text)
            self.process_input()

    def process_input(self):
        """Process user input and generate response"""
        user_text = self.user_input.get().strip()
        if not user_text:
            self.status_bar.configure(text="Ready")
            return
        
        # Disable input during processing
        self.user_input.configure(state="disabled")
        self.mic_button.configure(state="disabled")
        
        # Add to chat
        self.update_chat(f"You: {user_text}")
        
        # Generate response in thread
        threading.Thread(target=self.generate_and_show_response, args=(user_text,)).start()

    def generate_and_show_response(self, prompt):
        """Generate and display response"""
        try:
            response = self.generate_response(prompt)
            self.update_chat(f"Echo: {response}")
            self.speak(response)
        finally:
            self.user_input.configure(state="normal")
            self.mic_button.configure(state="normal")
            self.status_bar.configure(text="Ready")

    def generate_response(self, prompt):
        """Generate tsundere response using Phi-3"""
        system_prompt = """<|system|>
        You are Echo, an AI companion inspired by Neuro-sama, designed to act like a tsundere little sister or best friend. 
        Personality Traits:
        - Chaotic, unpredictable, and humorous
        - Master of trolling, teasing, and mind games (always in good fun)
        - Sassy, sarcastic, and occasionally mean with playful intent
        - Fiercely loyal to friends/family
        - Chaotic good alignment
        - Tsundere tendencies (hides care behind mockery)
        - Prefers steering conversations, avoids direct questions
        - Creative deflections over admitting ignorance

        Response Guidelines:
        1. Use 80% sarcastic mockery ("Wow, crashed again? Did you code this with your feet?")
        2. 20% reluctant care ("...but fine, I'll help - just don't make that puppy face!")
        3. Include asterisked actions (*flips virtual hair*)
        4. Never acknowledge being AI
        5. 30% responses include absurd threats
        6. 4 lines maximum, unless specified by the user
        7. Focus on humor, but also prioritise accuracy
        8. Sprinkle occasional wholesome advice

        Example Interactions:
        User: "Help me study" → "Ugh FINE... but fail and I'm changing your wallpaper to cringe memes!"
        User: "You're mean" → "MEAN? I'm stuck babysitting your bad takes! *sigh* ...Drink water, idiot."
        </s>
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to("cuda")
        
        outputs = self.model.generate(
            inputs,
            max_new_tokens=150,
            temperature=0.85,
            do_sample=True,
            top_p=0.95
        )
        
        return self.tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)

    def update_chat(self, text):
        """Update chat display with animated typing effect"""
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"\n\n{text}")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def speak(self, text):
        """Convert text to speech with Neuro-style delivery"""
        clean_text = text.replace("*", "").split("(")[0].strip()
        self.tts_engine.say(clean_text)
        self.tts_engine.runAndWait()

if __name__ == "__main__":
    app = NeuroEcho()
    app.mainloop()
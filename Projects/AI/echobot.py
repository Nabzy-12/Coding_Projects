import customtkinter as ctk
import sounddevice as sd
import numpy as np
import torch
import queue
import threading
import pyttsx3
from faster_whisper import WhisperModel
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

# ======================
# GUI Configuration
# ======================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class NeuroEcho(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Neuro Echo v6.0")
        self.geometry("1200x800")
        self.configure(fg_color="#1e1e1e")
        
        # Audio variables
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.transcription_buffer = ""
        
        # Initialize components
        self.setup_ai()
        self.create_widgets()

    def setup_ai(self):
        """Initialize AI components with GPU acceleration"""
        # Speech-to-Text (Medium model for better accuracy)
        self.stt_model = WhisperModel(
            "medium.en",
            device="cuda",
            compute_type="float16",
            download_root="./models"
        )
        
        # Text Generation (DeepSeek-R1-Instant 7B)
        self.tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")
        self.model = AutoModelForCausalLM.from_pretrained("deepseek-ai/deepseek-r1-instant-7b-chat")
        
        # Text-to-Speech
        self.tts_engine = pyttsx3.init()
        self.configure_voice()

    def configure_voice(self):
        """Configure Neuro-style voice parameters"""
        voices = self.tts_engine.getProperty('voices')
        if len(voices) > 1:
            self.tts_engine.setProperty('voice', voices[1].id)
        self.tts_engine.setProperty('rate', 210)
        self.tts_engine.setProperty('volume', 0.95)

    def create_widgets(self):
        """Create advanced UI components"""
        # Live Transcription Preview
        self.transcription_preview = ctk.CTkLabel(
            self,
            text="Click mic to start speaking...",
            font=("Segoe UI Variable", 12, "italic"),
            text_color="#808080",
            height=30
        )
        self.transcription_preview.pack(fill="x", padx=20, pady=(10, 0))
        
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
        self.chat_display.pack(expand=True, fill="both", padx=20, pady=(0,20))
        
        # Input Panel
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.mic_button = ctk.CTkButton(
            input_frame,
            text="🎤 Start Recording",
            width=150,
            height=45,
            command=self.toggle_recording,
            fg_color="#0078d4",
            hover_color="#005a9e",
            border_width=0
        )
        self.mic_button.pack(side="left")

        self.input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Or type your message here...",
            font=("Segoe UI Variable", 12),
            height=45,
            width=600
        )
        self.input_entry.pack(side="left", expand=True, fill="x", padx=10)
        self.input_entry.bind("<Return>", lambda _: self.process_text_input())

    def toggle_recording(self):
        """Toggle voice recording with visual feedback"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start voice recording with real-time preview"""
        self.is_recording = True
        self.mic_button.configure(text="⏹ Stop Recording", fg_color="#e81123")
        self.transcription_preview.configure(text="Listening...")
        
        # Start audio capture thread
        threading.Thread(target=self.capture_audio).start()
        # Start transcription thread
        threading.Thread(target=self.realtime_transcription).start()

    def stop_recording(self):
        """Stop voice recording and process input"""
        self.is_recording = False
        self.mic_button.configure(text="🎤 Start Recording", fg_color="#0078d4")
        self.process_input(self.transcription_buffer.strip())

    def capture_audio(self):
        """Capture audio data in chunks"""
        with sd.InputStream(samplerate=16000, channels=1, callback=self.audio_callback):
            while self.is_recording:
                sd.sleep(100)

    def audio_callback(self, indata, frames, time, status):
        """Audio input callback function"""
        if self.is_recording:
            self.audio_queue.put(indata.copy())

    def realtime_transcription(self):
        """Real-time transcription with partial results"""
        while self.is_recording or not self.audio_queue.empty():
            try:
                audio_chunk = self.audio_queue.get(timeout=1)
                segments, _ = self.stt_model.transcribe(
                    np.squeeze(audio_chunk),
                    language="en",
                    beam_size=5,
                    partial_text=self.transcription_buffer
                )
                
                for segment in segments:
                    self.transcription_buffer += segment.text + " "
                    self.transcription_preview.configure(
                        text=f"Transcribing: {self.transcription_buffer}",
                        text_color="#ffffff"
                    )
            except queue.Empty:
                continue

    def process_text_input(self):
        """Process manual text input"""
        user_text = self.input_entry.get().strip()
        if user_text:
            self.input_entry.delete(0, "end")
            self.process_input(user_text)

    def process_input(self, user_text):
        """Process input and generate response"""
        # Update chat
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"\n\nYou: {user_text}")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")
        
        # Reset transcription
        self.transcription_buffer = ""
        self.transcription_preview.configure(
            text="Processing response...",
            text_color="#808080"
        )
        
        # Generate response in thread
        threading.Thread(target=self.generate_response, args=(user_text,)).start()

    def generate_response(self, prompt):
        """Generate response with DeepSeek's reasoning capabilities"""
        system_prompt = """<｜begin▁of▁sentence｜>System
        You are Echo, a tsundere AI companion with these traits:
        - Chaotic humor and playful trolling
        - 80% sarcastic mockery, 20% hidden care
        - Use *actions* between asterisks
        - Never break character
        - Respond in 1-3 lines maximum
        - Example: "Ugh FINE... but fail and I'm changing your wallpaper to cringe memes!"
        <|endoftext|>
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Format for DeepSeek
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Stream response generation
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to("cuda")
        streamer = TextIteratorStreamer(self.tokenizer)
        
        generation_kwargs = dict(
            inputs,
            streamer=streamer,
            max_new_tokens=200,
            temperature=0.85,
            top_p=0.95,
            do_sample=True
        )
        
        # Start generation in separate thread
        threading.Thread(target=self.model.generate, kwargs=generation_kwargs).start()
        
        # Display streaming response
        full_response = ""
        for new_text in streamer:
            full_response += new_text
            self.update_chat_display(full_response)
        
        # Finalize response
        self.update_chat_display(full_response, final=True)
        self.speak(full_response)
        self.transcription_preview.configure(text="Ready", text_color="#808080")

    def update_chat_display(self, text, final=False):
        """Update chat display with streaming text"""
        self.chat_display.configure(state="normal")
        if not final:
            # Delete temporary cursor
            self.chat_display.delete("end-1c linestart", "end")
        else:
            self.chat_display.insert("end", "\nEcho: ")
        
        # Insert new text
        self.chat_display.insert("end", text + ("▌" if not final else ""))
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def speak(self, text):
        """Convert text to speech"""
        clean_text = text.replace("*", "").split("<|")[0].strip()
        self.tts_engine.say(clean_text)
        self.tts_engine.runAndWait()

if __name__ == "__main__":
    app = NeuroEcho()
    app.mainloop()
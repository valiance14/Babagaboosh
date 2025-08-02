import time
import whisper
import keyboard
import os
import tempfile
import numpy as np
import sounddevice as sd
import soundfile as sf
import threading
from typing import Optional

class SpeechToTextManager:
    """
    Free speech-to-text manager using OpenAI Whisper.
    Replaces Azure Cognitive Services to eliminate API costs.
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper model.
        
        Args:
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
                       'base' provides good balance of speed and accuracy
        """
        print(f"Loading Whisper model ({model_size})...")
        self.model = whisper.load_model(model_size)
        print("Whisper model loaded successfully!")
        
        # Audio recording settings
        self.sample_rate = 16000  # Whisper expects 16kHz
        self.channels = 1  # Mono audio
        self.dtype = np.float32
        
        # Continuous recording state
        self.is_recording = False
        self.audio_data = []
        self.recording_thread = None

    def speechtotext_from_mic(self) -> str:
        """
        Record audio from microphone and convert to text.
        Single recording session.
        
        Returns:
            str: Transcribed text
        """
        print("Speak into your microphone.")
        
        try:
            # Record audio for 5 seconds
            duration = 5  # seconds
            print(f"Recording for {duration} seconds...")
            
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype
            )
            sd.wait()  # Wait until recording is finished
            
            print("Processing audio...")
            
            # Convert to format expected by Whisper
            audio_np = audio_data.flatten()
            
            # Transcribe with Whisper
            result = self.model.transcribe(audio_np)
            text_result = result["text"].strip()
            
            if text_result:
                print(f"Recognized: {text_result}")
            else:
                print("No speech could be recognized")
            
            print(f"We got the following text: {text_result}")
            return text_result
            
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return ""

    def speechtotext_from_file(self, filename: str) -> str:
        """
        Convert audio file to text.
        
        Args:
            filename: Path to audio file
            
        Returns:
            str: Transcribed text
        """
        print(f"Listening to the file {filename}")
        
        try:
            # Load audio file
            if not os.path.exists(filename):
                print(f"Error: File {filename} not found")
                return ""
            
            # Transcribe with Whisper
            result = self.model.transcribe(filename)
            text_result = result["text"].strip()
            
            if text_result:
                print(f"Recognized: \n {text_result}")
            else:
                print("No speech could be recognized")
            
            return text_result
            
        except Exception as e:
            print(f"Error processing file: {e}")
            return ""

    def speechtotext_from_file_continuous(self, filename: str) -> str:
        """
        Convert long audio file to text with continuous processing.
        
        Args:
            filename: Path to audio file
            
        Returns:
            str: Complete transcribed text
        """
        print(f"Now processing the audio file: {filename}")
        
        try:
            if not os.path.exists(filename):
                print(f"Error: File {filename} not found")
                return ""
            
            # Transcribe with Whisper (it handles long files automatically)
            result = self.model.transcribe(filename)
            text_result = result["text"].strip()
            
            print(f"\n\nHeres the result we got from continuous file read!\n\n{text_result}\n\n")
            return text_result
            
        except Exception as e:
            print(f"Error processing file continuously: {e}")
            return ""

    def speechtotext_from_mic_continuous(self, stop_key: str = 'p') -> str:
        """
        Continuous speech recognition from microphone.
        Records until stop key is pressed.
        
        Args:
            stop_key: Key to press to stop recording (default: 'p')
            
        Returns:
            str: Complete transcribed text
        """
        print(f'Continuous Speech Recognition is now running, say something.')
        print(f"Press '{stop_key}' to stop recording.")
        
        try:
            self.is_recording = True
            self.audio_data = []
            
            # Start recording in a separate thread
            self.recording_thread = threading.Thread(target=self._continuous_recording)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            # Wait for stop key
            while self.is_recording:
                try:
                    if keyboard.read_key() == stop_key:
                        print(f"\nStopping speech recognition")
                        self.is_recording = False
                        break
                except:
                    # Handle keyboard reading errors
                    time.sleep(0.1)
                    continue
            
            # Wait for recording thread to finish
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=2.0)
            
            # Process recorded audio
            if len(self.audio_data) > 0:
                print("Processing recorded audio...")
                
                # Combine all audio chunks
                combined_audio = np.concatenate(self.audio_data)
                
                # Transcribe with Whisper
                result = self.model.transcribe(combined_audio)
                final_result = result["text"].strip()
                
                print(f"\n\nHeres the result we got!\n\n{final_result}\n\n")
                return final_result
            else:
                print("No audio was recorded")
                return ""
                
        except Exception as e:
            print(f"Error in continuous speech recognition: {e}")
            self.is_recording = False
            return ""
    
    def _continuous_recording(self):
        """
        Internal method for continuous audio recording.
        Runs in a separate thread.
        """
        try:
            # Record audio in chunks
            chunk_duration = 0.5  # seconds
            chunk_samples = int(chunk_duration * self.sample_rate)
            
            while self.is_recording:
                # Record a small chunk
                chunk = sd.rec(
                    chunk_samples,
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    dtype=self.dtype
                )
                sd.wait()  # Wait for chunk to complete
                
                if self.is_recording:  # Check again in case we stopped during recording
                    self.audio_data.append(chunk.flatten())
                
        except Exception as e:
            print(f"Error in continuous recording: {e}")
            self.is_recording = False


# Tests
if __name__ == '__main__':
    
    TEST_FILE = "TestAudio_WAV.wav"  # Use test file in repo
    
    speechtotext_manager = SpeechToTextManager()

    # Test file-based recognition if test file exists
    if os.path.exists(TEST_FILE):
        print(f"\n=== Testing file recognition with {TEST_FILE} ===")
        result = speechtotext_manager.speechtotext_from_file(TEST_FILE)
        print(f"Result: {result}")
        
        print(f"\n=== Testing continuous file recognition with {TEST_FILE} ===")
        result = speechtotext_manager.speechtotext_from_file_continuous(TEST_FILE)
        print(f"Result: {result}")
    else:
        print(f"Test file {TEST_FILE} not found, skipping file tests")

    # Test microphone recognition (commented out for automated testing)
    # print(f"\n=== Testing microphone recognition ===")
    # result = speechtotext_manager.speechtotext_from_mic()
    # print(f"Result: {result}")
    
    # print(f"\n=== Testing continuous microphone recognition ===")
    # result = speechtotext_manager.speechtotext_from_mic_continuous()
    # print(f"Result: {result}")
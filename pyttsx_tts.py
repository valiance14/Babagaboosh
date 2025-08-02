import pyttsx3
import time
import os
import tempfile
import threading
import queue

class PyttsxManager:
    def __init__(self):
        self.engine = None
        self.voices = []
        self.voice_mapping = {}
        
        try:
            # Try to initialize pyttsx3 with different approaches
            self.engine = pyttsx3.init()
            print("✓ pyttsx3 engine initialized successfully")
            
            # Set basic properties first
            try:
                self.engine.setProperty('rate', 150)  # Speed of speech
                self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
                print("✓ Basic properties set")
            except Exception as e:
                print(f"Warning: Could not set basic properties: {e}")
            
            # Try to get available voices, but don't fail if this doesn't work
            try:
                self.voices = self.engine.getProperty('voices')
                if self.voices:
                    print(f"\n✓ Found {len(self.voices)} available voices:")
                    for i, voice in enumerate(self.voices):
                        print(f"  {i}: {voice.name if hasattr(voice, 'name') else 'Unknown'} ({voice.id})")
                else:
                    print("\n⚠ No voices detected, will use default")
            except Exception as e:
                print(f"Warning: Could not get voices list: {e}")
                self.voices = []
            
            # Create voice mapping but don't set default voice yet
            self.voice_mapping = self._create_voice_mapping()
            
        except Exception as e:
            print(f"Error initializing pyttsx3: {e}")
            print("⚠ TTS will not be available")
            self.engine = None

    def _create_voice_mapping(self):
        """Map ElevenLabs voice names to available system voices"""
        mapping = {}
        
        if not self.voices:
            return mapping
            
        # Create mapping of common ElevenLabs voice names to system voices
        voice_names = [voice.name.lower() if hasattr(voice, 'name') else str(voice.id).lower() for voice in self.voices]
        
        # Map ElevenLabs voice names to system voices (best effort)
        elevenlabs_voices = [
            "Doug VO Only", "Doug Melina", "Pointboat", "default"
        ]
        
        for el_voice in elevenlabs_voices:
            # For now, just map all to the first available voice
            # In a more sophisticated implementation, you could do voice matching
            if self.voices:
                mapping[el_voice] = self.voices[0].id
        
        return mapping

    def _set_voice(self, voice_name):
        """Set the voice based on the requested voice name"""
        if not self.engine:
            return
        
        try:
            # Try to use the mapped voice
            if voice_name in self.voice_mapping:
                self.engine.setProperty('voice', self.voice_mapping[voice_name])
                print(f"✓ Set voice to mapped voice for '{voice_name}'")
            else:
                # Don't try to set a voice if we couldn't get the voices list
                # Just use whatever default the engine has
                print(f"⚠ Using default voice (requested: {voice_name})")
        except Exception as e:
            print(f"Warning: Could not set voice {voice_name}: {e}")

    def text_to_audio(self, input_text, voice="default", save_as_wave=True, subdirectory=""):
        """Convert text to speech, then save it to file. Returns the file path"""
        if not self.engine:
            print("pyttsx3 engine not available")
            return None
        
        try:
            # Set the voice
            self._set_voice(voice)
            
            # Create filename similar to ElevenLabs implementation
            if save_as_wave:
                file_name = f"___Msg{str(hash(input_text))}.wav"
            else:
                file_name = f"___Msg{str(hash(input_text))}.mp3"
            
            tts_file = os.path.join(os.path.abspath(os.curdir), subdirectory, file_name)
            
            # Save to file
            self.engine.save_to_file(input_text, tts_file)
            self.engine.runAndWait()
            
            return tts_file
            
        except Exception as e:
            print(f"Error in text_to_audio: {e}")
            return None

    def text_to_audio_played(self, input_text, voice="default"):
        """Convert text to speech, then play it out loud"""
        if not self.engine:
            print("pyttsx3 engine not available")
            return
        
        try:
            # Set the voice
            self._set_voice(voice)
            
            # Speak the text
            self.engine.say(input_text)
            self.engine.runAndWait()
            
        except Exception as e:
            print(f"Error in text_to_audio_played: {e}")

    def text_to_audio_streamed(self, input_text, voice="default"):
        """Convert text to speech, then stream it out loud (simplified - just plays immediately)"""
        # pyttsx3 doesn't support true streaming like ElevenLabs
        # For now, we'll just play it immediately like text_to_audio_played
        self.text_to_audio_played(input_text, voice)


# Test the implementation
if __name__ == '__main__':
    print("Testing pyttsx3 TTS Manager...")
    
    try:
        tts_manager = PyttsxManager()
        
        # Test playing audio
        print("\nTesting text_to_audio_played...")
        tts_manager.text_to_audio_played("This is a test of the pyttsx3 text to speech system", "default")
        
        # Test saving audio
        print("\nTesting text_to_audio...")
        file_path = tts_manager.text_to_audio("This is a saved test audio file", "default")
        if file_path:
            print(f"Audio saved to: {file_path}")
        
        # Test streaming (which is just immediate playback)
        print("\nTesting text_to_audio_streamed...")
        tts_manager.text_to_audio_streamed("This is a streamed test", "default")
        
        print("\nAll tests completed!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
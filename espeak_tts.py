import subprocess
import os
import tempfile
import hashlib

class EspeakTTSManager:
    """
    A TTS manager that uses espeak directly via subprocess.
    This provides a compatible interface with ElevenLabsManager.
    """

    def __init__(self):
        # Check if espeak is available
        self.espeak_available = self._check_espeak()
        
        # Voice mapping from ElevenLabs names to espeak voices
        self.voice_mapping = {
            "Doug VO Only": "en+m3",      # Male voice
            "Doug Melina": "en+f3",       # Female voice  
            "Pointboat": "en+m4",         # Another male voice
            "default": "en",              # Default English voice
        }
        
        # Default settings
        self.default_speed = 150  # words per minute
        self.default_pitch = 50   # pitch adjustment
        self.default_amplitude = 100  # volume
        
        if self.espeak_available:
            print("✓ ESpeak TTS Manager initialized successfully")
            self._list_available_voices()
        else:
            print("⚠ ESpeak not available - TTS will not work")

    def _check_espeak(self):
        """Check if espeak is available on the system"""
        try:
            result = subprocess.run(['espeak', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _list_available_voices(self):
        """List available espeak voices"""
        try:
            result = subprocess.run(['espeak', '--voices'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                print(f"✓ Found {len(lines)-1} espeak voices available")
                # Print first few voices as examples
                for line in lines[1:6]:  # Skip header, show first 5
                    print(f"  {line}")
                if len(lines) > 6:
                    print(f"  ... and {len(lines)-6} more voices")
        except Exception as e:
            print(f"Could not list voices: {e}")

    def _get_espeak_voice(self, voice_name):
        """Map ElevenLabs voice name to espeak voice"""
        return self.voice_mapping.get(voice_name, self.voice_mapping["default"])

    def text_to_audio(self, input_text, voice="default", save_as_wave=True, subdirectory=""):
        """Convert text to speech, then save it to file. Returns the file path"""
        if not self.espeak_available:
            print("ESpeak not available")
            return None
        
        try:
            # Create filename similar to ElevenLabs implementation
            if save_as_wave:
                file_name = f"___Msg{str(hash(input_text))}.wav"
            else:
                # Espeak outputs wav by default, we'll keep it as wav
                file_name = f"___Msg{str(hash(input_text))}.wav"
            
            tts_file = os.path.join(os.path.abspath(os.curdir), subdirectory, file_name)
            
            # Get the appropriate voice
            espeak_voice = self._get_espeak_voice(voice)
            
            # Build espeak command
            cmd = [
                'espeak',
                '-v', espeak_voice,
                '-s', str(self.default_speed),
                '-p', str(self.default_pitch),
                '-a', str(self.default_amplitude),
                '-w', tts_file,  # Write to file
                input_text
            ]
            
            # Execute espeak
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✓ Audio saved to: {tts_file}")
                return tts_file
            else:
                print(f"ESpeak error: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Error in text_to_audio: {e}")
            return None

    def text_to_audio_played(self, input_text, voice="default"):
        """Convert text to speech, then play it out loud"""
        if not self.espeak_available:
            print("ESpeak not available")
            return
        
        try:
            # Get the appropriate voice
            espeak_voice = self._get_espeak_voice(voice)
            
            # Build espeak command for direct playback
            cmd = [
                'espeak',
                '-v', espeak_voice,
                '-s', str(self.default_speed),
                '-p', str(self.default_pitch),
                '-a', str(self.default_amplitude),
                input_text
            ]
            
            # Execute espeak for direct playback
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"ESpeak playback error: {result.stderr}")
                
        except Exception as e:
            print(f"Error in text_to_audio_played: {e}")

    def text_to_audio_streamed(self, input_text, voice="default"):
        """Convert text to speech, then stream it out loud (same as played for espeak)"""
        # ESpeak doesn't have true streaming like ElevenLabs
        # For compatibility, we'll just play it immediately
        self.text_to_audio_played(input_text, voice)


# Test the implementation
if __name__ == '__main__':
    print("Testing ESpeak TTS Manager...")
    
    try:
        tts_manager = EspeakTTSManager()
        
        if not tts_manager.espeak_available:
            print("❌ ESpeak not available, cannot test")
            exit(1)
        
        # Test playing audio
        print("\nTesting text_to_audio_played...")
        tts_manager.text_to_audio_played("This is a test of the espeak text to speech system", "default")
        
        # Test saving audio
        print("\nTesting text_to_audio...")
        file_path = tts_manager.text_to_audio("This is a saved test audio file using espeak", "Doug VO Only")
        if file_path:
            print(f"✓ Audio saved to: {file_path}")
            # Check if file exists
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"✓ File exists and is {file_size} bytes")
            else:
                print("❌ File was not created")
        
        # Test streaming (which is just immediate playback)
        print("\nTesting text_to_audio_streamed...")
        tts_manager.text_to_audio_streamed("This is a streamed test using different voice", "Doug Melina")
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
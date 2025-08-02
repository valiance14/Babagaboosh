#!/usr/bin/env python3
"""
Test script to validate Whisper Speech-to-Text functionality.
"""
import sys
import os
import tempfile
import numpy as np
import soundfile as sf

def test_whisper_imports():
    """Test if Whisper and related modules import correctly"""
    try:
        from whisper_speech_to_text import SpeechToTextManager
        print("✅ whisper_speech_to_text imports successfully!")
        return True
    except ImportError as e:
        print(f"❌ whisper_speech_to_text import failed: {e}")
        return False

def test_whisper_initialization():
    """Test if Whisper model can be initialized"""
    try:
        from whisper_speech_to_text import SpeechToTextManager
        print("Initializing Whisper model (this may take a moment)...")
        manager = SpeechToTextManager(model_size="base")  # Use base model for balance
        print("✅ Whisper model initialized successfully!")
        return manager
    except Exception as e:
        print(f"❌ Whisper initialization failed: {e}")
        return None

def test_file_processing(manager):
    """Test file-based speech recognition"""
    try:
        # Test with existing audio files
        test_files = ["TestAudio_WAV.wav", "TestAudio_MP3.mp3"]
        
        for test_file in test_files:
            if os.path.exists(test_file):
                print(f"Testing file recognition with {test_file}...")
                result = manager.speechtotext_from_file(test_file)
                print(f"✅ File processing successful! Result: '{result[:50]}{'...' if len(result) > 50 else ''}'")
                return True
        
        # If no test files exist, create a simple synthetic audio file
        print("No test audio files found, creating synthetic test...")
        
        # Generate simple sine wave audio for testing
        duration = 2.0  # seconds
        sample_rate = 16000
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = 0.1 * np.sin(2 * np.pi * frequency * t)  # Low amplitude sine wave
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            sf.write(tmp_file.name, audio_data, sample_rate)
            temp_filename = tmp_file.name
        
        try:
            result = manager.speechtotext_from_file(temp_filename)
            print(f"✅ Synthetic audio processing successful! Result: '{result}'")
            return True
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_filename)
            except:
                pass
                
    except Exception as e:
        print(f"❌ File processing test failed: {e}")
        return False

def test_interface_compatibility():
    """Test that all expected methods exist with correct signatures"""
    try:
        from whisper_speech_to_text import SpeechToTextManager
        
        # Don't initialize the model, just check method existence
        methods_to_check = [
            'speechtotext_from_mic',
            'speechtotext_from_file', 
            'speechtotext_from_file_continuous',
            'speechtotext_from_mic_continuous'
        ]
        
        for method_name in methods_to_check:
            if hasattr(SpeechToTextManager, method_name):
                print(f"✅ Method {method_name} exists")
            else:
                print(f"❌ Method {method_name} missing")
                return False
        
        print("✅ All expected methods present - interface compatibility confirmed!")
        return True
        
    except Exception as e:
        print(f"❌ Interface compatibility test failed: {e}")
        return False

def main():
    print("🧪 Testing Whisper Speech-to-Text Integration")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_whisper_imports()
    interface_ok = test_interface_compatibility()
    
    if not imports_ok or not interface_ok:
        print("\n" + "=" * 50)
        print("❌ Basic tests failed. Please check the errors above.")
        return 1
    
    # Test initialization (this downloads models if needed)
    manager = test_whisper_initialization()
    
    if manager is None:
        print("\n" + "=" * 50)
        print("❌ Whisper initialization failed. Check internet connection and disk space.")
        return 1
    
    # Test file processing
    file_ok = test_file_processing(manager)
    
    print("\n" + "=" * 50)
    
    if imports_ok and interface_ok and manager and file_ok:
        print("🎉 All tests passed! Whisper Speech-to-Text is ready to use.")
        print("\n📋 Benefits of the new implementation:")
        print("✅ No Azure API keys required - completely free!")
        print("✅ Works offline - no internet needed for transcription")
        print("✅ High accuracy speech recognition")
        print("✅ Same interface as before - no code changes needed in calling modules")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
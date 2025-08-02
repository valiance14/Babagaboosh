#!/bin/bash

# System Dependencies Installation Script for Babagaboosh
# This script installs the required system dependencies for the TTS functionality

echo "🎭 Babagaboosh System Dependencies Installation"
echo "=============================================="

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Linux detected - using apt package manager"
    
    echo "📦 Updating package lists..."
    sudo apt update
    
    echo "🗣️  Installing ESpeak TTS engine..."
    sudo apt install -y espeak espeak-data
    
    echo "🎵 Installing FFmpeg for audio processing..."
    sudo apt install -y ffmpeg
    
    echo "✅ All system dependencies installed successfully!"
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS detected - using homebrew"
    
    # Check if homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew not found. Please install homebrew first:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    echo "🗣️  Installing ESpeak TTS engine..."
    brew install espeak
    
    echo "🎵 Installing FFmpeg for audio processing..."
    brew install ffmpeg
    
    echo "✅ All system dependencies installed successfully!"
    
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "Windows detected"
    echo "⚠️  Manual installation required for Windows:"
    echo ""
    echo "🗣️  ESpeak TTS:"
    echo "   1. Download from: http://espeak.sourceforge.net/download.html"
    echo "   2. Install and add to PATH"
    echo ""
    echo "🎵 FFmpeg:"
    echo "   1. Download from: https://ffmpeg.org/download.html"
    echo "   2. Extract and add to PATH"
    echo ""
    echo "Alternative: Use Windows Subsystem for Linux (WSL) and run this script there"
    
else
    echo "⚠️  Unsupported operating system: $OSTYPE"
    echo "Please manually install:"
    echo "  - ESpeak TTS engine"
    echo "  - FFmpeg"
fi

echo ""
echo "🧪 Testing installations..."

# Test ESpeak
if command -v espeak &> /dev/null; then
    echo "✅ ESpeak is available"
    espeak --version
else
    echo "❌ ESpeak not found in PATH"
fi

# Test FFmpeg
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg is available"
    ffmpeg -version | head -1
else
    echo "❌ FFmpeg not found in PATH"
fi

echo ""
echo "📋 Next steps:"
echo "1. Install Python dependencies: pip install -r requirements.txt"
echo "2. Set up environment variables (use setup-discord-environment.sh)"
echo "3. Run the application: python discord_main.py or python chatgpt_character.py"
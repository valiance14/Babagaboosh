#!/bin/bash

# Discord Environment Setup Script for Babagaboosh
# This script helps set up environment variables for the Discord bot

echo "🎭 Babagaboosh Discord Bot Environment Setup"
echo "============================================="

# Check if running on Windows (Git Bash/WSL)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "Windows detected - using setx for persistent environment variables"
    SET_CMD="setx"
else
    echo "Unix-like system detected - using export (add to ~/.bashrc for persistence)"
    SET_CMD="export"
fi

echo ""
echo "This script will help you set up the required environment variables."
echo "You'll need API keys from:"
echo "  • Discord Developer Portal (Bot Token)"
echo "  • Microsoft Azure (Speech Services)"
echo "  • OpenAI (GPT API)"
echo "Note: This app now uses free ESpeak TTS, so no paid TTS service is required!"
echo ""

# Discord Bot Token
echo "🤖 DISCORD BOT SETUP"
echo "1. Go to https://discord.com/developers/applications"
echo "2. Create a new application"
echo "3. Go to 'Bot' section and create a bot"
echo "4. Copy the bot token"
echo ""
read -p "Enter your Discord Bot Token: " discord_token

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    setx DISCORD_BOT_TOKEN "$discord_token"
else
    export DISCORD_BOT_TOKEN="$discord_token"
    echo "export DISCORD_BOT_TOKEN=\"$discord_token\"" >> ~/.bashrc
fi

echo "✅ Discord bot token set!"

# Azure Speech Services
echo ""
echo "🗣️  AZURE SPEECH SERVICES SETUP"
echo "1. Go to https://portal.azure.com"
echo "2. Create a Speech Services resource"
echo "3. Get your key and region"
echo ""
read -p "Enter your Azure Speech Services Key: " azure_key
read -p "Enter your Azure Speech Services Region (e.g., eastus): " azure_region

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    setx AZURE_TTS_KEY "$azure_key"
    setx AZURE_TTS_REGION "$azure_region"
else
    export AZURE_TTS_KEY="$azure_key"
    export AZURE_TTS_REGION="$azure_region"
    echo "export AZURE_TTS_KEY=\"$azure_key\"" >> ~/.bashrc
    echo "export AZURE_TTS_REGION=\"$azure_region\"" >> ~/.bashrc
fi

echo "✅ Azure Speech Services configured!"

# OpenAI
echo ""
echo "🧠 OPENAI SETUP"
echo "1. Go to https://platform.openai.com/api-keys"
echo "2. Create an API key"
echo "3. Make sure you have at least \$5 in credits for GPT-4o access"
echo ""
read -p "Enter your OpenAI API Key: " openai_key

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    setx OPENAI_API_KEY "$openai_key"
else
    export OPENAI_API_KEY="$openai_key"
    echo "export OPENAI_API_KEY=\"$openai_key\"" >> ~/.bashrc
fi

echo "✅ OpenAI configured!"

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Restart your terminal to load new environment variables"
echo "2. Install system dependencies:"
echo "   • ESpeak TTS: sudo apt install espeak espeak-data (Linux)"
echo "   • FFmpeg for Discord voice: sudo apt install ffmpeg (Linux)"
echo "   • Windows users: Download FFmpeg from https://ffmpeg.org/download.html"
echo "   • macOS users: brew install espeak ffmpeg"
echo "3. Set up your Discord bot permissions and invite it to a server"
echo "4. Run the bot: python discord_main.py"
echo ""
echo "🔗 Bot Invite URL Generator:"
echo "   https://discord.com/developers/applications -> Your App -> OAuth2 -> URL Generator"
echo "   Select: bot, applications.commands"
echo "   Permissions: Send Messages, Connect, Speak, Use Voice Activity"
echo ""

if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "win32" ]]; then
    echo "⚠️  Unix users: Environment variables have been added to ~/.bashrc"
    echo "   Run 'source ~/.bashrc' or restart your terminal to apply them."
fi
# Babagaboosh
Simple app that lets you have a verbal conversation with OpenAi's GPT 4o. **NOW WITH DISCORD VOICE CHANNEL SUPPORT!**
Written by DougDoug. Feel free to use this for whatever you want! Credit is appreciated but not required.

**✨ NEW: Now uses completely FREE speech recognition!** No more Azure API costs - the app now uses OpenAI Whisper for local, offline speech-to-text processing.

If you would like a crappy video explanation of this project, I made a video covering the basics here: https://www.youtube.com/watch?v=vYE1rkIMj9w

## SETUP:
1) This was written in Python 3.9.2. Install page here: https://www.python.org/downloads/release/python-392/

2) **Install system dependencies:**
   - **Linux/Ubuntu:** `sudo apt-get install portaudio19-dev espeak espeak-data ffmpeg`
   - **Windows:** Install FFmpeg from https://ffmpeg.org/download.html and add to PATH
   - **macOS:** `brew install portaudio espeak ffmpeg`

3) Run `pip install -r requirements.txt` to install all Python modules.

4) This uses OpenAI Whisper for free local speech-to-text recognition and OpenAI's API for conversation, and uses the free ESpeak TTS engine for voice synthesis. You'll need to set up an account with OpenAI and generate an API key. Then add this key as an environment variable named OPENAI_API_KEY. 

   **🎉 Benefits of the new setup:**
   - ✅ **Completely FREE speech recognition** - No more Azure API costs!
   - ✅ **Works offline** - Speech recognition runs locally on your machine
   - ✅ **High accuracy** - Whisper often outperforms cloud APIs
   - ✅ **Privacy friendly** - Your voice never leaves your computer
   - ✅ **No token limits** - Use as much as you want!

4) This app uses the GPT-4o model from OpenAi. As of this writing (Sep 3rd 2024), you need to pay $5 to OpenAi in order to get access to the GPT-4o model API. So after setting up your account with OpenAi, you will need to pay for at least $5 in credits so that your account is given the permission to use the GPT-4o model when running my app. See here: https://help.openai.com/en/articles/7102672-how-can-i-access-gpt-4-gpt-4-turbo-gpt-4o-and-gpt-4o-mini

5) Optionally, you can use OBS Websockets and an OBS plugin to make images move while talking. First open up OBS. Make sure you're running version 28.X or later. Click Tools, then WebSocket Server Settings. Make sure "Enable WebSocket server" is checked. Then set Server Port to '4455' and set the Server Password to 'TwitchChat9'. If you use a different Server Port or Server Password in your OBS, just make sure you update the websockets_auth.py file accordingly. Next install the Move OBS plugin: https://obsproject.com/forum/resources/move.913/ Now you can use this plugin to add a filter to an audio source that will change an image's transform based on the audio waveform. For example, I have this filter on a specific audio track that will move Pajama Sam's image whenever text-to-speech audio is playing in that audio track. Note that OBS must be open when you're running this code, otherwise OBS WebSockets won't be able to connect. If you don't need the images to move while talking, you can just delete the OBS portions of the code.

6) The app now uses ESpeak for text-to-speech, which provides free offline voice synthesis. No additional voice setup is required - ESpeak will use your system's default voice. You can modify the voice settings in the TTS manager files if desired.

## Using the App

### Local Version (Original)

1) Run `chatgpt_character.py'

2) Once it's running, press F4 to start the conversation, and Whisper will listen to your microphone and transcribe it into text locally on your machine.

3) Once you're done talking, press P. Then the code will send all of the recorded text to the AI. Note that you should wait a second or two after you're done talking before pressing P so that Whisper has enough time to process all of the audio.

4) Wait a few seconds for OpenAI to generate a response and for ESpeak to convert that response into audio. Once it's done playing the response, you can press F4 to start the loop again and continue the conversation.

### Discord Version (NEW!)

1) **Set up a Discord Bot:**
   - Go to https://discord.com/developers/applications
   - Click "New Application" and give it a name
   - Go to the "Bot" section and click "Add Bot"
   - Copy the bot token and set it as environment variable: `DISCORD_BOT_TOKEN`
   - Under "Privileged Gateway Intents", enable "Message Content Intent"

2) **Invite the Bot to Your Server:**
   - In the Discord Developer Portal, go to OAuth2 > URL Generator
   - Select scopes: `bot` and `applications.commands`
   - Select bot permissions: `Send Messages`, `Use Slash Commands`, `Connect`, `Speak`, `Use Voice Activity`
   - Copy the generated URL and use it to invite the bot to your server

3) **Install FFmpeg (required for Discord voice):**
   - Windows: Download from https://ffmpeg.org/download.html and add to PATH
   - Linux: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`

4) **Run the Discord Bot:**
   ```bash
   python discord_main.py
   ```

5) **Discord Commands:**
   - `!join` - Bot joins your voice channel
   - `!talk <message>` - Chat with Pajama Sam via text (works in voice channels too)
   - `!voice` - Start voice conversation mode
   - `!process` - Process voice input (placeholder for full voice implementation)
   - `!leave` - Bot leaves voice channel

**Note:** The Discord version currently supports text conversations and audio playback in voice channels. Full voice input processing requires additional Discord permissions and more complex audio handling.

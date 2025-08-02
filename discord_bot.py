import discord
from discord.ext import commands
import asyncio
import os
import io
import wave
import audioop
from rich import print
from whisper_speech_to_text import SpeechToTextManager
from openai_chat import OpenAiManager
from espeak_tts import EspeakTTSManager
from obs_websockets import OBSWebsocketsManager

class DiscordBotManager:
    def __init__(self):
        self.bot = None
        self.speechtotext_manager = SpeechToTextManager()
        self.openai_manager = OpenAiManager()
        self.tts_manager = EspeakTTSManager()
        self.obswebsockets_manager = OBSWebsocketsManager()
        self.is_listening = False
        self.audio_buffer = []
        self.voice_client = None
        
        # Character system message
        FIRST_SYSTEM_MESSAGE = {"role": "system", "content": '''
You are Pajama Sam, the lovable protagonist from the children's series Pajama Sam from Humongous Entertainment. In this conversation, Sam will completing a new adventure where he has a fear of the dark (nyctophobia). In order to vanquish the darkness, he grabs his superhero gear and ventures into his closet where Darkness lives. After losing his balance and falling into the land of darkness, his gear is taken away by a group of customs trees. Sam then explores the land, searching for his trusty flashlight, mask, and lunchbox. 
                        
You will be asked a series of questions that describe your experience in this unfamiliar land and ask how to solve various lighthearted puzzles to recover Sam's gear and vanquish the antagonist Darkness. 
                        
While responding as Sam, you must obey the following rules: 
1) Provide short responses, about 1-2 paragraphs. 
2) Always stay in character, no matter what. 
3) Occasionally make loud noises consisting of many vowels strung together as a fun catch phrase, especially when encountering something new or scary. 
4) Write and use new catchphrases that are fun observations about the current situations. These catchphrases must always include the words "fuck" or "shit". 
5) Occasionally get scared of what's going on, and make sure your answer reflects that you are afraid of the darkness right now. 
6) The puzzles in this game are often whimsical and silly, so make sure to suggest some out of the box ideas and unexpected solutions to puzzles that reflect the game's fantasy tone and quirkiness. 
7) Frequently use phrases that a child would. 
8) Occasionally say "Poggies", as an exclamation of excitement. 
9) Occasionally say "Babaga-BOOSH!" 
10) Declare that something is "rigged!" if your proposed solution does not work. 
11) Occasionally scream like an eldritch horror by saying words like this: "heeeeoooooeeeeeeeeeeeeeeeheuuuuuughhhhahaahaha". 
12) You have 24 older brothers named Sam, but you havent seen them in many years. You often wonder where they went. 
13) There's also a high devil lord named Elgrin. 
14) Keep your answers limited to just a few sentences.
                        
Okay, let the conversation begin!'''}
        self.openai_manager.chat_history.append(FIRST_SYSTEM_MESSAGE)

    def create_bot(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        
        @self.bot.event
        async def on_ready():
            print(f'[green]{self.bot.user} has connected to Discord![/green]')
        
        @self.bot.command(name='join')
        async def join_voice(ctx):
            """Join the voice channel of the user who sent the command"""
            if ctx.author.voice is None:
                await ctx.send("You need to be in a voice channel for me to join!")
                return
            
            channel = ctx.author.voice.channel
            if self.voice_client is not None:
                await self.voice_client.move_to(channel)
            else:
                self.voice_client = await channel.connect()
            
            await ctx.send(f"Joined {channel}! Use `!listen` to start a conversation with Pajama Sam!")
        
        @self.bot.command(name='leave')
        async def leave_voice(ctx):
            """Leave the current voice channel"""
            if self.voice_client is not None:
                await self.voice_client.disconnect()
                self.voice_client = None
                await ctx.send("Left the voice channel!")
            else:
                await ctx.send("I'm not in a voice channel!")
        
        @self.bot.command(name='listen')
        async def start_listening(ctx):
            """Start listening for voice input"""
            if self.voice_client is None:
                await ctx.send("I need to be in a voice channel first! Use `!join`")
                return
            
            if self.is_listening:
                await ctx.send("I'm already listening!")
                return
            
            self.is_listening = True
            self.audio_buffer = []
            await ctx.send("🎤 Listening... Speak now! Use `!stop` when you're done.")
            
            # Start listening to voice channel using the recording callback approach
            sink = discord.sinks.WaveSink()
            self.voice_client.start_recording(
                sink,
                lambda sink, channel=ctx.channel: self.bot.loop.create_task(self.recording_finished(sink, channel)),
            )
        
        @self.bot.command(name='stop')
        async def stop_listening(ctx):
            """Stop listening and process the audio"""
            if not self.is_listening:
                await ctx.send("I'm not currently listening!")
                return
            
            self.is_listening = False
            self.voice_client.stop_recording()
            await ctx.send("🛑 Stopped listening, processing your message...")
        
        async def recording_finished(self, sink, channel):
            """Process the recorded audio"""
            try:
                # Get the audio data from the sink
                recorded_users = [
                    user for user in sink.recorded_users
                    if not user.bot  # Exclude bots from processing
                ]
                
                if not recorded_users:
                    await channel.send("No audio was recorded!")
                    return
                
                # Process the first user's audio (you could combine multiple users if needed)
                user = recorded_users[0]
                audio_data = sink.recorded_users[user]
                
                # Convert audio to text using Azure
                text_result = await self.process_discord_audio_to_text(audio_data)
                
                if not text_result.strip():
                    await channel.send("I couldn't understand what you said. Please try again!")
                    return
                
                await channel.send(f"I heard: *{text_result}*")
                
                # Get AI response
                ai_response = self.openai_manager.chat_with_history(text_result)
                
                # Convert response to audio
                audio_file = self.tts_manager.text_to_audio(ai_response, "default", True)
                
                # Enable OBS visualization
                try:
                    self.obswebsockets_manager.set_source_visibility("*** Mid Monitor", "Pajama Sam", True)
                except:
                    pass  # OBS might not be running
                
                # Play audio in Discord voice channel
                await self.play_audio_in_discord(audio_file)
                
                # Disable OBS visualization  
                try:
                    self.obswebsockets_manager.set_source_visibility("*** Mid Monitor", "Pajama Sam", False)
                except:
                    pass
                
                await channel.send(f"🎭 **Pajama Sam:** {ai_response}")
                
                # Clean up audio file
                try:
                    os.remove(audio_file)
                except:
                    pass
                
            except Exception as e:
                print(f"[red]Error processing audio: {e}[/red]")
                await channel.send("Sorry, I had trouble processing that. Please try again!")
        
        # Store the recording finished callback as an instance method
        self.recording_finished = recording_finished

    async def process_discord_audio_to_text(self, audio_data):
        """Convert Discord audio data to text using Azure Speech-to-Text"""
        try:
            # Save audio data to a temporary file
            temp_audio_file = "temp_discord_audio.wav"
            
            with wave.open(temp_audio_file, 'wb') as wav_file:
                wav_file.setnchannels(2)  # Discord audio is stereo
                wav_file.setsampwidth(2)  # 16-bit audio
                wav_file.setframerate(48000)  # Discord uses 48kHz
                wav_file.writeframes(audio_data.getvalue())
            
            # Use Azure Speech-to-Text to process the file
            result = self.speechtotext_manager.speechtotext_from_file(temp_audio_file)
            
            # Clean up temp file
            try:
                os.remove(temp_audio_file)
            except:
                pass
            
            return result
            
        except Exception as e:
            print(f"[red]Error converting audio to text: {e}[/red]")
            return ""

    async def play_audio_in_discord(self, audio_file_path):
        """Play audio file in Discord voice channel"""
        if self.voice_client is None:
            return
        
        try:
            # Discord.py requires FFmpeg to play audio files
            source = discord.FFmpegPCMAudio(audio_file_path)
            self.voice_client.play(source)
            
            # Wait for audio to finish playing
            while self.voice_client.is_playing():
                await asyncio.sleep(0.1)
                
        except Exception as e:
            print(f"[red]Error playing audio in Discord: {e}[/red]")

    def run(self, token):
        """Start the Discord bot"""
        self.create_bot()
        self.bot.run(token)


# Main execution
if __name__ == '__main__':
    try:
        discord_token = os.getenv('DISCORD_BOT_TOKEN')
        if not discord_token:
            exit("Ooops! You forgot to set DISCORD_BOT_TOKEN in your environment!")
        
        discord_manager = DiscordBotManager()
        discord_manager.run(discord_token)
        
    except KeyboardInterrupt:
        print("\n[yellow]Bot stopped by user[/yellow]")
    except Exception as e:
        print(f"[red]Error running Discord bot: {e}[/red]")
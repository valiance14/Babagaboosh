import discord
from discord.ext import commands
import asyncio
import os
import tempfile
import wave
from rich import print
from azure_speech_to_text import SpeechToTextManager
from openai_chat import OpenAiManager
from eleven_labs import ElevenLabsManager
from obs_websockets import OBSWebsocketsManager

ELEVENLABS_VOICE = "Pointboat"  # Replace this with the name of whatever voice you have created on Elevenlabs
BACKUP_FILE = "ChatHistoryBackup.txt"

class PajamaSamBot:
    def __init__(self):
        # Initialize managers
        self.elevenlabs_manager = ElevenLabsManager()
        self.obswebsockets_manager = OBSWebsocketsManager()
        self.speechtotext_manager = SpeechToTextManager()
        self.openai_manager = OpenAiManager()
        
        # Character setup
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
        
        # Discord bot setup
        self.is_recording = False
        
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        self.setup_commands()

    def setup_commands(self):
        @self.bot.event
        async def on_ready():
            print(f'[green]🎭 Pajama Sam bot is ready! {self.bot.user} has connected to Discord![/green]')
            print(f'[green]Invite the bot to a server and use the following commands:[/green]')
            print(f'[green]!join - Join your voice channel[/green]')
            print(f'[green]!talk <message> - Talk to Pajama Sam via text[/green]')
            print(f'[green]!voice - Start voice conversation[/green]')
            print(f'[green]!leave - Leave voice channel[/green]')

        @self.bot.command(name='join')
        async def join_voice(ctx):
            """Join the voice channel of the user who sent the command"""
            if ctx.author.voice is None:
                await ctx.send("🔊 You need to be in a voice channel for me to join!")
                return
            
            channel = ctx.author.voice.channel
            voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            
            if voice_client is not None:
                await voice_client.move_to(channel)
            else:
                voice_client = await channel.connect()
            
            await ctx.send(f"🎭 **Pajama Sam joined {channel}!** \nUse `!talk <message>` to chat with me or `!voice` for voice conversation!")

        @self.bot.command(name='leave')
        async def leave_voice(ctx):
            """Leave the current voice channel"""
            voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            
            if voice_client is not None:
                await voice_client.disconnect()
                await ctx.send("👋 Pajama Sam left the voice channel! Babaga-BOOSH!")
            else:
                await ctx.send("I'm not in a voice channel!")

        @self.bot.command(name='talk')
        async def talk_text(ctx, *, message):
            """Chat with Pajama Sam via text"""
            try:
                async with ctx.typing():
                    # Get AI response
                    ai_response = self.openai_manager.chat_with_history(message)
                    
                    # Write backup
                    with open(BACKUP_FILE, "w") as file:
                        file.write(str(self.openai_manager.chat_history))
                    
                    # Send text response
                    await ctx.send(f"🎭 **Pajama Sam:** {ai_response}")
                    
                    # If bot is in voice channel, also speak the response
                    voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
                    if voice_client is not None:
                        await self.speak_response(voice_client, ai_response)
                        
            except Exception as e:
                print(f"[red]Error in text chat: {e}[/red]")
                await ctx.send("Uh oh! Something went wrong... This is rigged!")

        @self.bot.command(name='voice')
        async def voice_conversation(ctx):
            """Start a voice conversation with Pajama Sam"""
            voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            
            if voice_client is None:
                await ctx.send("🔊 I need to be in a voice channel first! Use `!join`")
                return

            await ctx.send("""
🎤 **Voice conversation with Pajama Sam!**

**How to use:**
1. Just start talking in the voice channel!
2. When you're done speaking, type `!process` to get Sam's response
3. Use `!stop` to end the voice conversation

*Note: This bot uses simple voice activation. For best results, speak clearly and use `!process` when you finish talking.*

Ready to talk? Start speaking now! 🎭
            """)

        @self.bot.command(name='process')
        async def process_voice(ctx):
            """Process voice input and get Pajama Sam's response"""
            voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            
            if voice_client is None:
                await ctx.send("I'm not in a voice channel!")
                return

            try:
                async with ctx.typing():
                    await ctx.send("🎧 Processing your voice... (This is a simplified version - in a full implementation, this would capture and process your voice)")
                    
                    # For now, ask user to provide text input as a fallback
                    await ctx.send("⚠️ **Voice processing placeholder**: Please use `!talk <your message>` instead for now, or provide text input:")
                    
                    # In a full implementation, this would:
                    # 1. Capture audio from voice channel
                    # 2. Convert to text using Azure Speech-to-Text  
                    # 3. Process with OpenAI
                    # 4. Convert response to speech with ElevenLabs
                    # 5. Play in Discord voice channel
                    
            except Exception as e:
                print(f"[red]Error processing voice: {e}[/red]")
                await ctx.send("I couldn't process that! Try again or use `!talk` instead.")

    async def speak_response(self, voice_client, text):
        """Convert text to speech and play in Discord voice channel"""
        try:
            # Enable OBS visualization
            try:
                self.obswebsockets_manager.set_source_visibility("*** Mid Monitor", "Pajama Sam", True)
            except:
                pass  # OBS might not be running
            
            # Generate audio file
            audio_file = self.elevenlabs_manager.text_to_audio(text, ELEVENLABS_VOICE, True)
            
            # Play in Discord voice channel
            if voice_client and not voice_client.is_playing():
                source = discord.FFmpegPCMAudio(audio_file)
                voice_client.play(source)
                
                # Wait for audio to finish
                while voice_client.is_playing():
                    await asyncio.sleep(0.1)
            
            # Disable OBS visualization
            try:
                self.obswebsockets_manager.set_source_visibility("*** Mid Monitor", "Pajama Sam", False)
            except:
                pass
            
            # Clean up audio file
            try:
                os.remove(audio_file)
            except:
                pass
                
        except Exception as e:
            print(f"[red]Error speaking response: {e}[/red]")

    def run(self, token):
        """Start the Discord bot"""
        try:
            self.bot.run(token)
        except Exception as e:
            print(f"[red]Error running bot: {e}[/red]")


# Main execution
if __name__ == '__main__':
    try:
        # Check for required environment variables
        discord_token = os.getenv('DISCORD_BOT_TOKEN')
        if not discord_token:
            print("[red]❌ DISCORD_BOT_TOKEN environment variable not set![/red]")
            print("[yellow]Please set your Discord bot token as an environment variable:[/yellow]")
            print("[yellow]export DISCORD_BOT_TOKEN='your_bot_token_here'[/yellow]")
            exit(1)
        
        # Check other required API keys
        required_vars = ['AZURE_TTS_KEY', 'AZURE_TTS_REGION', 'ELEVENLABS_API_KEY', 'OPENAI_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"[red]❌ Missing required environment variables: {', '.join(missing_vars)}[/red]")
            print("[yellow]Please set all required API keys as environment variables.[/yellow]")
            exit(1)
        
        print("[green]🚀 Starting Pajama Sam Discord Bot...[/green]")
        
        bot = PajamaSamBot()
        bot.run(discord_token)
        
    except KeyboardInterrupt:
        print("\n[yellow]👋 Bot stopped by user[/yellow]")
    except Exception as e:
        print(f"[red]❌ Error running Discord bot: {e}[/red]")
#!/usr/bin/env python3
"""
Test script to validate Discord bot setup without requiring API keys.
"""
import sys
import os

def test_discord_imports():
    """Test if Discord.py imports correctly"""
    try:
        import discord
        from discord.ext import commands
        print("✅ discord.py imports successfully!")
        print(f"   Discord.py version: {discord.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Discord.py import failed: {e}")
        return False

def test_core_modules():
    """Test if core modules can be imported"""
    modules = ['rich', 'asyncio', 'os', 'tempfile', 'wave']
    success = True
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} imports successfully!")
        except ImportError as e:
            print(f"❌ {module} import failed: {e}")
            success = False
    
    return success

def test_bot_structure():
    """Test basic bot structure without initializing services"""
    try:
        # Test basic Discord bot structure
        import discord
        from discord.ext import commands
        
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        
        bot = commands.Bot(command_prefix='!', intents=intents)
        
        @bot.command(name='test')
        async def test_command(ctx):
            await ctx.send("Test command works!")
        
        print("✅ Discord bot structure is valid!")
        return True
        
    except Exception as e:
        print(f"❌ Bot structure test failed: {e}")
        return False

def main():
    print("🧪 Testing Discord Bot Setup")
    print("=" * 40)
    
    # Test imports
    discord_ok = test_discord_imports()
    core_ok = test_core_modules()
    structure_ok = test_bot_structure()
    
    print("\n" + "=" * 40)
    
    if discord_ok and core_ok and structure_ok:
        print("🎉 All tests passed! Discord bot is ready to run.")
        print("\n📋 Next steps:")
        print("1. Set up your Discord bot token: DISCORD_BOT_TOKEN")
        print("2. Set up API keys: AZURE_TTS_KEY, AZURE_TTS_REGION, ELEVENLABS_API_KEY, OPENAI_API_KEY")
        print("3. Install FFmpeg for voice support")
        print("4. Run: python discord_main.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
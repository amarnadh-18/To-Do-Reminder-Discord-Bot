#!/usr/bin/env python3
"""
Startup script for the To-Do Discord Bot
"""

import os
import sys
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 13):
        print("❌ Python 3.13 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("   Please copy env.example to .env and configure your settings.")
        return False
    
    # Check if DISCORD_TOKEN is set
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv('DISCORD_TOKEN'):
        print("❌ DISCORD_TOKEN not found in .env file!")
        print("   Please add your Discord bot token to the .env file.")
        return False
    
    print("✅ All requirements met!")
    return True

def main():
    """Main startup function"""
    print("🚀 Starting To-Do Discord Bot...")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n📖 Setup Instructions:")
        print("1. Copy env.example to .env")
        print("2. Add your Discord bot token to .env")
        print("3. Make sure MongoDB is running")
        print("4. Run: python start.py")
        sys.exit(1)
    
    # Import and run the bot
    try:
        print("📦 Importing bot modules...")
        from bot import main as bot_main
        import asyncio
        
        print("🎯 Starting bot...")
        asyncio.run(bot_main())
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed: uv sync")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
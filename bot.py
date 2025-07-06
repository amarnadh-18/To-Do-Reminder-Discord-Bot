import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
import asyncio

# Import our modules
from db.database import db
from scheduler.scheduler import reminder_scheduler
from scheduler.reminder_jobs import ReminderJobHandler

# Load environment variables
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord.log', encoding='UTF-8', mode='w'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Validate token
if not token:
    logger.error("❌ DISCORD_TOKEN not found in environment variables!")
    exit(1)

# Check database connection
if db is None:
    logger.error("❌ Database connection failed! Please check your MongoDB configuration.")
    exit(1)

# Set up bot intents - Safe configuration without privileged intents
intents = discord.Intents.default()
intents.message_content = True  # Required for reading message content
# intents.members = True  # Disabled to avoid privileged intents error

# Create bot instance
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Global reminder handler
reminder_handler = None

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    logger.info(f"✅ {bot.user} has connected to Discord!")
    logger.info(f"📊 Bot is in {len(bot.guilds)} guilds")
    
    # Initialize reminder handler
    global reminder_handler
    reminder_handler = ReminderJobHandler(bot)
    
    # Set up scheduler callback
    reminder_scheduler.set_reminder_callback(reminder_handler.handle_reminder_callback)
    
    # Start the scheduler
    try:
        reminder_scheduler.start()
        logger.info("✅ Reminder scheduler started!")
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}")
    
    # Start reminder processor
    await reminder_handler.start_reminder_processor()
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="your tasks | !help"
        )
    )

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found! Use `!help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: {error.param}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument provided.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏰ Command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
    else:
        logger.error(f"❌ Unhandled command error: {error}")
        await ctx.send("❌ An unexpected error occurred. Please try again.")

@bot.event
async def on_guild_join(guild):
    """Called when the bot joins a new guild"""
    logger.info(f"🎉 Joined guild: {guild.name} (ID: {guild.id})")
    
    # Try to send welcome message to system channel
    if guild.system_channel:
        embed = discord.Embed(
            title="🎉 Thanks for adding To-Do Bot!",
            description="I'm here to help you manage your tasks and reminders!",
            color=0x00ff00
        )
        embed.add_field(
            name="Getting Started",
            value="Use `!help` to see all available commands.\nUse `!add <task>` to create your first task!",
            inline=False
        )
        embed.add_field(
            name="Quick Commands",
            value="• `!add <title> [description]` - Add a task\n• `!list` - View your tasks\n• `!remind <task_id> <time>` - Set a reminder",
            inline=False
        )
        
        try:
            await guild.system_channel.send(embed=embed)
        except:
            logger.warning(f"Could not send welcome message to {guild.name}")

@bot.event
async def on_guild_remove(guild):
    """Called when the bot leaves a guild"""
    logger.info(f"👋 Left guild: {guild.name} (ID: {guild.id})")

async def load_extensions():
    """Load all bot extensions/cogs"""
    try:
        await bot.load_extension("cogs.tasks")
        logger.info("✅ Loaded tasks cog")
    except Exception as e:
        logger.error(f"❌ Failed to load tasks cog: {e}")

async def main():
    """Main function to run the bot"""
    try:
        # Load extensions
        await load_extensions()
        
        # Start the bot
        logger.info("🚀 Starting To-Do Bot...")
        await bot.start(token)  # type: ignore
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot interrupted by user")
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
    finally:
        # Cleanup
        if reminder_handler:
            await reminder_handler.stop_reminder_processor()
        
        reminder_scheduler.stop()
        db.close()
        logger.info("🧹 Cleanup completed")

# Run the bot if executed directly
if __name__ == "__main__":
    asyncio.run(main())



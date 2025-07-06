import asyncio
from datetime import datetime
from typing import Optional
import logging
from db.database import db
from db.models import TaskManager, Reminder
from utils.helpers import EmbedHelper
import discord

class ReminderJobHandler:
    """Handler for processing reminder jobs"""
    
    def __init__(self, bot):
        self.bot = bot
        if db is None:
            raise RuntimeError("Database connection is not available")
        self.task_manager = TaskManager(db)
        self.logger = logging.getLogger(__name__)
        self.is_running = False
    
    async def start_reminder_processor(self):
        """Start the background task to process reminders"""
        if self.is_running:
            return
        
        self.is_running = True
        self.logger.info("🔄 Starting reminder processor...")
        
        # Start the background task
        asyncio.create_task(self._process_reminders_loop())
    
    async def stop_reminder_processor(self):
        """Stop the reminder processor"""
        self.is_running = False
        self.logger.info("🛑 Stopping reminder processor...")
    
    async def _process_reminders_loop(self):
        """Main loop for processing reminders"""
        while self.is_running:
            try:
                await self._process_pending_reminders()
                # Wait for 30 seconds before checking again
                await asyncio.sleep(30)
            except Exception as e:
                self.logger.error(f"❌ Error in reminder processing loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _process_pending_reminders(self):
        """Process all pending reminders"""
        try:
            current_time = datetime.utcnow()
            pending_reminders = self.task_manager.get_pending_reminders(current_time)
            
            for reminder in pending_reminders:
                await self._send_reminder(reminder)
                
        except Exception as e:
            self.logger.error(f"❌ Error processing pending reminders: {e}")
    
    async def _send_reminder(self, reminder: Reminder):
        """Send a reminder to the user"""
        try:
            # Get the task details
            task = self.task_manager.get_task_by_id(reminder.task_id)
            if not task:
                self.logger.warning(f"⚠️ Task {reminder.task_id} not found for reminder {reminder._id}")
                return
            
            # Try to send the reminder to the user using fetch_user (works without members intent)
            try:
                user = await self.bot.fetch_user(reminder.user_id)
            except discord.NotFound:
                self.logger.warning(f"⚠️ User {reminder.user_id} not found for reminder")
                return
            except discord.HTTPException as e:
                self.logger.error(f"❌ HTTP error fetching user {reminder.user_id}: {e}")
                return
            
            # Create reminder embed
            embed = EmbedHelper.create_reminder_embed(task, reminder.message)
            
            # Send the reminder
            try:
                await user.send(embed=embed)
                self.logger.info(f"✅ Sent reminder {reminder._id} to user {reminder.user_id}")
            except discord.Forbidden:
                self.logger.warning(f"⚠️ Cannot send DM to user {reminder.user_id} - DMs may be disabled")
                return
            except Exception as e:
                self.logger.error(f"❌ Failed to send DM to user {reminder.user_id}: {e}")
                return
            
            # Mark reminder as sent
            self.task_manager.mark_reminder_sent(str(reminder._id))
            
        except Exception as e:
            self.logger.error(f"❌ Error sending reminder {reminder._id}: {e}")
    
    async def handle_reminder_callback(self, reminder_id: str, user_id: int, 
                                     task_id: str, message: str):
        """Callback function for scheduled reminders"""
        try:
            # Get the task details
            task = self.task_manager.get_task_by_id(task_id)
            if not task:
                self.logger.warning(f"⚠️ Task {task_id} not found for scheduled reminder")
                return
            
            # Try to send the reminder to the user using fetch_user (works without members intent)
            try:
                user = await self.bot.fetch_user(user_id)
            except discord.NotFound:
                self.logger.warning(f"⚠️ User {user_id} not found for scheduled reminder")
                return
            except discord.HTTPException as e:
                self.logger.error(f"❌ HTTP error fetching user {user_id}: {e}")
                return
            
            # Create reminder embed
            embed = EmbedHelper.create_reminder_embed(task, message)
            
            # Send the reminder
            try:
                await user.send(embed=embed)
                self.logger.info(f"✅ Sent scheduled reminder {reminder_id} to user {user_id}")
            except discord.Forbidden:
                self.logger.warning(f"⚠️ Cannot send DM to user {user_id} - DMs may be disabled")
                return
            except Exception as e:
                self.logger.error(f"❌ Failed to send DM to user {user_id}: {e}")
                return
            
            # Mark reminder as sent in database
            self.task_manager.mark_reminder_sent(reminder_id)
            
        except Exception as e:
            self.logger.error(f"❌ Error in reminder callback: {e}")
    
    def create_reminder(self, user_id: int, task_id: str, reminder_time: datetime, 
                       message: str = "") -> Optional[str]:
        """Create a new reminder"""
        try:
            # Create reminder in database
            reminder = Reminder(user_id, task_id, reminder_time, message)
            reminder_id = self.task_manager.create_reminder(reminder)
            
            # Add to scheduler
            from scheduler.scheduler import reminder_scheduler
            reminder_scheduler.add_reminder(
                reminder_id, reminder_time, user_id, task_id, message
            )
            
            self.logger.info(f"✅ Created reminder {reminder_id} for task {task_id}")
            return reminder_id
            
        except Exception as e:
            self.logger.error(f"❌ Error creating reminder: {e}")
            return None
    
    def delete_reminder(self, reminder_id: str) -> bool:
        """Delete a reminder"""
        try:
            # Remove from scheduler
            from scheduler.scheduler import reminder_scheduler
            reminder_scheduler.remove_reminder(reminder_id)
            
            # Remove from database
            # Note: We'll need to add a method to TaskManager for this
            # For now, we'll just mark it as sent
            self.task_manager.mark_reminder_sent(reminder_id)
            
            self.logger.info(f"🗑️ Deleted reminder {reminder_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error deleting reminder {reminder_id}: {e}")
            return False

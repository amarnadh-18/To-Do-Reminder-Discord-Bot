from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime
import asyncio
from typing import Optional, Callable
import logging

class ReminderScheduler:
    """Scheduler for handling task reminders"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.reminder_callback: Optional[Callable] = None
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """Start the scheduler"""
        try:
            self.scheduler.start()
            self.logger.info("✅ Reminder scheduler started successfully!")
        except Exception as e:
            self.logger.error(f"❌ Failed to start scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler"""
        try:
            if hasattr(self.scheduler, 'shutdown'):
                self.scheduler.shutdown()
                self.logger.info("🛑 Reminder scheduler stopped.")
            else:
                self.logger.info("🛑 Scheduler already stopped or not running.")
        except Exception as e:
            self.logger.error(f"❌ Error stopping scheduler: {e}")
    
    def set_reminder_callback(self, callback: Callable):
        """Set the callback function for when reminders are triggered"""
        self.reminder_callback = callback
    
    def add_reminder(self, reminder_id: str, reminder_time: datetime, 
                    user_id: int, task_id: str, message: str):
        """Add a new reminder to the scheduler"""
        try:
            job_id = f"reminder_{reminder_id}"
            
            # Create the job
            self.scheduler.add_job(
                func=self._trigger_reminder,
                trigger=DateTrigger(run_date=reminder_time),
                args=[reminder_id, user_id, task_id, message],
                id=job_id,
                replace_existing=True
            )
            
            self.logger.info(f"✅ Added reminder {reminder_id} for {reminder_time}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add reminder {reminder_id}: {e}")
            return False
    
    def remove_reminder(self, reminder_id: str):
        """Remove a reminder from the scheduler"""
        try:
            job_id = f"reminder_{reminder_id}"
            self.scheduler.remove_job(job_id)
            self.logger.info(f"🗑️ Removed reminder {reminder_id}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to remove reminder {reminder_id}: {e}")
            return False
    
    def update_reminder(self, reminder_id: str, new_time: datetime):
        """Update an existing reminder's time"""
        try:
            job_id = f"reminder_{reminder_id}"
            
            # Remove existing job and add new one
            self.scheduler.remove_job(job_id)
            
            # Get the existing job's args
            existing_job = self.scheduler.get_job(job_id)
            if existing_job:
                args = existing_job.args
                self.scheduler.add_job(
                    func=self._trigger_reminder,
                    trigger=DateTrigger(run_date=new_time),
                    args=args,
                    id=job_id
                )
                self.logger.info(f"✅ Updated reminder {reminder_id} to {new_time}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update reminder {reminder_id}: {e}")
            return False
    
    async def _trigger_reminder(self, reminder_id: str, user_id: int, 
                              task_id: str, message: str):
        """Internal method to trigger a reminder"""
        try:
            if self.reminder_callback:
                await self.reminder_callback(reminder_id, user_id, task_id, message)
            else:
                self.logger.warning("No reminder callback set!")
                
        except Exception as e:
            self.logger.error(f"❌ Error triggering reminder {reminder_id}: {e}")
    
    def get_job_count(self) -> int:
        """Get the number of scheduled jobs"""
        return len(self.scheduler.get_jobs())
    
    def get_jobs(self):
        """Get all scheduled jobs"""
        return self.scheduler.get_jobs()
    
    def clear_all_jobs(self):
        """Clear all scheduled jobs"""
        try:
            self.scheduler.remove_all_jobs()
            self.logger.info("🗑️ Cleared all scheduled reminders")
        except Exception as e:
            self.logger.error(f"❌ Error clearing jobs: {e}")

# Global scheduler instance
reminder_scheduler = ReminderScheduler()

import discord
from discord.ext import commands
from datetime import datetime
from typing import Optional
import logging
import re

from db.database import db
from db.models import Task, TaskManager
from utils.timeparser import TimeParser
from utils.helpers import EmbedHelper, ValidationHelper
from scheduler.reminder_jobs import ReminderJobHandler

class TaskCommands(commands.Cog):
    """Commands for managing tasks and reminders"""
    
    def __init__(self, bot):
        self.bot = bot
        if db is None:
            raise RuntimeError("Database connection is not available")
        self.task_manager = TaskManager(db)
        self.reminder_handler = ReminderJobHandler(bot)
        self.logger = logging.getLogger(__name__)
    
    @commands.command(name="add", help="Add a new task")
    async def add_task(self, ctx, title: str, *, description: str = ""):
        """Add a new task"""
        try:
            # Sanitize inputs
            title = ValidationHelper.sanitize_input(title, 100)
            description = ValidationHelper.sanitize_input(description, 500)
            
            if not title:
                await ctx.send("❌ Task title cannot be empty!")
                return
            
            # Create the task
            task = Task(
                user_id=ctx.author.id,
                title=title,
                description=description
            )
            
            task_id = self.task_manager.create_task(task)
            if not task_id:
                await ctx.send("❌ Failed to create task in database!")
                return
            
            # Create embed response
            embed = EmbedHelper.create_task_embed(task, "✅ Task Created!")
            embed.add_field(name="Task ID", value=task_id, inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"❌ Error adding task: {e}")
            await ctx.send("❌ Failed to create task. Please try again.")
    
    @commands.command(name="list", help="List your tasks")
    async def list_tasks(self, ctx, filter_type: str = "pending"):
        """List tasks for the user"""
        try:
            # Determine filter
            if filter_type.lower() in ["completed", "done", "finished"]:
                tasks = self.task_manager.get_user_tasks(ctx.author.id, completed=True)
                title = "✅ Completed Tasks"
            elif filter_type.lower() in ["all", "everything"]:
                tasks = self.task_manager.get_user_tasks(ctx.author.id)
                title = "📋 All Tasks"
            else:
                tasks = self.task_manager.get_user_tasks(ctx.author.id, completed=False)
                title = "⏳ Pending Tasks"
            
            # Create embed
            embed = EmbedHelper.create_task_list_embed(tasks, title)
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"❌ Error listing tasks: {e}")
            await ctx.send("❌ Failed to list tasks. Please try again.")
    
    @commands.command(name="view", help="View details of a specific task")
    async def view_task(self, ctx, task_id: str):
        """View a specific task"""
        try:
            # Validate task ID
            if not ValidationHelper.validate_task_id(task_id):
                await ctx.send("❌ Invalid task ID format!")
                return
            
            # Get the task
            task = self.task_manager.get_task_by_id(task_id)
            if not task:
                await ctx.send("❌ Task not found!")
                return
            
            # Check if user owns the task
            if task.user_id != ctx.author.id:
                await ctx.send("❌ You can only view your own tasks!")
                return
            
            # Create embed
            embed = EmbedHelper.create_task_embed(task)
            embed.add_field(name="Task ID", value=task_id, inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"❌ Error viewing task: {e}")
            await ctx.send("❌ Failed to view task. Please try again.")
    
    @commands.command(name="complete", help="Mark a task as completed")
    async def complete_task(self, ctx, task_id: str):
        """Mark a task as completed"""
        try:
            # Validate task ID
            if not ValidationHelper.validate_task_id(task_id):
                await ctx.send("❌ Invalid task ID format!")
                return
            
            # Get the task
            task = self.task_manager.get_task_by_id(task_id)
            if not task:
                await ctx.send("❌ Task not found!")
                return
            
            # Check if user owns the task
            if task.user_id != ctx.author.id:
                await ctx.send("❌ You can only complete your own tasks!")
                return
            
            # Check if already completed
            if task.completed:
                await ctx.send("✅ Task is already completed!")
                return
            
            # Update the task
            success = self.task_manager.update_task(task_id, {"completed": True})
            if success:
                task.completed = True
                embed = EmbedHelper.create_task_embed(task, "✅ Task Completed!")
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Failed to complete task. Please try again.")
            
        except Exception as e:
            self.logger.error(f"❌ Error completing task: {e}")
            await ctx.send("❌ Failed to complete task. Please try again.")
    
    @commands.command(name="delete", help="Delete a task")
    async def delete_task(self, ctx, task_id: str):
        """Delete a task"""
        try:
            # Validate task ID
            if not ValidationHelper.validate_task_id(task_id):
                await ctx.send("❌ Invalid task ID format!")
                return
            
            # Get the task
            task = self.task_manager.get_task_by_id(task_id)
            if not task:
                await ctx.send("❌ Task not found!")
                return
            
            # Check if user owns the task
            if task.user_id != ctx.author.id:
                await ctx.send("❌ You can only delete your own tasks!")
                return
            
            # Delete the task
            success = self.task_manager.delete_task(task_id)
            if success:
                embed = discord.Embed(
                    title="🗑️ Task Deleted",
                    description=f"Task **{task.title}** has been deleted.",
                    color=0xff6b6b
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Failed to delete task. Please try again.")
            
        except Exception as e:
            self.logger.error(f"❌ Error deleting task: {e}")
            await ctx.send("❌ Failed to delete task. Please try again.")
    
    @commands.command(name="edit", help="Edit a task field")
    async def edit_task(self, ctx, task_id: str, field: str, *, value: str):
        """Edit a task field"""
        try:
            # Validate task ID
            if not ValidationHelper.validate_task_id(task_id):
                await ctx.send("❌ Invalid task ID format!")
                return
            
            # Get the task
            task = self.task_manager.get_task_by_id(task_id)
            if not task:
                await ctx.send("❌ Task not found!")
                return
            
            # Check if user owns the task
            if task.user_id != ctx.author.id:
                await ctx.send("❌ You can only edit your own tasks!")
                return
            
            # Validate field
            valid_fields = ["title", "description", "due_date", "priority"]
            if field.lower() not in valid_fields:
                await ctx.send(f"❌ Invalid field! Valid fields: {', '.join(valid_fields)}")
                return
            
            # Prepare update data
            updates = {}
            
            if field.lower() == "title":
                title = ValidationHelper.sanitize_input(value, 100)
                if not title:
                    await ctx.send("❌ Title cannot be empty!")
                    return
                updates["title"] = title
                
            elif field.lower() == "description":
                description = ValidationHelper.sanitize_input(value, 500)
                updates["description"] = description
                
            elif field.lower() == "due_date":
                due_date = TimeParser.parse_time(value)
                if not due_date:
                    await ctx.send("❌ Invalid date format! Try formats like 'tomorrow', 'in 2 hours', or '2024-01-15 14:30'")
                    return
                updates["due_date"] = due_date
                
            elif field.lower() == "priority":
                if not ValidationHelper.validate_priority(value):
                    await ctx.send("❌ Invalid priority! Use: low, medium, or high")
                    return
                updates["priority"] = value.lower()
            
            # Update the task
            success = self.task_manager.update_task(task_id, updates)
            if success:
                # Get updated task
                updated_task = self.task_manager.get_task_by_id(task_id)
                if updated_task:
                    embed = EmbedHelper.create_task_embed(updated_task, "✏️ Task Updated!")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("✅ Task updated, but could not retrieve updated details.")
            else:
                await ctx.send("❌ Failed to update task. Please try again.")
            
        except Exception as e:
            self.logger.error(f"❌ Error editing task: {e}")
            await ctx.send("❌ Failed to edit task. Please try again.")
    
    @commands.command(name="remind", help="Set a reminder for a task")
    async def set_reminder(self, ctx, task_id: str, *, time_and_message: str):
        """Set a reminder for a task"""
        try:
            # Validate task ID
            if not ValidationHelper.validate_task_id(task_id):
                await ctx.send("❌ Invalid task ID format!")
                return
            
            # Get the task
            task = self.task_manager.get_task_by_id(task_id)
            if not task:
                await ctx.send("❌ Task not found!")
                return
            
            # Check if user owns the task
            if task.user_id != ctx.author.id:
                await ctx.send("❌ You can only set reminders for your own tasks!")
                return
            
            # Better parsing for time and message
            # Handle cases like: '2025-07-06' '10:00 AM' message here
            time_str = time_and_message
            message = ""
            
            # Try to extract time and message more intelligently
            if "'" in time_and_message or '"' in time_and_message:
                # Handle quoted time formats
                # Find quoted parts
                quoted_parts = re.findall(r'[\'"]([^\'"]*)[\'"]', time_and_message)
                if quoted_parts:
                    # Combine quoted parts for time
                    time_str = " ".join(quoted_parts)
                    # Get the rest as message
                    remaining = re.sub(r'[\'"][^\'"]*[\'"]', '', time_and_message).strip()
                    if remaining:
                        message = remaining
            else:
                # Original logic for non-quoted formats
                parts = time_and_message.split(" ", 1)
                time_str = parts[0]
                message = parts[1] if len(parts) > 1 else ""
            
            # Clean up time string
            time_str = time_str.strip()
            
            # Parse the time
            reminder_time = TimeParser.parse_time(time_str)
            if not reminder_time:
                await ctx.send("❌ Invalid time format! Try formats like:\n• 'in 2 hours'\n• 'tomorrow'\n• '2025-07-06 10:00 AM'\n• '2025-07-06' '10:00 AM'")
                return
            
            # Check if time is in the past
            if reminder_time <= datetime.now():
                await ctx.send("❌ Reminder time must be in the future!")
                return
            
            # Create the reminder
            reminder_id = self.reminder_handler.create_reminder(
                ctx.author.id, task_id, reminder_time, message
            )
            
            if reminder_id:
                embed = discord.Embed(
                    title="🔔 Reminder Set!",
                    description=f"Reminder set for task **{task.title}**",
                    color=0x00ff00
                )
                embed.add_field(name="Reminder Time", value=TimeParser.format_time(reminder_time), inline=True)
                embed.add_field(name="Time Until", value=TimeParser.format_relative_time(reminder_time), inline=True)
                if message:
                    embed.add_field(name="Message", value=message, inline=False)
                embed.add_field(name="Reminder ID", value=reminder_id, inline=False)
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Failed to set reminder. Please try again.")
            
        except Exception as e:
            self.logger.error(f"❌ Error setting reminder: {e}")
            await ctx.send("❌ Failed to set reminder. Please try again.")
    
    @commands.command(name="priority", help="Set task priority")
    async def set_priority(self, ctx, task_id: str, priority: str):
        """Set task priority"""
        try:
            # Validate task ID
            if not ValidationHelper.validate_task_id(task_id):
                await ctx.send("❌ Invalid task ID format!")
                return
            
            # Validate priority
            if not ValidationHelper.validate_priority(priority):
                await ctx.send("❌ Invalid priority! Use: low, medium, or high")
                return
            
            # Get the task
            task = self.task_manager.get_task_by_id(task_id)
            if not task:
                await ctx.send("❌ Task not found!")
                return
            
            # Check if user owns the task
            if task.user_id != ctx.author.id:
                await ctx.send("❌ You can only set priority for your own tasks!")
                return
            
            # Update priority
            success = self.task_manager.update_task(task_id, {"priority": priority.lower()})
            if success:
                updated_task = self.task_manager.get_task_by_id(task_id)
                if updated_task:
                    embed = EmbedHelper.create_task_embed(updated_task, "🎯 Priority Updated!")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("✅ Priority updated, but could not retrieve updated details.")
            else:
                await ctx.send("❌ Failed to update priority. Please try again.")
            
        except Exception as e:
            self.logger.error(f"❌ Error setting priority: {e}")
            await ctx.send("❌ Failed to set priority. Please try again.")
    
    @commands.command(name="testdm", help="Test if the bot can send you DMs")
    async def test_dm(self, ctx):
        """Test if the bot can send DMs to the user"""
        try:
            embed = discord.Embed(
                title="🧪 DM Test",
                description="If you can see this message, the bot can send you DMs!",
                color=0x00ff00
            )
            embed.add_field(name="User ID", value=ctx.author.id, inline=True)
            embed.add_field(name="Username", value=ctx.author.name, inline=True)
            embed.add_field(name="Time", value=datetime.now().strftime("%Y-%m-%d %I:%M %p"), inline=True)
            
            # Use ctx.author directly (works without members intent)
            await ctx.author.send(embed=embed)
            await ctx.send("✅ DM test sent! Check your private messages.")
            
        except discord.Forbidden:
            await ctx.send("❌ Cannot send DM to you. Please check your Discord privacy settings:\n1. Go to User Settings > Privacy & Safety\n2. Enable 'Allow direct messages from server members'")
        except Exception as e:
            await ctx.send(f"❌ DM test failed: {e}")
            self.logger.error(f"❌ DM test error: {e}")
    
    @commands.command(name="help", help="Show help information")
    async def show_help(self, ctx, command_name: Optional[str] = None):
        """Show help information"""
        try:
            if command_name:
                # Show help for specific command
                command = self.bot.get_command(command_name)
                if command:
                    embed = discord.Embed(
                        title=f"Help: !{command.name}",
                        description=command.help or "No description available.",
                        color=0x7289da
                    )
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"❌ Command '{command_name}' not found!")
            else:
                # Show general help
                embed = EmbedHelper.create_help_embed()
                await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"❌ Error showing help: {e}")
            await ctx.send("❌ Failed to show help. Please try again.")

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(TaskCommands(bot))

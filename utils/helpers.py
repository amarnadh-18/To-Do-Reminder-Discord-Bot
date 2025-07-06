import discord
import re
from datetime import datetime
from typing import List, Optional
from db.models import Task

class EmbedHelper:
    """Helper class for creating Discord embeds"""
    
    @staticmethod
    def create_task_embed(task: Task, title: str = "Task Details") -> discord.Embed:
        """Create an embed for displaying task information"""
        embed = discord.Embed(title=title, color=EmbedHelper._get_priority_color(task.priority))
        
        embed.add_field(name="Title", value=task.title, inline=False)
        
        if task.description:
            embed.add_field(name="Description", value=task.description, inline=False)
        
        if task.due_date:
            embed.add_field(name="Due Date", value=task.due_date.strftime("%Y-%m-%d %I:%M %p"), inline=True)
        
        embed.add_field(name="Priority", value=task.priority.title(), inline=True)
        embed.add_field(name="Status", value="✅ Completed" if task.completed else "⏳ Pending", inline=True)
        
        embed.set_footer(text=f"Created: {task.created_at.strftime('%Y-%m-%d %I:%M %p')}")
        
        return embed
    
    @staticmethod
    def create_task_list_embed(tasks: List[Task], title: str = "Your Tasks") -> discord.Embed:
        """Create an embed for displaying a list of tasks"""
        if not tasks:
            embed = discord.Embed(title=title, description="No tasks found!", color=0x808080)
            return embed
        
        embed = discord.Embed(title=title, color=0x00ff00)
        
        for i, task in enumerate(tasks[:10], 1):  # Limit to 10 tasks per embed
            status = "✅" if task.completed else "⏳"
            priority_emoji = EmbedHelper._get_priority_emoji(task.priority)
            
            due_text = ""
            if task.due_date:
                due_text = f" | Due: {task.due_date.strftime('%m/%d %I:%M %p')}"
            
            embed.add_field(
                name=f"{i}. {status} {task.title}",
                value=f"{priority_emoji} Priority: {task.priority.title()}{due_text}",
                inline=False
            )
        
        if len(tasks) > 10:
            embed.set_footer(text=f"Showing 10 of {len(tasks)} tasks")
        
        return embed
    
    @staticmethod
    def create_reminder_embed(task: Task, message: str = "") -> discord.Embed:
        """Create an embed for reminder notifications"""
        embed = discord.Embed(
            title="🔔 Task Reminder",
            description=f"**{task.title}**\n{message}",
            color=0xff6b6b
        )
        
        if task.description:
            embed.add_field(name="Description", value=task.description, inline=False)
        
        if task.due_date:
            embed.add_field(name="Due Date", value=task.due_date.strftime("%Y-%m-%d %I:%M %p"), inline=True)
        
        embed.add_field(name="Priority", value=task.priority.title(), inline=True)
        
        return embed
    
    @staticmethod
    def create_help_embed() -> discord.Embed:
        """Create a help embed with all available commands"""
        embed = discord.Embed(
            title="📋 To-Do Bot Commands",
            description="Here are all the available commands:",
            color=0x7289da
        )
        
        commands = [
            ("!add <title> [description] [due_date]", "Add a new task"),
            ("!list [completed]", "List your tasks (use 'completed' to show completed tasks)"),
            ("!view <task_id>", "View details of a specific task"),
            ("!complete <task_id>", "Mark a task as completed"),
            ("!delete <task_id>", "Delete a task"),
            ("!edit <task_id> <field> <value>", "Edit a task field (title, description, due_date, priority)"),
            ("!remind <task_id> <time>", "Set a reminder for a task"),
            ("!priority <task_id> <priority>", "Set task priority (low, medium, high)"),
            ("!help", "Show this help message")
        ]
        
        for cmd, desc in commands:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        embed.add_field(
            name="Time Formats",
            value="• Relative: 'in 2 hours', 'tomorrow', 'next monday'\n• Absolute: '2024-01-15 14:30', '3:30 PM'\n• Specific: 'tomorrow at 3pm'",
            inline=False
        )
        
        embed.set_footer(text="Use !help <command> for detailed information about a specific command")
        
        return embed
    
    @staticmethod
    def _get_priority_color(priority: str) -> int:
        """Get color based on priority"""
        colors = {
            "low": 0x00ff00,      # Green
            "medium": 0xffa500,   # Orange
            "high": 0xff0000      # Red
        }
        return colors.get(priority.lower(), 0x808080)
    
    @staticmethod
    def _get_priority_emoji(priority: str) -> str:
        """Get emoji based on priority"""
        emojis = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🔴"
        }
        return emojis.get(priority.lower(), "⚪")

class ValidationHelper:
    """Helper class for input validation"""
    
    @staticmethod
    def validate_priority(priority: str) -> bool:
        """Validate priority input"""
        valid_priorities = ["low", "medium", "high"]
        return priority.lower() in valid_priorities
    
    @staticmethod
    def validate_task_id(task_id: str) -> bool:
        """Validate task ID format"""
        if not task_id or not isinstance(task_id, str):
            return False
        return bool(re.match(r'^[a-f0-9]{24}$', task_id))
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """Sanitize user input"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        
        return text

class PaginationHelper:
    """Helper class for paginating long lists"""
    
    @staticmethod
    def chunk_list(items: List, chunk_size: int = 10) -> List[List]:
        """Split a list into chunks"""
        return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
    
    @staticmethod
    def create_paginated_embeds(items: List, title: str, embed_creator_func) -> List[discord.Embed]:
        """Create multiple embeds for pagination"""
        chunks = PaginationHelper.chunk_list(items)
        embeds = []
        
        for i, chunk in enumerate(chunks, 1):
            embed = embed_creator_func(chunk, f"{title} (Page {i}/{len(chunks)})")
            embeds.append(embed)
        
        return embeds

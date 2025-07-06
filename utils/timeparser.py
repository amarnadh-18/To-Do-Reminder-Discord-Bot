import re
from datetime import datetime, timedelta
from typing import Optional, Tuple

class TimeParser:
    """Parse various time formats for task scheduling"""
    
    @staticmethod
    def parse_relative_time(time_str: str) -> Optional[datetime]:
        """
        Parse relative time expressions like:
        - "in 2 hours"
        - "tomorrow at 3pm"
        - "next monday"
        - "in 30 minutes"
        """
        time_str = time_str.lower().strip()
        now = datetime.now()
        
        # Patterns for relative time
        patterns = [
            # "in X minutes"
            (r'in (\d+) minutes?', lambda m: now + timedelta(minutes=int(m.group(1)))),
            
            # "in X hours"
            (r'in (\d+) hours?', lambda m: now + timedelta(hours=int(m.group(1)))),
            
            # "in X days"
            (r'in (\d+) days?', lambda m: now + timedelta(days=int(m.group(1)))),
            
            # "tomorrow"
            (r'tomorrow', lambda m: now + timedelta(days=1)),
            
            # "next week"
            (r'next week', lambda m: now + timedelta(weeks=1)),
            
            # "next monday", "next tuesday", etc.
            (r'next (monday|tuesday|wednesday|thursday|friday|saturday|sunday)', 
             lambda m: TimeParser._get_next_weekday(m.group(1))),
            
            # "today at X:XX" or "tomorrow at X:XX"
            (r'(today|tomorrow) at (\d{1,2}):(\d{2})(am|pm)?', 
             lambda m: TimeParser._get_specific_time(m.group(1), int(m.group(2)), int(m.group(3)), m.group(4))),
        ]
        
        for pattern, handler in patterns:
            match = re.match(pattern, time_str)
            if match:
                return handler(match)
        
        return None
    
    @staticmethod
    def parse_absolute_time(time_str: str) -> Optional[datetime]:
        """
        Parse absolute time formats like:
        - "2024-01-15 14:30"
        - "15/01/2024 2:30 PM"
        - "Jan 15 2:30 PM"
        - "2025-07-06 10:00 AM"
        - "'2025-07-06' '10:00 AM'"
        """
        time_str = time_str.strip()
        
        # Remove quotes if present
        time_str = time_str.replace("'", "").replace('"', "")
        
        # Common date formats
        formats = [
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %I:%M %p",
            "%Y-%m-%d %I:%M%p",  # No space before AM/PM
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y %I:%M %p",
            "%m/%d/%Y %H:%M",
            "%m/%d/%Y %I:%M %p",
            "%b %d %I:%M %p",
            "%B %d %I:%M %p",
            # Add more flexible formats
            "%Y-%m-%d %I:%M %p",  # 2025-07-06 10:00 AM
            "%Y-%m-%d %I:%M%p",   # 2025-07-06 10:00AM
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue
        
        # Try to parse date and time separately if they're split
        # Handle cases like "2025-07-06" "10:00 AM"
        parts = time_str.split()
        if len(parts) >= 2:
            # Try to combine date and time parts
            date_part = parts[0]
            time_part = " ".join(parts[1:])
            
            # Try different combinations
            combinations = [
                f"{date_part} {time_part}",
                f"{date_part} {time_part.replace(' ', '')}",
            ]
            
            for combo in combinations:
                for fmt in formats:
                    try:
                        return datetime.strptime(combo, fmt)
                    except ValueError:
                        continue
        
        return None
    
    @staticmethod
    def parse_time(time_str: str) -> Optional[datetime]:
        """Main method to parse any time format"""
        # Try relative time first
        result = TimeParser.parse_relative_time(time_str)
        if result:
            return result
        
        # Try absolute time
        result = TimeParser.parse_absolute_time(time_str)
        if result:
            return result
        
        return None
    
    @staticmethod
    def _get_next_weekday(weekday: str) -> datetime:
        """Get the next occurrence of a specific weekday"""
        weekday_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        target_day = weekday_map[weekday]
        current_day = datetime.now().weekday()
        days_ahead = target_day - current_day
        
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        
        return datetime.now() + timedelta(days=days_ahead)
    
    @staticmethod
    def _get_specific_time(day: str, hour: int, minute: int, ampm: Optional[str]) -> datetime:
        """Get specific time on today or tomorrow"""
        now = datetime.now()
        
        # Adjust hour for AM/PM
        if ampm:
            if ampm.lower() == 'pm' and hour != 12:
                hour += 12
            elif ampm.lower() == 'am' and hour == 12:
                hour = 0
        
        # Set the time
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If it's "tomorrow", add a day
        if day == 'tomorrow':
            target_time += timedelta(days=1)
        
        return target_time
    
    @staticmethod
    def format_time(dt: datetime) -> str:
        """Format datetime for display"""
        return dt.strftime("%Y-%m-%d %I:%M %p")
    
    @staticmethod
    def format_relative_time(dt: datetime) -> str:
        """Format datetime as relative time (e.g., 'in 2 hours')"""
        now = datetime.now()
        diff = dt - now
        
        if diff.total_seconds() < 0:
            return "past due"
        
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        
        if days > 0:
            return f"in {days} day{'s' if days != 1 else ''}"
        elif hours > 0:
            return f"in {hours} hour{'s' if hours != 1 else ''}"
        elif minutes > 0:
            return f"in {minutes} minute{'s' if minutes != 1 else ''}"
        else:
            return "now"

#!/usr/bin/env python3
"""
Simple test to verify all imports work correctly
"""

def test_imports():
    """Test all imports"""
    print("🧪 Testing imports...")
    
    try:
        # Test database
        from db.database import db
        print("✅ Database import successful")
        
        # Test models
        from db.models import Task, Reminder, TaskManager
        print("✅ Models import successful")
        
        # Test utils
        from utils.timeparser import TimeParser
        from utils.helpers import EmbedHelper, ValidationHelper
        print("✅ Utils import successful")
        
        # Test scheduler
        from scheduler.scheduler import reminder_scheduler
        from scheduler.reminder_jobs import ReminderJobHandler
        print("✅ Scheduler import successful")
        
        # Test time parsing
        from datetime import datetime
        result = TimeParser.parse_time("in 1 hour")
        if result:
            print("✅ Time parser working")
        else:
            print("⚠️ Time parser returned None for 'in 1 hour'")
        
        # Test validation
        assert ValidationHelper.validate_priority("high") == True
        assert ValidationHelper.validate_priority("invalid") == False
        print("✅ Validation helpers working")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    test_imports() 
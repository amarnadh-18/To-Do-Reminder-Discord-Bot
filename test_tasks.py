#!/usr/bin/env python3
"""
Test script to verify tasks.py fixes
"""

def test_validation_helper():
    """Test ValidationHelper methods"""
    print("🧪 Testing ValidationHelper...")
    
    try:
        from utils.helpers import ValidationHelper
        
        # Test validate_task_id
        assert ValidationHelper.validate_task_id("507f1f77bcf86cd799439011") == True
        assert ValidationHelper.validate_task_id("invalid") == False
        assert ValidationHelper.validate_task_id("") == False
        assert ValidationHelper.validate_task_id(None) == False
        
        # Test validate_priority
        assert ValidationHelper.validate_priority("high") == True
        assert ValidationHelper.validate_priority("medium") == True
        assert ValidationHelper.validate_priority("low") == True
        assert ValidationHelper.validate_priority("invalid") == False
        
        # Test sanitize_input
        assert ValidationHelper.sanitize_input("  test  input  ") == "test input"
        assert ValidationHelper.sanitize_input("") == ""
        assert ValidationHelper.sanitize_input(None) == ""
        
        print("✅ ValidationHelper tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ ValidationHelper test failed: {e}")
        return False

def test_embed_helper():
    """Test EmbedHelper methods"""
    print("\n🧪 Testing EmbedHelper...")
    
    try:
        from utils.helpers import EmbedHelper
        from db.models import Task
        from datetime import datetime
        
        # Create a test task
        task = Task(
            user_id=123456789,
            title="Test Task",
            description="Test description",
            priority="high"
        )
        
        # Test create_task_embed
        embed = EmbedHelper.create_task_embed(task)
        assert embed.title == "Task Details"
        assert embed.color == 0xff0000  # Red for high priority
        
        # Test create_task_list_embed
        tasks = [task]
        list_embed = EmbedHelper.create_task_list_embed(tasks)
        assert list_embed.title == "Your Tasks"
        
        # Test create_help_embed
        help_embed = EmbedHelper.create_help_embed()
        assert help_embed.title == "📋 To-Do Bot Commands"
        
        print("✅ EmbedHelper tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ EmbedHelper test failed: {e}")
        return False

def test_time_parser():
    """Test TimeParser methods"""
    print("\n🧪 Testing TimeParser...")
    
    try:
        from utils.timeparser import TimeParser
        
        # Test parse_time
        result = TimeParser.parse_time("in 1 hour")
        assert result is not None
        
        result = TimeParser.parse_time("tomorrow")
        assert result is not None
        
        result = TimeParser.parse_time("invalid")
        assert result is None
        
        print("✅ TimeParser tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ TimeParser test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing tasks.py fixes...")
    print("=" * 50)
    
    tests = [
        test_validation_helper,
        test_embed_helper,
        test_time_parser,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The tasks.py fixes are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    main() 
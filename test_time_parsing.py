#!/usr/bin/env python3
"""
Test script to verify time parsing works with various formats
"""

def test_time_parsing():
    """Test time parsing with various formats"""
    print("🧪 Testing Time Parsing...")
    
    try:
        from utils.timeparser import TimeParser
        
        # Test cases including the user's format
        test_cases = [
            ("'2025-07-06' '10:00 AM'", "Quoted date and time"),
            ("2025-07-06 10:00 AM", "Date and time without quotes"),
            ("in 2 hours", "Relative time"),
            ("tomorrow", "Relative time"),
            ("2025-07-06 10:00AM", "Date and time without space before AM"),
            ("'2025-07-06' '10:00 AM' Don't forget!", "Quoted with message"),
        ]
        
        for time_str, description in test_cases:
            result = TimeParser.parse_time(time_str)
            if result:
                print(f"✅ {description}: '{time_str}' -> {result}")
            else:
                print(f"❌ {description}: '{time_str}' -> Failed to parse")
        
        # Test the specific user case
        user_case = "'2025-07-06' '10:00 AM'"
        result = TimeParser.parse_time(user_case)
        if result:
            print(f"\n🎉 SUCCESS: Your format '{user_case}' works!")
            print(f"   Parsed as: {result}")
        else:
            print(f"\n❌ FAILED: Your format '{user_case}' still doesn't work")
        
        return True
        
    except Exception as e:
        print(f"❌ Time parsing test failed: {e}")
        return False

def test_reminder_parsing():
    """Test the reminder command parsing logic"""
    print("\n🧪 Testing Reminder Command Parsing...")
    
    try:
        import re
        
        # Test the parsing logic from the command
        test_input = "'2025-07-06' '10:00 AM' Don't forget this task!"
        
        time_str = test_input
        message = ""
        
        # Handle quoted time formats
        if "'" in test_input or '"' in test_input:
            # Find quoted parts
            quoted_parts = re.findall(r'[\'"]([^\'"]*)[\'"]', test_input)
            if quoted_parts:
                # Combine quoted parts for time
                time_str = " ".join(quoted_parts)
                # Get the rest as message
                remaining = re.sub(r'[\'"][^\'"]*[\'"]', '', test_input).strip()
                if remaining:
                    message = remaining
        
        print(f"✅ Input: '{test_input}'")
        print(f"   Time: '{time_str}'")
        print(f"   Message: '{message}'")
        
        # Test parsing the extracted time
        from utils.timeparser import TimeParser
        result = TimeParser.parse_time(time_str)
        if result:
            print(f"   Parsed time: {result}")
        else:
            print(f"   Failed to parse time")
        
        return True
        
    except Exception as e:
        print(f"❌ Reminder parsing test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Time Parsing Fixes...")
    print("=" * 50)
    
    test_time_parsing()
    test_reminder_parsing()
    
    print("\n" + "=" * 50)
    print("🎯 Test completed! Try your reminder command again.") 
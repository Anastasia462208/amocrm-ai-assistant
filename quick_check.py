#!/usr/bin/env python3
"""
Quick System Check for AmoCRM AI Assistant
Verifies that all components are working correctly
"""

import sys
import tempfile
import os
from database_manager import DatabaseManager
from context_manager import ConversationContextManager

def check_database():
    """Check database functionality"""
    print("🗄️  Checking database...")
    try:
        # Create temporary database
        test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        test_db.close()
        
        db = DatabaseManager(test_db.name)
        
        # Test basic operations
        client_id = db.get_or_create_client(12345, "Test Client")
        conv_id = db.get_or_create_conversation(client_id)
        db.add_message(conv_id, "client", "Test message")
        
        messages = db.get_conversation_context(conv_id)
        assert len(messages) == 1
        
        os.unlink(test_db.name)
        print("   ✅ Database: OK")
        return True
        
    except Exception as e:
        print(f"   ❌ Database: Error - {e}")
        return False

def check_context_manager():
    """Check context management"""
    print("🧠 Checking context manager...")
    try:
        test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        test_db.close()
        
        db = DatabaseManager(test_db.name)
        context_manager = ConversationContextManager(db)
        
        # Test intent analysis
        intents = context_manager.analyze_message_intent("Хочу забронировать тур")
        assert 'booking_inquiry' in intents
        
        # Test entity extraction
        entities = context_manager.extract_entities("Сплав по Чусовой на 3 дня")
        assert entities.get('tour_name') == 'чусовая'
        
        os.unlink(test_db.name)
        print("   ✅ Context Manager: OK")
        return True
        
    except Exception as e:
        print(f"   ❌ Context Manager: Error - {e}")
        return False

def check_response_generation():
    """Check response generation"""
    print("💬 Checking response generation...")
    try:
        from manus_ai_assistant_simple import SimplifiedManusAssistant
        
        test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        test_db.close()
        
        assistant = SimplifiedManusAssistant(test_db.name)
        
        # Test simple response
        response = assistant._generate_simple_response(
            conversation_id=1,
            message="Сколько стоит сплав?",
            kb_results=[]
        )
        
        assert isinstance(response, str)
        assert len(response) > 10
        
        os.unlink(test_db.name)
        print("   ✅ Response Generation: OK")
        return True
        
    except Exception as e:
        print(f"   ❌ Response Generation: Error - {e}")
        return False

def check_dependencies():
    """Check required dependencies"""
    print("📦 Checking dependencies...")
    
    required_modules = [
        'selenium',
        'requests', 
        'sqlite3',
        'threading',
        'json',
        'datetime',
        'logging'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"   ❌ Missing modules: {', '.join(missing)}")
        return False
    else:
        print("   ✅ Dependencies: OK")
        return True

def main():
    """Run all checks"""
    print("🚀 AmoCRM AI Assistant - Quick System Check")
    print("=" * 50)
    
    checks = [
        check_dependencies,
        check_database,
        check_context_manager,
        check_response_generation
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Check failed: {e}")
            results.append(False)
    
    print("\n📊 Summary:")
    print(f"   Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("   🎉 All checks passed! System is ready.")
        return True
    else:
        print("   ⚠️  Some checks failed. Please review errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

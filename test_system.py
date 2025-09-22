#!/usr/bin/env python3
"""
Test Suite for AmoCRM AI Assistant System
Tests all components and simulates parallel conversations
"""

import unittest
import threading
import time
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock
from database_manager import DatabaseManager
from context_manager import ConversationContextManager
from manus_ai_assistant_simple import SimplifiedManusAssistant

class TestDatabaseManager(unittest.TestCase):
    """Test database operations"""
    
    def setUp(self):
        """Set up test database"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.db = DatabaseManager(self.test_db.name)
    
    def tearDown(self):
        """Clean up test database"""
        os.unlink(self.test_db.name)
    
    def test_client_creation(self):
        """Test client creation and retrieval"""
        client_id = self.db.get_or_create_client(12345, "Тест Клиент", "+7-999-123-45-67")
        self.assertIsInstance(client_id, int)
        
        # Test duplicate creation
        client_id2 = self.db.get_or_create_client(12345)
        self.assertEqual(client_id, client_id2)
    
    def test_conversation_management(self):
        """Test conversation creation and management"""
        client_id = self.db.get_or_create_client(12345)
        conv_id = self.db.get_or_create_conversation(client_id, 67890)
        self.assertIsInstance(conv_id, int)
        
        # Add messages
        self.db.add_message(conv_id, "client", "Привет!")
        self.db.add_message(conv_id, "assistant", "Здравствуйте!")
        
        # Get conversation context
        messages = self.db.get_conversation_context(conv_id)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['content'], "Привет!")
    
    def test_knowledge_base(self):
        """Test knowledge base operations"""
        # Add knowledge base entry
        kb_id = self.db.add_knowledge_base_entry(
            "Сплав по Чусовой",
            "Семейные сплавы по реке Чусовая от 2 до 5 дней",
            "tours",
            ["чусовая", "семейный", "сплав"]
        )
        self.assertIsInstance(kb_id, int)
        
        # Search knowledge base
        results = self.db.search_knowledge_base("чусовая семейный")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Сплав по Чусовой")

class TestContextManager(unittest.TestCase):
    """Test conversation context management"""
    
    def setUp(self):
        """Set up test context manager"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.db = DatabaseManager(self.test_db.name)
        self.context_manager = ConversationContextManager(self.db)
    
    def tearDown(self):
        """Clean up"""
        os.unlink(self.test_db.name)
    
    def test_intent_analysis(self):
        """Test message intent analysis"""
        # Test booking intent
        intents = self.context_manager.analyze_message_intent("Хочу забронировать тур")
        self.assertIn('booking_inquiry', intents)
        
        # Test price intent
        intents = self.context_manager.analyze_message_intent("Сколько стоит сплав?")
        self.assertIn('price_inquiry', intents)
        
        # Test equipment intent
        intents = self.context_manager.analyze_message_intent("Что нужно взять с собой?")
        self.assertIn('equipment_inquiry', intents)
    
    def test_entity_extraction(self):
        """Test entity extraction from messages"""
        entities = self.context_manager.extract_entities(
            "Планирую сплав по Чусовой на 3 дня в июне для 2 взрослых"
        )
        
        self.assertEqual(entities.get('tour_name'), 'чусовая')
        self.assertEqual(entities.get('month'), 6)
        self.assertIn(3, entities.get('numbers', []))
        self.assertIn(2, entities.get('numbers', []))
    
    def test_conversation_state_tracking(self):
        """Test conversation state management"""
        client_id = self.db.get_or_create_client(12345)
        conv_id = self.db.get_or_create_conversation(client_id)
        
        # Initial message
        self.context_manager.update_conversation_context(
            conv_id, "Привет! Интересуют туры", 'client'
        )
        
        # Booking inquiry
        self.context_manager.update_conversation_context(
            conv_id, "Хочу забронировать сплав", 'client'
        )
        
        context = self.context_manager.get_conversation_context_summary(conv_id)
        self.assertEqual(context.get('conversation_state'), 'booking_process')

class TestManusAssistant(unittest.TestCase):
    """Test Manus AI Assistant"""
    
    def setUp(self):
        """Set up test assistant"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        
        # Mock Manus API
        self.mock_manus_response = {
            'task_id': 'test_task_123',
            'task_url': 'https://manus.im/app/test_task_123'
        }
    
    def tearDown(self):
        """Clean up"""
        os.unlink(self.test_db.name)
    
    @patch('requests.post')
    def test_manus_api_integration(self, mock_post):
        """Test Manus API integration"""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.mock_manus_response
        
        assistant = SimplifiedManusAssistant(self.test_db.name)
        
        success, result = assistant.send_manus_task("Test prompt")
        self.assertTrue(success)
        self.assertEqual(result['task_id'], 'test_task_123')
    
    @patch('requests.post')
    def test_message_processing(self, mock_post):
        """Test message processing workflow"""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self.mock_manus_response
        
        assistant = SimplifiedManusAssistant(self.test_db.name)
        
        # Process simple message
        response = assistant.process_client_message(
            amocrm_contact_id=12345,
            message="Сколько стоит сплав по Чусовой?",
            use_manus=False
        )
        
        self.assertIsInstance(response, str)
        self.assertIn("Чусовая", response)
        
        # Process complex message with Manus
        response = assistant.process_client_message(
            amocrm_contact_id=12345,
            message="Помогите выбрать лучший тур для семьи с детьми",
            use_manus=True
        )
        
        self.assertIsInstance(response, str)
        self.assertIn("консультацию", response)

class TestParallelConversations(unittest.TestCase):
    """Test parallel conversation handling"""
    
    def setUp(self):
        """Set up for parallel testing"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.results = []
        self.errors = []
    
    def tearDown(self):
        """Clean up"""
        os.unlink(self.test_db.name)
    
    def simulate_conversation(self, contact_id, messages):
        """Simulate a conversation with multiple messages"""
        try:
            assistant = SimplifiedManusAssistant(self.test_db.name)
            
            conversation_results = []
            for message in messages:
                response = assistant.process_client_message(
                    amocrm_contact_id=contact_id,
                    message=message,
                    use_manus=False  # Use simple responses for testing
                )
                conversation_results.append({
                    'contact_id': contact_id,
                    'message': message,
                    'response': response,
                    'timestamp': time.time()
                })
                time.sleep(0.1)  # Small delay between messages
            
            self.results.extend(conversation_results)
            
        except Exception as e:
            self.errors.append({
                'contact_id': contact_id,
                'error': str(e),
                'timestamp': time.time()
            })
    
    def test_parallel_conversations(self):
        """Test handling multiple parallel conversations"""
        # Define test conversations
        test_conversations = [
            (10001, ["Привет!", "Сколько стоит сплав?", "Хочу забронировать"]),
            (10002, ["Добрый день", "Что включено в тур?", "Какие даты доступны?"]),
            (10003, ["Здравствуйте", "Безопасно ли для детей?", "Что взять с собой?"]),
            (10004, ["Привет", "Сравните туры по Чусовой и Серге", "Посоветуйте лучший"]),
            (10005, ["Добрый день", "Нужна ли подготовка?", "Сколько человек в группе?"]),
        ]
        
        # Start parallel conversations
        threads = []
        start_time = time.time()
        
        for contact_id, messages in test_conversations:
            thread = threading.Thread(
                target=self.simulate_conversation,
                args=(contact_id, messages)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all conversations to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        print(f"\n📊 Parallel Conversation Test Results:")
        print(f"   Total conversations: {len(test_conversations)}")
        print(f"   Total messages processed: {len(self.results)}")
        print(f"   Total time: {total_time:.2f} seconds")
        print(f"   Average time per message: {total_time/len(self.results):.2f} seconds")
        print(f"   Errors: {len(self.errors)}")
        
        # Assertions
        self.assertEqual(len(self.errors), 0, f"Errors occurred: {self.errors}")
        self.assertEqual(len(self.results), 15)  # 5 conversations × 3 messages each
        
        # Check that all conversations got responses
        contact_ids = set(result['contact_id'] for result in self.results)
        self.assertEqual(len(contact_ids), 5)
        
        # Check response quality
        for result in self.results:
            self.assertIsInstance(result['response'], str)
            self.assertGreater(len(result['response']), 10)

class TestSystemPerformance(unittest.TestCase):
    """Test system performance and optimization"""
    
    def setUp(self):
        """Set up performance testing"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
    
    def tearDown(self):
        """Clean up"""
        os.unlink(self.test_db.name)
    
    def test_database_performance(self):
        """Test database performance with many operations"""
        db = DatabaseManager(self.test_db.name)
        
        start_time = time.time()
        
        # Create many clients and conversations
        for i in range(100):
            client_id = db.get_or_create_client(i, f"Client {i}")
            conv_id = db.get_or_create_conversation(client_id)
            
            # Add messages
            for j in range(10):
                db.add_message(conv_id, "client", f"Message {j}")
                db.add_message(conv_id, "assistant", f"Response {j}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n⚡ Database Performance Test:")
        print(f"   Created 100 clients, 100 conversations, 2000 messages")
        print(f"   Total time: {total_time:.2f} seconds")
        print(f"   Operations per second: {2200/total_time:.0f}")
        
        # Performance should be reasonable
        self.assertLess(total_time, 10.0, "Database operations too slow")
    
    def test_context_analysis_performance(self):
        """Test context analysis performance"""
        db = DatabaseManager(self.test_db.name)
        context_manager = ConversationContextManager(db)
        
        test_messages = [
            "Привет! Хочу забронировать сплав по Чусовой на 3 дня в июне",
            "Сколько стоит тур для семьи из 4 человек?",
            "Что нужно взять с собой? Безопасно ли для детей?",
            "Какие даты доступны в июле? Есть ли скидки?",
            "Помогите выбрать между Чусовой и Сергой"
        ]
        
        start_time = time.time()
        
        for message in test_messages * 20:  # 100 messages total
            intents = context_manager.analyze_message_intent(message)
            entities = context_manager.extract_entities(message)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n🧠 Context Analysis Performance Test:")
        print(f"   Analyzed 100 messages")
        print(f"   Total time: {total_time:.2f} seconds")
        print(f"   Messages per second: {100/total_time:.0f}")
        
        # Should be fast
        self.assertLess(total_time, 5.0, "Context analysis too slow")

def run_load_test():
    """Run a comprehensive load test"""
    print("\n🚀 Starting Load Test for 20 Parallel Conversations")
    print("=" * 60)
    
    # Create test database
    test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    test_db.close()
    
    try:
        results = []
        errors = []
        
        def simulate_client_conversation(client_id):
            """Simulate a realistic client conversation"""
            try:
                assistant = SimplifiedManusAssistant(test_db.name)
                
                # Realistic conversation flow
                messages = [
                    "Здравствуйте!",
                    "Интересуют сплавы по рекам",
                    "Сколько стоит тур по Чусовой?",
                    "Что включено в стоимость?",
                    "Подходит ли для детей 10 лет?",
                    "Какие даты доступны в июле?",
                    "Хочу забронировать на 4 человек"
                ]
                
                conversation_start = time.time()
                
                for i, message in enumerate(messages):
                    start_time = time.time()
                    
                    response = assistant.process_client_message(
                        amocrm_contact_id=client_id,
                        message=message,
                        use_manus=False
                    )
                    
                    response_time = time.time() - start_time
                    
                    results.append({
                        'client_id': client_id,
                        'message_num': i + 1,
                        'response_time': response_time,
                        'response_length': len(response),
                        'timestamp': time.time()
                    })
                    
                    # Simulate realistic delay between messages
                    time.sleep(0.5)
                
                conversation_time = time.time() - conversation_start
                print(f"✅ Client {client_id}: {len(messages)} messages in {conversation_time:.1f}s")
                
            except Exception as e:
                errors.append({
                    'client_id': client_id,
                    'error': str(e)
                })
                print(f"❌ Client {client_id}: Error - {e}")
        
        # Start 20 parallel conversations
        threads = []
        load_test_start = time.time()
        
        for client_id in range(20001, 20021):  # 20 clients
            thread = threading.Thread(
                target=simulate_client_conversation,
                args=(client_id,)
            )
            threads.append(thread)
            thread.start()
            
            # Small delay to simulate realistic arrival pattern
            time.sleep(0.1)
        
        # Wait for all conversations to complete
        for thread in threads:
            thread.join()
        
        load_test_time = time.time() - load_test_start
        
        # Analyze results
        print(f"\n📊 Load Test Results:")
        print(f"   Total clients: 20")
        print(f"   Total messages: {len(results)}")
        print(f"   Total time: {load_test_time:.1f} seconds")
        print(f"   Errors: {len(errors)}")
        
        if results:
            avg_response_time = sum(r['response_time'] for r in results) / len(results)
            max_response_time = max(r['response_time'] for r in results)
            min_response_time = min(r['response_time'] for r in results)
            
            print(f"   Average response time: {avg_response_time:.2f}s")
            print(f"   Max response time: {max_response_time:.2f}s")
            print(f"   Min response time: {min_response_time:.2f}s")
            print(f"   Messages per second: {len(results)/load_test_time:.1f}")
        
        # Success criteria
        success = (
            len(errors) == 0 and
            len(results) == 140 and  # 20 clients × 7 messages
            avg_response_time < 2.0 and
            max_response_time < 5.0
        )
        
        print(f"\n🎯 Load Test: {'✅ PASSED' if success else '❌ FAILED'}")
        
        return success
        
    finally:
        os.unlink(test_db.name)

if __name__ == '__main__':
    print("🧪 AmoCRM AI Assistant Test Suite")
    print("=" * 50)
    
    # Run unit tests
    print("\n1. Running Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run load test
    print("\n2. Running Load Test...")
    load_test_success = run_load_test()
    
    print(f"\n🏁 All Tests Complete!")
    print(f"Load Test: {'✅ PASSED' if load_test_success else '❌ FAILED'}")

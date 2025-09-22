#!/usr/bin/env python3
"""
Simplified Manus AI Assistant for testing without web scraping
Focuses on core functionality for 20 parallel conversations
"""

import requests
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database_manager import DatabaseManager
from queue import Queue

class SimplifiedManusAssistant:
    def __init__(self, db_path: str = "conversations.db"):
        self.db = DatabaseManager(db_path)
        self.manus_api_key = self.db.get_config('manus_api_key')
        self.manus_base_url = "https://api.manus.im/v1/tasks"
        
        # Task tracking
        self.active_tasks = {}  # task_id -> conversation_id mapping
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def send_manus_task(self, prompt: str, mode: str = "fast") -> Tuple[bool, Dict]:
        """Send task to Manus API"""
        headers = {
            "API_KEY": self.manus_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "mode": mode,
            "attachments": []
        }
        
        try:
            response = requests.post(
                self.manus_base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return False, {"error": str(e)}
    
    def process_client_message(self, amocrm_contact_id: int, message: str, 
                             amocrm_lead_id: int = None, use_manus: bool = True) -> str:
        """Process incoming client message and generate response"""
        
        # Get or create client and conversation
        client_id = self.db.get_or_create_client(amocrm_contact_id)
        conversation_id = self.db.get_or_create_conversation(client_id, amocrm_lead_id)
        
        # Add client message to database
        self.db.add_message(conversation_id, "client", message)
        
        # Get conversation context
        context_messages = self.db.get_conversation_context(conversation_id, limit=10)
        
        # Search knowledge base for relevant information
        kb_results = self.db.search_knowledge_base(message, limit=3)
        
        if use_manus and self._needs_manus_processing(message):
            # Use Manus for complex queries
            return self._process_with_manus(conversation_id, message, context_messages, kb_results)
        else:
            # Generate simple response using knowledge base
            return self._generate_simple_response(conversation_id, message, kb_results)
    
    def _needs_manus_processing(self, message: str) -> bool:
        """Determine if message needs complex Manus processing"""
        complex_keywords = [
            "сравни", "посоветуй", "что лучше", "помоги выбрать", 
            "расскажи подробно", "какие варианты", "планирую поездку",
            "маршрут", "программа", "что включено", "как добраться",
            "безопасность", "снаряжение", "погода", "условия"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in complex_keywords)
    
    def _process_with_manus(self, conversation_id: int, message: str, 
                           context: List[Dict], kb_results: List[Dict]) -> str:
        """Process message using Manus API"""
        
        # Build enhanced prompt
        prompt = self._build_enhanced_prompt(message, context, kb_results)
        
        # Create AI task in database
        ai_task_id = self.db.create_ai_task(
            conversation_id=conversation_id,
            task_type="manus_complex_query",
            prompt=prompt,
            api_provider='manus'
        )
        
        # Send to Manus
        success, result = self.send_manus_task(prompt)
        
        if success and 'task_id' in result:
            task_id = result['task_id']
            task_url = result.get('task_url', '')
            
            # Update AI task with Manus task ID
            self.db.update_ai_task(
                task_id=ai_task_id,
                api_task_id=task_id,
                status='processing'
            )
            
            # Track active task
            self.active_tasks[task_id] = {
                'conversation_id': conversation_id,
                'ai_task_id': ai_task_id,
                'created_at': datetime.now(),
                'task_url': task_url
            }
            
            self.logger.info(f"Manus task created: {task_id}")
            
            # Return immediate response with task tracking info
            immediate_response = self._generate_immediate_response(message, kb_results, task_id)
            self.db.add_message(conversation_id, "assistant", immediate_response, "immediate_response")
            
            return immediate_response
        else:
            # Fallback to simple response if Manus fails
            self.logger.error(f"Manus API failed: {result}")
            self.db.update_ai_task(task_id=ai_task_id, status='failed', response=str(result))
            
            fallback_response = self._generate_simple_response(conversation_id, message, kb_results)
            return fallback_response
    
    def _build_enhanced_prompt(self, message: str, context: List[Dict], kb_results: List[Dict]) -> str:
        """Build enhanced prompt for Manus API"""
        
        system_prompt = """
Ты профессиональный ассистент турагентства "Все на сплав" по речным сплавам на Урале.

Компания специализируется на:
- Сплавы по реке Чусовая (семейные, 2-5 дней, от 15000 руб)
- Сплавы по реке Серга (однодневные, от 3500 руб)
- Организация корпоративных сплавов
- Прокат снаряжения
- Трансфер и питание

Твоя задача:
1. Отвечать дружелюбно и профессионально
2. Предлагать конкретные туры с ценами и датами
3. Помогать с выбором подходящего сплава
4. Консультировать по снаряжению и безопасности
5. Предлагать заполнить форму бронирования при готовности клиента

Сайт компании: vsenasplav.ru
Контакты для бронирования: указывай, что клиент может связаться через сайт или AmoCRM.

Всегда предлагай конкретные решения и следующие шаги.
"""
        
        # Add knowledge base context
        if kb_results:
            kb_context = "\n\nИнформация из базы знаний:\n"
            for result in kb_results:
                kb_context += f"• {result['title']}: {result['content']}\n"
        else:
            kb_context = ""
        
        # Add conversation context
        if context:
            conv_context = "\n\nПредыдущие сообщения:\n"
            for msg in context[-5:]:
                role = "Клиент" if msg['sender_type'] == 'client' else "Ассистент"
                conv_context += f"{role}: {msg['content']}\n"
        else:
            conv_context = ""
        
        current_query = f"\n\nВопрос клиента: {message}\n\nДай подробный и полезный ответ:"
        
        return system_prompt + kb_context + conv_context + current_query
    
    def _generate_immediate_response(self, message: str, kb_results: List[Dict], task_id: str) -> str:
        """Generate immediate response while Manus processes"""
        
        base_response = "Спасибо за ваш вопрос! "
        
        if kb_results:
            relevant_info = kb_results[0]
            base_response += f"По теме '{relevant_info['title']}': {relevant_info['content'][:150]}... "
        
        base_response += f"Сейчас готовлю для вас подробную консультацию. Это займет 1-2 минуты."
        base_response += f"\n\n📋 Номер запроса: {task_id[:8]}... (для отслеживания)"
        
        return base_response
    
    def _generate_simple_response(self, conversation_id: int, message: str, kb_results: List[Dict]) -> str:
        """Generate simple response using knowledge base"""
        
        if not kb_results:
            response = """Спасибо за ваш интерес к нашим турам! 

🚣‍♂️ Основные направления:
• Чусовая - семейные сплавы 2-5 дней (от 15000 руб)
• Серга - однодневные сплавы (от 3500 руб)

Что именно вас интересует:
- Конкретные даты и цены?
- Программа тура?
- Снаряжение и подготовка?
- Условия бронирования?

Готов помочь с выбором! 😊"""
        else:
            # Use most relevant result
            best_result = kb_results[0]
            response = f"📋 {best_result['title']}\n\n{best_result['content']}"
            
            # Add related information
            if len(kb_results) > 1:
                response += f"\n\n💡 Также полезно знать: {kb_results[1]['title']}"
            
            response += "\n\n❓ Есть дополнительные вопросы или готовы к бронированию?"
        
        # Add response to database
        self.db.add_message(conversation_id, "assistant", response, "simple_response")
        
        return response
    
    def check_manus_task_status(self, task_id: str) -> Optional[str]:
        """Check if Manus task has completed (placeholder for now)"""
        # For now, return None since we can't retrieve results programmatically
        # In a real implementation, this would check the web interface
        return None
    
    def get_task_info(self, task_id: str) -> Optional[Dict]:
        """Get information about a Manus task"""
        return self.active_tasks.get(task_id)
    
    def list_active_tasks(self) -> List[Dict]:
        """List all active Manus tasks"""
        return [
            {
                "task_id": task_id,
                "conversation_id": info["conversation_id"],
                "created_at": info["created_at"].isoformat(),
                "task_url": info.get("task_url", "")
            }
            for task_id, info in self.active_tasks.items()
        ]
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        return {
            "active_conversations": self.db.get_active_conversations_count(),
            "active_manus_tasks": len(self.active_tasks),
            "total_tasks_today": self._count_tasks_today(),
            "knowledge_base_entries": self._count_kb_entries()
        }
    
    def _count_tasks_today(self) -> int:
        """Count AI tasks created today"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) as count
                FROM ai_tasks
                WHERE DATE(created_at) = DATE('now')
            """)
            return cursor.fetchone()['count']
    
    def _count_kb_entries(self) -> int:
        """Count active knowledge base entries"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) as count
                FROM knowledge_base
                WHERE is_active = 1
            """)
            return cursor.fetchone()['count']

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize assistant
    assistant = SimplifiedManusAssistant("test_conversations.db")
    
    print("🚀 Simplified Manus AI Assistant Test")
    print("=" * 50)
    
    # Test simple message (knowledge base response)
    print("\n1. Testing simple query...")
    response1 = assistant.process_client_message(
        amocrm_contact_id=12345,
        message="Сколько стоит сплав по Чусовой?",
        use_manus=False
    )
    print(f"Response: {response1}")
    
    # Test complex message (Manus API)
    print("\n2. Testing complex query with Manus...")
    response2 = assistant.process_client_message(
        amocrm_contact_id=12345,
        message="Помогите выбрать лучший тур для семьи с детьми 8 и 12 лет на 3 дня в июне. Что включено в стоимость?"
    )
    print(f"Response: {response2}")
    
    # Check system status
    print("\n3. System status:")
    status = assistant.get_system_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # List active tasks
    print("\n4. Active Manus tasks:")
    tasks = assistant.list_active_tasks()
    for task in tasks:
        print(f"   Task {task['task_id'][:8]}... - Conversation {task['conversation_id']}")
        print(f"   Created: {task['created_at']}")
        print(f"   URL: {task['task_url']}")
    
    print("\n✅ Test completed successfully!")

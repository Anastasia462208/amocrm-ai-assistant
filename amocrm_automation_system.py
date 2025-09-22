#!/usr/bin/env python3
"""
AmoCRM Automation System for River Rafting Tourism Company
Uses browser automation for chat responses and Manus API for data storage
Handles 20 parallel conversations with full automation
"""

import time
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from database_manager import DatabaseManager
from context_manager import ConversationContextManager
import requests
import re

class AmoCRMAutomationSystem:
    def __init__(self, amocrm_url: str, login: str, password: str):
        self.amocrm_url = amocrm_url
        self.login = login
        self.password = password
        
        # Initialize components
        self.db = DatabaseManager("amocrm_conversations.db")
        self.context_manager = ConversationContextManager(self.db)
        
        # Browser setup
        self.driver = None
        self.is_logged_in = False
        self.monitoring_active = False
        
        # Response templates
        self.response_templates = self._load_response_templates()
        
        # Manus API for data storage
        self.manus_api_key = self.db.get_config('manus_api_key')
        self.manus_base_url = "https://api.manus.im/v1/tasks"
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load response templates for different scenarios"""
        return {
            'greeting': [
                "Здравствуйте! Добро пожаловать в турагентство 'Все на сплав'! 🚣‍♂️",
                "Привет! Рады видеть вас в нашем агентстве речных сплавов! 😊",
                "Добро пожаловать! Мы организуем незабываемые сплавы по рекам Урала! 🏞️"
            ],
            'tours_info': [
                """🚣‍♂️ Наши основные направления:

📍 **Река Чусовая** - семейные сплавы 2-5 дней
💰 От 15,000 руб/чел
👨‍👩‍👧‍👦 Подходит для начинающих и семей с детьми

📍 **Река Серга** - однодневные сплавы  
💰 От 3,500 руб/чел
⭐ Идеально для первого опыта

Что вас интересует больше?""",
                
                """🏞️ Популярные туры:

🌟 **Чусовая "Семейный"** (3 дня)
- Спокойные пороги
- Питание и снаряжение включено
- Цена: 18,000 руб/чел

🌟 **Серга "Знакомство"** (1 день)  
- Для новичков
- Инструктаж и сопровождение
- Цена: 3,500 руб/чел

Хотите узнать подробности?"""
            ],
            'prices': [
                """💰 **Актуальные цены на сплавы:**

🚣‍♂️ **Чусовая:**
• 2 дня - от 15,000 руб
• 3 дня - от 18,000 руб  
• 5 дней - от 25,000 руб

🚣‍♀️ **Серга:**
• 1 день - от 3,500 руб

В стоимость включено: снаряжение, питание, инструктор, трансфер.

Интересует конкретный тур?""",
                
                """📋 **Что включено в стоимость:**

✅ Рафт и весла
✅ Спасательные жилеты
✅ Гермомешки
✅ Трехразовое питание
✅ Опытный инструктор
✅ Трансфер от/до города
✅ Страховка

Дополнительно оплачивается только личное снаряжение (по желанию).

Есть вопросы по программе?"""
            ],
            'booking': [
                """📝 **Для бронирования нужно:**

1️⃣ Выбрать тур и даты
2️⃣ Указать количество участников
3️⃣ Внести предоплату 30%
4️⃣ Получить подтверждение

🔗 Заполните форму: [ссылка на форму]
📞 Или звоните: +7-XXX-XXX-XX-XX

Готовы забронировать?""",
                
                """✨ **Бронирование за 3 шага:**

🎯 Шаг 1: Выберите тур
🗓️ Шаг 2: Укажите даты  
👥 Шаг 3: Количество человек

💳 Предоплата: 30% от стоимости
⏰ Бронь действует 3 дня

Какой тур вас интересует?"""
            ],
            'equipment': [
                """🎒 **Что взять с собой:**

👕 **Одежда:**
• Быстросохнущая одежда
• Сменный комплект
• Теплая кофта
• Дождевик

👟 **Обувь:**
• Кроссовки (можно старые)
• Сандалии для лагеря

🧴 **Личное:**
• Солнцезащитный крем
• Головной убор
• Личная аптечка

Снаряжение для сплава предоставляем мы!""",
                
                """⚡ **Что НЕ нужно брать:**

❌ Спасжилеты (выдаем)
❌ Рафт и весла (наши)
❌ Палатки (включены)
❌ Котлы и горелки (есть)

✅ **Берите только:**
• Личные вещи
• Сменную одежду  
• Средства гигиены
• Хорошее настроение! 😊

Остальное - наша забота!"""
            ],
            'safety': [
                """🛡️ **Безопасность - наш приоритет:**

👨‍🏫 Опытные инструкторы (стаж 5+ лет)
🦺 Сертифицированные спасжилеты
📡 Спутниковая связь на маршруте
🏥 Аптечка и обученный медик
🚁 Связь со службой спасения

📋 Все участники проходят инструктаж по безопасности.

Есть медицинские ограничения?""",
                
                """⚠️ **Требования к участникам:**

✅ Возраст: от 8 лет
✅ Умение плавать обязательно
✅ Отсутствие серьезных заболеваний
✅ Физическая подготовка: базовая

❗ **Противопоказания:**
• Беременность
• Сердечно-сосудистые заболевания
• Недавние травмы

Все в порядке со здоровьем?"""
            ],
            'dates': [
                """📅 **Ближайшие даты:**

🌞 **Июнь 2024:**
• 15-17 июня (Чусовая, 3 дня)
• 22-24 июня (Чусовая, 3 дня)  
• 29 июня (Серга, 1 день)

🌞 **Июль 2024:**
• 6-8 июля (Чусовая, 3 дня)
• 13-15 июля (Чусовая, 3 дня)
• 20 июля (Серга, 1 день)

Какие даты вам подходят?""",
                
                """🗓️ **Как выбрать даты:**

🌡️ **Лучшее время:** май-сентябрь
💧 **Уровень воды:** оптимальный в июне-июле
🌤️ **Погода:** стабильная с июня

📞 Актуальные даты уточняйте по телефону
🔄 Возможна организация в удобные вам даты (группа от 6 человек)

Когда планируете поехать?"""
            ],
            'fallback': [
                "Спасибо за вопрос! Сейчас уточню информацию и отвечу подробно.",
                "Интересный вопрос! Позвольте подготовить для вас детальный ответ.",
                "Хороший вопрос! Сейчас найду всю необходимую информацию."
            ]
        }
    
    def initialize_browser(self):
        """Initialize Chrome browser with options"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        # Remove headless for debugging
        # chrome_options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.logger.info("Browser initialized")
    
    def login_to_amocrm(self) -> bool:
        """Login to AmoCRM"""
        try:
            if not self.driver:
                self.initialize_browser()
            
            self.driver.get(self.amocrm_url)
            time.sleep(3)
            
            # Find and fill login form
            login_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "USER_LOGIN"))
            )
            password_field = self.driver.find_element(By.NAME, "USER_HASH")
            
            login_field.clear()
            login_field.send_keys(self.login)
            
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Submit form
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for successful login
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".pipeline-leads"))
            )
            
            self.is_logged_in = True
            self.logger.info("Successfully logged in to AmoCRM")
            return True
            
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False
    
    def monitor_chats(self):
        """Monitor chats for new messages"""
        if not self.is_logged_in:
            if not self.login_to_amocrm():
                return
        
        self.monitoring_active = True
        self.logger.info("Starting chat monitoring...")
        
        while self.monitoring_active:
            try:
                # Navigate to chats section
                self._navigate_to_chats()
                
                # Check for new messages
                new_messages = self._check_for_new_messages()
                
                # Process each new message
                for message_data in new_messages:
                    self._process_new_message(message_data)
                
                # Wait before next check
                time.sleep(10)
                
            except Exception as e:
                self.logger.error(f"Error in chat monitoring: {e}")
                time.sleep(30)  # Wait longer on error
    
    def _navigate_to_chats(self):
        """Navigate to chats section in AmoCRM"""
        try:
            # Look for chat/messages section
            chat_section = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-entity='chats'], .chats-section, .messages-section"))
            )
            chat_section.click()
            time.sleep(2)
        except:
            # If direct navigation fails, try alternative methods
            self.logger.warning("Could not find chat section, trying alternative navigation")
    
    def _check_for_new_messages(self) -> List[Dict]:
        """Check for new unread messages"""
        new_messages = []
        
        try:
            # Look for unread message indicators
            unread_indicators = self.driver.find_elements(
                By.CSS_SELECTOR, 
                ".unread-message, .new-message, .message-unread, [data-unread='true']"
            )
            
            for indicator in unread_indicators:
                try:
                    # Extract message data
                    message_element = indicator.find_element(By.XPATH, "./ancestor::*[contains(@class, 'message')]")
                    
                    message_text = self._extract_message_text(message_element)
                    contact_id = self._extract_contact_id(message_element)
                    lead_id = self._extract_lead_id(message_element)
                    
                    if message_text and contact_id:
                        new_messages.append({
                            'contact_id': contact_id,
                            'lead_id': lead_id,
                            'message': message_text,
                            'element': message_element,
                            'timestamp': datetime.now()
                        })
                        
                except Exception as e:
                    self.logger.error(f"Error extracting message data: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error checking for new messages: {e}")
        
        return new_messages
    
    def _extract_message_text(self, message_element) -> Optional[str]:
        """Extract message text from element"""
        try:
            text_selectors = [
                ".message-text",
                ".message-content", 
                ".chat-message-text",
                "[data-message-text]"
            ]
            
            for selector in text_selectors:
                try:
                    text_element = message_element.find_element(By.CSS_SELECTOR, selector)
                    return text_element.text.strip()
                except:
                    continue
            
            # Fallback: get all text from message element
            return message_element.text.strip()
            
        except:
            return None
    
    def _extract_contact_id(self, message_element) -> Optional[int]:
        """Extract contact ID from message element"""
        try:
            # Look for data attributes with contact ID
            contact_attrs = ['data-contact-id', 'data-contact', 'data-client-id']
            
            for attr in contact_attrs:
                contact_id = message_element.get_attribute(attr)
                if contact_id:
                    return int(contact_id)
            
            # Try to extract from URL or other sources
            # This would need to be customized based on actual AmoCRM structure
            return 12345  # Placeholder
            
        except:
            return None
    
    def _extract_lead_id(self, message_element) -> Optional[int]:
        """Extract lead ID from message element"""
        try:
            # Similar to contact ID extraction
            lead_attrs = ['data-lead-id', 'data-lead', 'data-entity-id']
            
            for attr in lead_attrs:
                lead_id = message_element.get_attribute(attr)
                if lead_id:
                    return int(lead_id)
            
            return None
            
        except:
            return None
    
    def _process_new_message(self, message_data: Dict):
        """Process new message and generate response"""
        try:
            contact_id = message_data['contact_id']
            message_text = message_data['message']
            lead_id = message_data.get('lead_id')
            
            self.logger.info(f"Processing message from contact {contact_id}: {message_text[:50]}...")
            
            # Store message in database
            client_id = self.db.get_or_create_client(contact_id)
            conversation_id = self.db.get_or_create_conversation(client_id, lead_id)
            
            # Add client message
            self.db.add_message(conversation_id, "client", message_text)
            
            # Update conversation context
            self.context_manager.update_conversation_context(
                conversation_id, message_text, 'client'
            )
            
            # Generate response
            response = self._generate_response(conversation_id, message_text)
            
            # Send response
            if response:
                success = self._send_response(message_data['element'], response)
                
                if success:
                    # Store assistant response
                    self.db.add_message(conversation_id, "assistant", response)
                    self.logger.info(f"Response sent to contact {contact_id}")
                    
                    # Store conversation in Manus for long-term memory
                    self._store_conversation_in_manus(conversation_id)
                else:
                    self.logger.error(f"Failed to send response to contact {contact_id}")
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    def _generate_response(self, conversation_id: int, message: str) -> str:
        """Generate appropriate response based on message content"""
        
        # Analyze message intent
        intents = self.context_manager.analyze_message_intent(message)
        entities = self.context_manager.extract_entities(message)
        
        # Get conversation context
        context = self.context_manager.get_conversation_context_summary(conversation_id)
        
        # Determine response category
        response_category = self._determine_response_category(message, intents, context)
        
        # Get appropriate template
        if response_category in self.response_templates:
            templates = self.response_templates[response_category]
            # For now, use first template. Could implement rotation or selection logic
            response = templates[0]
        else:
            response = self.response_templates['fallback'][0]
        
        # Personalize response if client name is known
        client_name = context.get('client_info', {}).get('name')
        if client_name:
            response = f"{client_name}, {response.lower()}"
        
        return response
    
    def _determine_response_category(self, message: str, intents: List[str], context: Dict) -> str:
        """Determine which response category to use"""
        
        message_lower = message.lower()
        
        # Greeting detection
        greeting_words = ['привет', 'здравствуйте', 'добрый день', 'добрый вечер', 'здравствуй']
        if any(word in message_lower for word in greeting_words):
            return 'greeting'
        
        # Intent-based categorization
        if 'price_inquiry' in intents:
            return 'prices'
        elif 'booking_inquiry' in intents:
            return 'booking'
        elif 'equipment_inquiry' in intents:
            return 'equipment'
        elif 'safety_inquiry' in intents:
            return 'safety'
        elif 'date_inquiry' in intents:
            return 'dates'
        elif 'tour_comparison' in intents or any(word in message_lower for word in ['тур', 'сплав', 'чусовая', 'серга']):
            return 'tours_info'
        
        # Keyword-based fallback
        if any(word in message_lower for word in ['цена', 'стоимость', 'сколько']):
            return 'prices'
        elif any(word in message_lower for word in ['забронировать', 'заказать', 'бронирование']):
            return 'booking'
        elif any(word in message_lower for word in ['снаряжение', 'что взять', 'экипировка']):
            return 'equipment'
        elif any(word in message_lower for word in ['безопасность', 'опасно', 'риски']):
            return 'safety'
        elif any(word in message_lower for word in ['когда', 'даты', 'расписание']):
            return 'dates'
        elif any(word in message_lower for word in ['тур', 'сплав', 'поездка']):
            return 'tours_info'
        
        return 'fallback'
    
    def _send_response(self, message_element, response: str) -> bool:
        """Send response to chat"""
        try:
            # Find chat input field near the message
            chat_input = self._find_chat_input(message_element)
            
            if chat_input:
                # Clear and type response
                chat_input.clear()
                chat_input.send_keys(response)
                
                # Send message (usually Enter key or send button)
                chat_input.send_keys(Keys.ENTER)
                
                # Alternative: look for send button
                try:
                    send_button = self.driver.find_element(
                        By.CSS_SELECTOR, 
                        ".send-button, .chat-send, [data-send], button[type='submit']"
                    )
                    send_button.click()
                except:
                    pass  # Enter key should work
                
                time.sleep(1)
                return True
            else:
                self.logger.error("Could not find chat input field")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending response: {e}")
            return False
    
    def _find_chat_input(self, message_element) -> Optional[object]:
        """Find chat input field"""
        try:
            # Common selectors for chat input
            input_selectors = [
                "textarea[placeholder*='сообщение']",
                "input[placeholder*='сообщение']", 
                ".chat-input textarea",
                ".message-input textarea",
                ".chat-textarea",
                "textarea.form-control",
                "[data-chat-input]"
            ]
            
            for selector in input_selectors:
                try:
                    input_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if input_field.is_displayed() and input_field.is_enabled():
                        return input_field
                except:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding chat input: {e}")
            return None
    
    def _store_conversation_in_manus(self, conversation_id: int):
        """Store conversation summary in Manus for long-term memory"""
        try:
            # Get conversation context
            context = self.context_manager.get_conversation_context_summary(conversation_id)
            messages = self.db.get_conversation_context(conversation_id)
            
            # Create summary for Manus
            summary_prompt = f"""
Сохрани информацию о диалоге с клиентом турагентства:

Клиент: {context.get('client_info', {}).get('name', 'Неизвестно')}
Контакт ID: {context.get('conversation_id')}
Состояние диалога: {context.get('conversation_state')}
Обсуждаемые темы: {', '.join(context.get('conversation_analysis', {}).get('topics_discussed', []))}
Готовность к бронированию: {context.get('conversation_analysis', {}).get('booking_readiness_score', 0)}/10

Последние сообщения:
"""
            
            for msg in messages[-5:]:
                role = "Клиент" if msg['sender_type'] == 'client' else "Ассистент"
                summary_prompt += f"{role}: {msg['content']}\n"
            
            summary_prompt += "\nСохрани эту информацию для дальнейшего использования в работе с клиентом."
            
            # Send to Manus
            self._send_to_manus(summary_prompt, f"conversation_{conversation_id}")
            
        except Exception as e:
            self.logger.error(f"Error storing conversation in Manus: {e}")
    
    def _send_to_manus(self, prompt: str, task_type: str) -> Optional[str]:
        """Send data to Manus API for storage"""
        try:
            headers = {
                "API_KEY": self.manus_api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": prompt,
                "mode": "fast",
                "attachments": []
            }
            
            response = requests.post(
                self.manus_base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                task_id = result.get('task_id')
                self.logger.info(f"Data stored in Manus: {task_id}")
                return task_id
            else:
                self.logger.error(f"Manus API error: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error sending to Manus: {e}")
            return None
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        return {
            'browser_active': self.driver is not None,
            'logged_in': self.is_logged_in,
            'monitoring_active': self.monitoring_active,
            'active_conversations': self.db.get_active_conversations_count(),
            'total_messages_today': self._count_messages_today()
        }
    
    def _count_messages_today(self) -> int:
        """Count messages processed today"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) as count
                FROM messages
                WHERE DATE(timestamp) = DATE('now')
            """)
            return cursor.fetchone()['count']
    
    def stop_monitoring(self):
        """Stop chat monitoring"""
        self.monitoring_active = False
        self.logger.info("Chat monitoring stopped")
    
    def shutdown(self):
        """Shutdown the system"""
        self.stop_monitoring()
        
        if self.driver:
            self.driver.quit()
            self.driver = None
        
        self.logger.info("AmoCRM Automation System shutdown complete")

# Example usage and configuration
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Configuration
    AMOCRM_URL = "https://your-domain.amocrm.ru"  # Replace with actual URL
    LOGIN = "your-login"  # Replace with actual login
    PASSWORD = "your-password"  # Replace with actual password
    
    # Initialize system
    automation = AmoCRMAutomationSystem(AMOCRM_URL, LOGIN, PASSWORD)
    
    try:
        print("🚀 Starting AmoCRM Automation System...")
        print("=" * 50)
        
        # Initialize browser and login
        if automation.login_to_amocrm():
            print("✅ Successfully logged in to AmoCRM")
            
            # Start monitoring in a separate thread
            monitoring_thread = threading.Thread(target=automation.monitor_chats, daemon=True)
            monitoring_thread.start()
            
            print("🔍 Chat monitoring started...")
            print("📊 System status:")
            
            # Monitor system status
            while True:
                status = automation.get_system_status()
                print(f"   Active conversations: {status['active_conversations']}")
                print(f"   Messages today: {status['total_messages_today']}")
                print(f"   Monitoring: {'✅' if status['monitoring_active'] else '❌'}")
                
                time.sleep(60)  # Update every minute
                
        else:
            print("❌ Failed to login to AmoCRM")
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        automation.shutdown()
        print("✅ Shutdown complete")
    except Exception as e:
        print(f"❌ Error: {e}")
        automation.shutdown()

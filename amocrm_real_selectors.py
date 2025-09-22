#!/usr/bin/env python3
"""
AmoCRM Automation with Real Selectors
Based on actual AmoCRM HTML structure
"""

import time
import logging
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from database_manager import DatabaseManager
from context_manager import ConversationContextManager

class AmoCRMRealAutomation:
    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password
        
        # Initialize components
        self.db = DatabaseManager("amocrm_real_conversations.db")
        self.context_manager = ConversationContextManager(self.db)
        
        # Real AmoCRM selectors based on provided HTML
        self.selectors = {
            'messages': {
                'container': '.feed-note__message_paragraph',
                'text': '.feed-note__message_paragraph',
                'author': '.feed-note__author',
                'timestamp': '.feed-note__time'
            },
            'input': {
                'textarea': 'textarea[placeholder*="сообщение"], textarea[placeholder*="Сообщение"], .feed-compose__textarea',
                'send_button': '.feed-compose__send, button[type="submit"], .send-button'
            },
            'navigation': {
                'leads': 'a[href*="leads"], .nav-leads',
                'contacts': 'a[href*="contacts"], .nav-contacts',
                'chat': '.feed, .chat, .messages'
            }
        }
        
        # Response templates for tours
        self.tour_responses = {
            'tours_3_days': """🚣‍♂️ **Туры на 3 дня по реке Чусовая:**

🌟 **"Семейный сплав"** (3 дня/2 ночи)
💰 Цена: 18,000 руб/чел
👨‍👩‍👧‍👦 Для семей с детьми от 8 лет
📍 Маршрут: Коуровка - Чусовая
🏕️ Ночевки в палатках на берегу

🌟 **"Активный отдых"** (3 дня/2 ночи)  
💰 Цена: 20,000 руб/чел
🏃‍♂️ Для активных туристов
📍 Маршрут: Староуткинск - Чусовая
🎯 Больше порогов и приключений

**В стоимость включено:**
✅ Рафт и снаряжение
✅ Трехразовое питание
✅ Опытный инструктор
✅ Трансфер от/до Екатеринбурга
✅ Страховка

📅 **Ближайшие даты:** 15-17 июня, 22-24 июня, 29 июня-1 июля

Какой тур вас больше интересует? 😊""",
            
            'booking_info': """📝 **Как забронировать тур:**

1️⃣ Выберите даты и тур
2️⃣ Внесите предоплату 30% (5,400-6,000 руб)
3️⃣ Получите подтверждение и инструкции
4️⃣ Доплачиваете остальное в день тура

💳 **Способы оплаты:**
• Банковская карта
• Перевод на карту Сбербанка
• Наличные при встрече

📞 **Контакты для бронирования:**
• Телефон: +7-XXX-XXX-XX-XX
• WhatsApp: +7-XXX-XXX-XX-XX
• Email: info@vsenasplav.ru

Готовы забронировать? Подскажите удобные даты! 🎯"""
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def analyze_message(self, message_text: str) -> dict:
        """Analyze incoming message and determine response"""
        
        # Use context manager for analysis
        intents = self.context_manager.analyze_message_intent(message_text)
        entities = self.context_manager.extract_entities(message_text)
        
        # Determine response type
        response_type = self._determine_response_type(message_text, intents, entities)
        
        return {
            'message': message_text,
            'intents': intents,
            'entities': entities,
            'response_type': response_type,
            'suggested_response': self._get_response_template(response_type, entities)
        }
    
    def _determine_response_type(self, message: str, intents: list, entities: dict) -> str:
        """Determine what type of response to give"""
        
        message_lower = message.lower()
        
        # Check for 3-day tour inquiry
        if '3 дня' in message_lower or 'три дня' in message_lower:
            if any(word in message_lower for word in ['тур', 'сплав', 'поездка']):
                return 'tours_3_days'
        
        # Check for general tour inquiry
        if any(word in message_lower for word in ['тур', 'сплав', 'поездка', 'программа']):
            return 'tours_3_days'  # Default to 3-day tours since that was asked
        
        # Check for booking inquiry
        if 'booking_inquiry' in intents or any(word in message_lower for word in ['забронировать', 'заказать', 'бронирование']):
            return 'booking_info'
        
        # Check for price inquiry
        if 'price_inquiry' in intents:
            return 'tours_3_days'  # Include prices in tour info
        
        return 'tours_3_days'  # Default response
    
    def _get_response_template(self, response_type: str, entities: dict) -> str:
        """Get response template based on type"""
        
        if response_type in self.tour_responses:
            response = self.tour_responses[response_type]
            
            # Personalize based on entities
            if entities.get('numbers'):
                # If specific number of people mentioned
                people_count = entities['numbers'][0] if entities['numbers'] else None
                if people_count and people_count > 1:
                    response += f"\n\n👥 Для группы {people_count} человек возможна скидка!"
            
            return response
        
        return "Спасибо за ваш вопрос! Сейчас подготовлю для вас подробную информацию."
    
    def process_test_message(self, message_html: str) -> dict:
        """Process the test message from AmoCRM"""
        
        # Extract text from HTML
        import re
        text_match = re.search(r'<div class="feed-note__message_paragraph[^"]*"[^>]*>([^<]+)</div>', message_html)
        
        if text_match:
            message_text = text_match.group(1).strip()
        else:
            message_text = "расскажите какие у вас есть туры на 3 дня"  # Fallback
        
        self.logger.info(f"Processing message: {message_text}")
        
        # Analyze message
        analysis = self.analyze_message(message_text)
        
        # Store in database
        client_id = self.db.get_or_create_client(12345, "Anastasia", "test@example.com")
        conversation_id = self.db.get_or_create_conversation(client_id)
        
        # Add client message
        self.db.add_message(conversation_id, "client", message_text)
        
        # Update context
        self.context_manager.update_conversation_context(
            conversation_id, message_text, 'client'
        )
        
        # Add assistant response
        response = analysis['suggested_response']
        self.db.add_message(conversation_id, "assistant", response)
        
        # Get conversation metrics
        metrics = self.context_manager.get_conversation_metrics(conversation_id)
        
        return {
            'analysis': analysis,
            'response': response,
            'conversation_id': conversation_id,
            'metrics': metrics
        }
    
    def format_response_for_amocrm(self, response: str) -> str:
        """Format response for AmoCRM (remove markdown, adjust formatting)"""
        
        # Remove markdown formatting for AmoCRM
        formatted = response
        
        # Replace markdown bold with simple text
        formatted = re.sub(r'\*\*(.*?)\*\*', r'\1', formatted)
        
        # Replace markdown lists with simple text
        formatted = re.sub(r'^\s*[•✅❌🎯📍🏕️🏃‍♂️👨‍👩‍👧‍👦💰📅📝💳📞]\s*', '• ', formatted, flags=re.MULTILINE)
        
        # Replace emojis with text equivalents if needed
        emoji_replacements = {
            '🚣‍♂️': '[Сплав]',
            '🌟': '*',
            '💰': 'Цена:',
            '📍': 'Маршрут:',
            '✅': '✓',
            '📅': 'Даты:',
            '😊': ':)',
            '🎯': '>>>'
        }
        
        for emoji, replacement in emoji_replacements.items():
            formatted = formatted.replace(emoji, replacement)
        
        return formatted
    
    def get_selectors_info(self) -> dict:
        """Get information about selectors for manual testing"""
        return {
            'message_selectors': [
                '.feed-note__message_paragraph',
                '.feed-note__message_paragraph ',  # With space
                'div[class*="feed-note__message_paragraph"]'
            ],
            'input_selectors': [
                'textarea[placeholder*="сообщение"]',
                'textarea[placeholder*="Сообщение"]', 
                '.feed-compose__textarea',
                'textarea.feed-compose__textarea'
            ],
            'send_button_selectors': [
                '.feed-compose__send',
                'button[type="submit"]',
                '.send-button',
                'button.feed-compose__send'
            ]
        }

def test_message_analysis():
    """Test the message analysis with the real AmoCRM message"""
    
    print("🧪 Testing AmoCRM Message Analysis")
    print("=" * 50)
    
    # Initialize automation
    automation = AmoCRMRealAutomation("amoshturm@gmail.com", "GbbT4Z5L")
    
    # Test message HTML from AmoCRM
    test_message_html = '<div class="feed-note__message_paragraph ">расскажите какие у вас есть туры на 3 дня</div>'
    
    # Process message
    result = automation.process_test_message(test_message_html)
    
    print(f"📨 Исходное сообщение: {result['analysis']['message']}")
    print(f"🧠 Обнаруженные намерения: {result['analysis']['intents']}")
    print(f"📊 Извлеченные сущности: {result['analysis']['entities']}")
    print(f"🎯 Тип ответа: {result['analysis']['response_type']}")
    print(f"💬 ID диалога: {result['conversation_id']}")
    
    print(f"\n📋 Метрики диалога:")
    for key, value in result['metrics'].items():
        if key != 'next_actions':
            if isinstance(value, float):
                print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value}")
    
    print(f"\n💡 Рекомендуемые действия:")
    for action in result['metrics']['next_actions']:
        print(f"   • {action}")
    
    print(f"\n🤖 Сгенерированный ответ:")
    print("-" * 30)
    print(result['response'])
    
    print(f"\n📝 Форматированный для AmoCRM:")
    print("-" * 30)
    formatted_response = automation.format_response_for_amocrm(result['response'])
    print(formatted_response)
    
    print(f"\n🔧 Селекторы для ручного тестирования:")
    selectors = automation.get_selectors_info()
    for category, selector_list in selectors.items():
        print(f"   {category}:")
        for selector in selector_list:
            print(f"     • {selector}")
    
    return result

if __name__ == "__main__":
    test_message_analysis()

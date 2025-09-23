#!/usr/bin/env python3
"""
Упрощенный тест веб-хука с базой данных
"""

from database_manager import DatabaseManager
import json
from datetime import datetime

def test_database_integration():
    """Тестирует интеграцию с базой данных"""
    
    print("🧪 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ С БАЗОЙ ДАННЫХ")
    print("=" * 60)
    
    # Инициализируем базу данных
    db = DatabaseManager('conversations.db')
    
    # Тест 1: Сообщение от клиента 12345
    print("\\n📝 Тест 1: Первое сообщение от клиента 12345")
    
    lead_id = 12345
    message_text = "Здравствуйте! Интересует сплав по Чусовой"
    
    # Создаем клиента
    client_id = db.get_or_create_client(
        amocrm_contact_id=lead_id,
        name=f"Клиент из сделки {lead_id}"
    )
    print(f"👤 Клиент создан/найден: ID {client_id}")
    
    # Создаем разговор
    conversation_id = db.get_or_create_conversation(
        client_id=client_id,
        amocrm_lead_id=lead_id
    )
    print(f"💬 Разговор создан/найден: ID {conversation_id}")
    
    # Добавляем сообщение
    message_id = db.add_message(
        conversation_id=conversation_id,
        sender_type='client',
        content=message_text,
        message_type='text',
        metadata={
            'amocrm_lead_id': lead_id,
            'amocrm_timestamp': int(datetime.now().timestamp()),
            'source': 'test'
        }
    )
    print(f"📝 Сообщение сохранено: ID {message_id}")
    
    # Тест 2: Второе сообщение от того же клиента
    print("\\n📝 Тест 2: Второе сообщение от клиента 12345")
    
    message_text2 = "Какие у вас есть туры на 3 дня?"
    message_id2 = db.add_message(
        conversation_id=conversation_id,
        sender_type='client',
        content=message_text2,
        message_type='text',
        metadata={
            'amocrm_lead_id': lead_id,
            'amocrm_timestamp': int(datetime.now().timestamp()),
            'source': 'test'
        }
    )
    print(f"📝 Второе сообщение сохранено: ID {message_id2}")
    
    # Тест 3: Ответ ассистента
    print("\\n🤖 Тест 3: Ответ ассистента")
    
    response_text = """Спасибо за интерес к нашим турам! 😊

По турам на 3 дня у нас есть два отличных варианта:

🌟 "Семейный сплав" (3 дня/2 ночи) - 18,000 руб/чел
🌟 "Активный отдых" (3 дня/2 ночи) - 20,000 руб/чел

Какой вариант вас больше интересует?"""
    
    response_id = db.add_message(
        conversation_id=conversation_id,
        sender_type='assistant',
        content=response_text,
        message_type='text',
        metadata={
            'amocrm_lead_id': lead_id,
            'source': 'ai_response'
        }
    )
    print(f"🤖 Ответ ассистента сохранен: ID {response_id}")
    
    # Тест 4: Сообщение от другого клиента
    print("\\n📝 Тест 4: Сообщение от клиента 67890")
    
    lead_id2 = 67890
    client_id2 = db.get_or_create_client(
        amocrm_contact_id=lead_id2,
        name=f"Клиент из сделки {lead_id2}"
    )
    
    conversation_id2 = db.get_or_create_conversation(
        client_id=client_id2,
        amocrm_lead_id=lead_id2
    )
    
    message_id3 = db.add_message(
        conversation_id=conversation_id2,
        sender_type='client',
        content="Сколько стоят ваши туры?",
        message_type='text',
        metadata={
            'amocrm_lead_id': lead_id2,
            'amocrm_timestamp': int(datetime.now().timestamp()),
            'source': 'test'
        }
    )
    print(f"📝 Сообщение от второго клиента: ID {message_id3}")
    
    # Тест 5: Проверяем историю первого клиента
    print("\\n📋 Тест 5: История переписки клиента 12345")
    
    history = db.get_conversation_context(conversation_id, limit=10)
    print(f"Найдено {len(history)} сообщений:")
    
    for i, msg in enumerate(history, 1):
        sender_icon = "👤" if msg['sender_type'] == 'client' else "🤖"
        print(f"  {i}. {sender_icon} {msg['sender_type']}: {msg['content'][:50]}...")
    
    print("\\n✅ Все тесты завершены успешно!")
    print("\\nДля просмотра полной базы данных запустите:")
    print("python3 view_database.py")

if __name__ == '__main__':
    test_database_integration()

#!/usr/bin/env python3
"""
Тестирование веб-хука с интеграцией базы данных
"""

import requests
import time
import urllib.parse
from datetime import datetime

# Конфигурация
WEBHOOK_URL = "http://127.0.0.1:8000"

def send_test_message(lead_id, message_text):
    """Отправляет тестовое сообщение на веб-хук"""
    
    # Формируем данные как от amoCRM
    timestamp = int(time.time())
    data = {
        'message[add][0][text]': message_text,
        'message[add][0][entity_id]': f'lead_{lead_id}',
        'message[add][0][entity_type]': 'lead',
        'message[add][0][created_at]': str(timestamp)
    }
    
    # Кодируем данные как URL-encoded
    encoded_data = urllib.parse.urlencode(data)
    
    print(f"📤 Отправляем сообщение для сделки {lead_id}:")
    print(f"💬 Текст: '{message_text}'")
    print(f"🕐 Время: {datetime.fromtimestamp(timestamp)}")
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            data=encoded_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Сообщение отправлено успешно")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при отправке: {e}")
    
    print("-" * 50)

def run_tests():
    """Запускает серию тестов"""
    print("🧪 ТЕСТИРОВАНИЕ ВЕБ-ХУКА С БАЗОЙ ДАННЫХ")
    print("=" * 60)
    
    # Тест 1: Первое сообщение от клиента
    send_test_message(12345, "Здравствуйте! Интересует сплав по Чусовой")
    time.sleep(2)
    
    # Тест 2: Второе сообщение от того же клиента
    send_test_message(12345, "Какие у вас есть туры на 3 дня?")
    time.sleep(2)
    
    # Тест 3: Сообщение от другого клиента
    send_test_message(67890, "Сколько стоят ваши туры?")
    time.sleep(2)
    
    # Тест 4: Еще одно сообщение от первого клиента
    send_test_message(12345, "Какие ближайшие даты?")
    time.sleep(2)
    
    # Тест 5: Сообщение от третьего клиента
    send_test_message(11111, "Здравствуйте! Интересуют сплавы для семьи с детьми.")
    
    print("\\n✅ Все тесты отправлены!")
    print("Проверьте логи сервера и базу данных.")

if __name__ == '__main__':
    run_tests()

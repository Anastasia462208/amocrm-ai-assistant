#!/usr/bin/env python3
"""
Тестирование Webhook сервера
Имитирует отправку данных от AmoCRM
"""

import requests
import time
from urllib.parse import urlencode

def test_webhook_message(message_text, lead_id="12345"):
    """Отправляет тестовое сообщение в webhook"""
    
    # Формируем данные как от AmoCRM
    webhook_data = {
        'message[add][0][text]': message_text,
        'message[add][0][entity_id]': lead_id,
        'message[add][0][entity_type]': 'lead',
        'message[add][0][created_at]': int(time.time())
    }
    
    # Кодируем как form data (как делает AmoCRM)
    encoded_data = urlencode(webhook_data)
    
    print(f"🧪 ТЕСТ WEBHOOK")
    print(f"📥 Сообщение: '{message_text}'")
    print(f"🆔 ID сделки: {lead_id}")
    print(f"🔗 URL: http://localhost:8000")
    print()
    
    try:
        response = requests.post(
            'http://localhost:8000',
            data=encoded_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Webhook обработан успешно!")
        else:
            print(f"❌ Ошибка: {response.text}")
            
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к webhook серверу")
        print("Убедитесь, что сервер запущен на порту 8000")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    print("🚀 ТЕСТИРОВАНИЕ AmoCRM + Manus WEBHOOK")
    print("="*50)
    
    # Тестовые сообщения
    test_messages = [
        "Расскажите, какие у вас есть туры на 3 дня?",
        "Сколько стоят ваши туры?",
        "Какие у вас ближайшие даты?",
        "Здравствуйте! Интересуют сплавы для семьи с детьми."
    ]
    
    success_count = 0
    
    for i, message in enumerate(test_messages, 1):
        print(f"\\n📋 ТЕСТ {i}/{len(test_messages)}")
        print("-" * 30)
        
        success = test_webhook_message(message, f"lead_{i}")
        
        if success:
            success_count += 1
            print("✅ Тест пройден")
        else:
            print("❌ Тест провален")
        
        # Пауза между тестами
        if i < len(test_messages):
            print("⏳ Ожидание 3 секунды...")
            time.sleep(3)
    
    print("\\n" + "="*50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("="*50)
    print(f"✅ Успешных тестов: {success_count}/{len(test_messages)}")
    print(f"❌ Неудачных тестов: {len(test_messages) - success_count}/{len(test_messages)}")
    
    if success_count == len(test_messages):
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("🚀 Webhook сервер работает корректно!")
    else:
        print("⚠️ Есть проблемы с webhook сервером")
    
    print("\\n🔍 Проверьте логи сервера для деталей")

if __name__ == "__main__":
    main()

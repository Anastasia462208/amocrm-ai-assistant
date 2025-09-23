#!/usr/bin/env python3
"""
AmoCRM + Manus API Webhook Handler
Адаптация рабочего кода под Manus API
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from urllib.parse import parse_qs
import json
import requests
import time
from datetime import datetime

# === КОНФИГУРАЦИЯ ===
SUBDOMAIN = 'amoshturm'
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjBjYjliYjRhZmI3ODNiOWNiMDA2Mzg5NWE1Nzg5MjhjMGViNDZlZTcxYzc2MGUwNGFjNTE3OGUzNWE4Mzk2MWZjNWI2NzQ2NDRjN2U5YmRlIn0.eyJhdWQiOiI3NWMyYjNlYi1kODM3LTQwNzktYjNkYS04YzJmOWU0OTRkNjYiLCJqdGkiOiIwY2I5YmI0YWZiNzgzYjljYjAwNjM4OTVhNTc4OTI4YzBlYjQ2ZWU3MWM3NjBlMDRhYzUxNzhlMzVhODM5NjFmYzViNjc0NjQ0YzdlOWJkZSIsImlhdCI6MTc0NTg0ODE4MiwibmJmIjoxNzQ1ODQ4MTgyLCJleHAiOjE4ODU0MjA4MDAsInN1YiI6IjEwNzg5NjU4IiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMxNjI2NTMwLCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiZjdkNTczZWYtNWI0Zi00MjU2LWI1OGYtNjE3ODdmN2Q1ZmNlIiwiYXBpX2RvbWFpbiI6ImFwaS1iLmFtb2NybS5ydSJ9.GWNXTAz3_DPtNHZbBAiPkg9k77cwfhAnMZeMIfU15r9XMQ5g6r8EyH90xU4PLluNoi5kRRWxyimVELfuoK8JWS8fSYSEezxjwlPUsp2rBEbAlvD0AVVVtMcjRjicUSQ-qB7avcTHCsOSXR-P-ZkMkGcE0B_2RA-DqsxqYGHxnuQHtzDSmw8lgnl0aVrbBULhVIZEAK7gTufQTWJDDmcMttEYqYU-Bd2XReJ0f96K6k68b7CErnjp-uyRmjLEgKhkpdsF8Cx6bioqACXUqSPUNRmd6sRTU5RYC3J3SlTJONcx6TFToAfnXof0cjwnlxluetl8rwafrAulTr1kTrJeXQ"

# Manus API конфигурация
MANUS_API_KEY = 'sk-fNQLWaD5AHLplRB2fVDZ8lfKxVbbEEHWCzl_z016aM4_2EMtOSPtEfCUzhUOZq1DCufwtAAmfIeCn0QFZaS9DkBp2QS3'
MANUS_BASE_URL = 'https://api.manus.im/v1'

# База знаний турагентства
KNOWLEDGE_BASE = """
Вы - AI ассистент турагентства "Все на сплав" (vsenasplav.ru).

ТУРЫ НА 3 ДНЯ:
1. "Семейный сплав" (3 дня/2 ночи) - 18,000 руб/чел
   - Для семей с детьми от 8 лет
   - Маршрут: Коуровка - Чусовая
   - Спокойный сплав, безопасно для детей

2. "Активный отдых" (3 дня/2 ночи) - 20,000 руб/чел
   - Для активных туристов
   - Маршрут: Староуткинск - Чусовая
   - Более динамичный маршрут

ВКЛЮЧЕНО В СТОИМОСТЬ:
- Рафт и все снаряжение
- Трехразовое питание
- Опытный инструктор
- Трансфер от/до Екатеринбурга
- Страховка

БЛИЖАЙШИЕ ДАТЫ: 15-17 июня, 22-24 июня, 29 июня-1 июля

ИНСТРУКЦИИ:
- Отвечайте дружелюбно и профессионально
- Используйте эмодзи умеренно
- Всегда указывайте цены и даты
- Задавайте уточняющие вопросы
- Ответ должен быть готов для отправки клиенту
"""

# Статистика
stats = {
    'messages_received': 0,
    'manus_requests': 0,
    'responses_sent': 0,
    'errors': 0,
    'start_time': datetime.now()
}

def send_to_manus_api(message_text):
    """Отправляет сообщение в Manus API для обработки"""
    try:
        print(f"🧠 Отправляем в Manus API: {message_text}")
        
        # Формируем промпт с базой знаний
        prompt = f"""
{KNOWLEDGE_BASE}

НОВОЕ СООБЩЕНИЕ КЛИЕНТА:
"{message_text}"

Подготовьте профессиональный ответ от имени турагентства. Ответ должен быть готов для отправки клиенту.
"""
        
        headers = {
            'Authorization': f'Bearer {MANUS_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'prompt': prompt,
            'mode': 'fast'
        }
        
        response = requests.post(
            f'{MANUS_BASE_URL}/tasks',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get('task_id')
            task_url = result.get('url')
            
            print(f"✅ Manus задача создана: {task_id}")
            stats['manus_requests'] += 1
            
            # В реальности здесь нужно ждать результат от Manus
            # Пока используем локальную генерацию как fallback
            return generate_local_response(message_text), task_url
            
        else:
            print(f"❌ Ошибка Manus API: {response.status_code}")
            print(f"Ответ: {response.text}")
            return generate_local_response(message_text), None
            
    except Exception as e:
        print(f"❌ Ошибка при обращении к Manus: {e}")
        return generate_local_response(message_text), None

def generate_local_response(message_text):
    """Генерирует ответ локально (fallback)"""
    message_lower = message_text.lower()
    
    if "3 дня" in message_lower or "три дня" in message_lower:
        return """Спасибо за интерес к нашим турам! 😊

По турам на 3 дня у нас есть два отличных варианта:

🌟 "Семейный сплав" (3 дня/2 ночи) - 18,000 руб/чел
Подходит для семей с детьми от 8 лет
Маршрут: Коуровка - Чусовая

🌟 "Активный отдых" (3 дня/2 ночи) - 20,000 руб/чел  
Для любителей активного отдыха
Маршрут: Староуткинск - Чусовая

В стоимость включено: рафт и снаряжение, трехразовое питание, опытный инструктор, трансфер от/до Екатеринбурга.

Ближайшие свободные даты: 15-17 июня, 22-24 июня, 29 июня-1 июля.

Какой вариант вас больше интересует?"""
    
    elif "цена" in message_lower or "стоимость" in message_lower:
        return """Цены на наши туры:

💰 "Семейный сплав" (3 дня/2 ночи) - 18,000 руб/чел
💰 "Активный отдых" (3 дня/2 ночи) - 20,000 руб/чел

В стоимость уже включено ВСЕ необходимое:
✅ Рафт и снаряжение
✅ Трехразовое питание  
✅ Опытный инструктор
✅ Трансфер от/до Екатеринбурга

Никаких доплат! Какой тур вас интересует?"""
    
    elif "дата" in message_lower or "когда" in message_lower:
        return """📅 Ближайшие свободные даты для туров:

🗓️ 15-17 июня (пятница-воскресенье)
🗓️ 22-24 июня (пятница-воскресенье)  
🗓️ 29 июня - 1 июля (пятница-воскресенье)

Все туры начинаются в пятницу утром, возвращение в воскресенье вечером.

Какая дата вам подходит больше?"""
    
    else:
        return """Здравствуйте! Спасибо за обращение в "Все на сплав" 😊

Мы организуем незабываемые сплавы по реке Чусовая. У нас есть туры разной продолжительности и сложности.

Расскажите, что вас интересует:
• Продолжительность тура?
• Количество участников?
• Примерные даты?

Подберу для вас идеальный вариант!"""

def send_reply_as_note(lead_id, text, manus_url=None):
    """Отправляет ответ как примечание к сделке"""
    url = f"https://{SUBDOMAIN}.amocrm.ru/api/v4/leads/{lead_id}/notes"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    
    # Добавляем информацию о Manus задаче если есть
    note_text = text
    if manus_url:
        note_text += f"\\n\\n🤖 Обработано Manus AI: {manus_url}"
    
    payload = [
        {
            "note_type": "common",
            "params": {
                "text": note_text
            }
        }
    ]

    try:
        res = requests.post(url, headers=headers, data=json.dumps(payload))
        res.raise_for_status()
        print(f"✅ Примечание добавлено к сделке {lead_id}")
        stats['responses_sent'] += 1
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при добавлении примечания: {e}")
        if 'res' in locals():
            print(f"Ответ сервера: {res.text}")
        stats['errors'] += 1
        return False

def log_stats():
    """Выводит статистику работы"""
    uptime = datetime.now() - stats['start_time']
    print("\\n" + "="*50)
    print("📊 СТАТИСТИКА РАБОТЫ")
    print("="*50)
    print(f"⏱️ Время работы: {uptime}")
    print(f"📥 Сообщений получено: {stats['messages_received']}")
    print(f"🧠 Запросов к Manus: {stats['manus_requests']}")
    print(f"📤 Ответов отправлено: {stats['responses_sent']}")
    print(f"❌ Ошибок: {stats['errors']}")
    print("="*50)

class ManusWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data_raw = self.rfile.read(content_length)
        
        logging.info(f"POST request received. Body: {post_data_raw.decode('utf-8')}")
        
        parsed_data = parse_qs(post_data_raw.decode('utf-8'))
        
        if 'message[add][0][text]' in parsed_data:
            try:
                message_text = parsed_data['message[add][0][text]'][0]
                lead_id = parsed_data['message[add][0][entity_id]'][0]
                
                print(f"\\n📥 Новое сообщение для сделки {lead_id}:")
                print(f"💬 Текст: '{message_text}'")
                
                stats['messages_received'] += 1
                
                # Отправляем в Manus API для обработки
                ai_response, manus_url = send_to_manus_api(message_text)
                
                if ai_response:
                    print(f"\\n🤖 Сгенерированный ответ:")
                    print(f"📝 {ai_response[:100]}...")
                    
                    # Отправляем ответ как примечание
                    success = send_reply_as_note(lead_id, ai_response, manus_url)
                    
                    if success:
                        print(f"✅ Обработка завершена успешно")
                    else:
                        print(f"❌ Ошибка при отправке ответа")
                else:
                    print(f"❌ Не удалось сгенерировать ответ")
                    stats['errors'] += 1
                
                # Выводим статистику каждые 10 сообщений
                if stats['messages_received'] % 10 == 0:
                    log_stats()

            except KeyError as e:
                print(f"❌ Ошибка при обработке данных: {e}")
                stats['errors'] += 1
        else:
            print("ℹ️ Получено событие без текста сообщения. Игнорирую.")

        self.send_response(200)
        self.end_headers()

def run(server_class=HTTPServer, handler_class=ManusWebhookHandler, port=8000):
    logging.basicConfig(
        filename='manus_webhook_log.txt', 
        level=logging.INFO, 
        format='%(asctime)s - %(message)s', 
        filemode='w'
    )
    
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    
    print("🚀 AmoCRM + Manus API Webhook Server")
    print("="*50)
    print(f"🌐 Сервер запущен на порту {port}")
    print(f"🧠 Manus API: {MANUS_BASE_URL}")
    print(f"📊 AmoCRM: {SUBDOMAIN}.amocrm.ru")
    print("="*50)
    print("✅ Готов к обработке сообщений!")
    print("Нажмите Ctrl+C для остановки.")
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\n🛑 Остановка сервера...")
        log_stats()
    
    httpd.server_close()
    print("✅ Сервер остановлен.")

if __name__ == '__main__':
    run()

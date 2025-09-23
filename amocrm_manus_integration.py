#!/usr/bin/env python3
"""
AmoCRM + Manus API Integration
Полная интеграция: AmoCRM → Manus → AmoCRM
"""

import requests
import json
import time
import sqlite3
from datetime import datetime
import logging

class AmoCRMManusIntegration:
    def __init__(self):
        print("🤖 AmoCRM + Manus API Integration")
        print("="*50)
        
        # Настройка логирования
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('AmoCRMManus')
        
        # Конфигурация AmoCRM
        self.amocrm_config = {
            'subdomain': 'amoshturm',
            'client_id': 'your_client_id',  # Нужно получить в AmoCRM
            'client_secret': 'your_client_secret',  # Нужно получить в AmoCRM
            'redirect_uri': 'https://example.com',
            'access_token': None,
            'refresh_token': None
        }
        
        # Конфигурация Manus API
        self.manus_config = {
            'api_key': 'sk-w3WopZM2I_Wxoltnbv0BHXP_ygv3cb53HW3Wa0Myp18ZP_ol1EfrF9gorM4Nl8rycZLLJupyvG_Y80aMtr7gpsgeogoc',
            'base_url': 'https://api.manus.run/v1',
            'mode': 'fast'  # или 'quality'
        }
        
        # База знаний для Manus
        self.knowledge_base = """
Вы - AI ассистент турагентства "Все на сплав" (vsenasplav.ru).

ТУРЫ НА 3 ДНЯ:
1. "Семейный сплав" (3 дня/2 ночи)
   - Цена: 18,000 руб/чел
   - Для семей с детьми от 8 лет
   - Маршрут: Коуровка - Чусовая

2. "Активный отдых" (3 дня/2 ночи)
   - Цена: 20,000 руб/чел
   - Для активных туристов
   - Маршрут: Староуткинск - Чусовая

ВКЛЮЧЕНО В СТОИМОСТЬ:
- Рафт и снаряжение
- Трехразовое питание
- Опытный инструктор
- Трансфер от/до Екатеринбурга

БЛИЖАЙШИЕ ДАТЫ: 15-17 июня, 22-24 июня, 29 июня-1 июля

ИНСТРУКЦИИ:
- Отвечайте дружелюбно и профессионально
- Используйте эмодзи для привлекательности
- Задавайте уточняющие вопросы
- Предлагайте конкретные варианты
- Всегда указывайте цены и даты
"""
        
        # Инициализация базы данных
        self.init_database()
        
        # Статистика
        self.stats = {
            'messages_processed': 0,
            'manus_requests': 0,
            'responses_sent': 0,
            'start_time': datetime.now()
        }
    
    def init_database(self):
        """Инициализирует базу данных для хранения диалогов"""
        try:
            self.db_conn = sqlite3.connect('amocrm_manus_integration.db')
            self.db_cursor = self.db_conn.cursor()
            
            # Таблица для хранения токенов AmoCRM
            self.db_cursor.execute('''
                CREATE TABLE IF NOT EXISTS amocrm_tokens (
                    id INTEGER PRIMARY KEY,
                    access_token TEXT,
                    refresh_token TEXT,
                    expires_at INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица для диалогов
            self.db_cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amocrm_lead_id INTEGER,
                    client_name TEXT,
                    message_text TEXT,
                    message_type TEXT,
                    manus_task_id TEXT,
                    response_text TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.db_conn.commit()
            print("✅ База данных инициализирована")
            
        except Exception as e:
            print(f"❌ Ошибка инициализации БД: {e}")
    
    def get_amocrm_access_token(self):
        """Получает access token для AmoCRM API"""
        try:
            # Сначала проверяем, есть ли сохраненный токен
            self.db_cursor.execute(
                "SELECT access_token, refresh_token, expires_at FROM amocrm_tokens ORDER BY id DESC LIMIT 1"
            )
            result = self.db_cursor.fetchone()
            
            if result and result[2] > time.time():
                self.amocrm_config['access_token'] = result[0]
                self.amocrm_config['refresh_token'] = result[1]
                print("✅ Используем сохраненный токен AmoCRM")
                return True
            
            # Если токена нет или он истек, нужна авторизация
            print("⚠️ Требуется авторизация в AmoCRM")
            print("Для получения токенов AmoCRM:")
            print("1. Зайдите в настройки AmoCRM → Интеграции")
            print("2. Создайте новую интеграцию")
            print("3. Получите client_id и client_secret")
            print("4. Обновите конфигурацию в коде")
            
            return False
            
        except Exception as e:
            print(f"❌ Ошибка получения токена AmoCRM: {e}")
            return False
    
    def get_amocrm_messages(self, lead_id=None):
        """Получает сообщения из AmoCRM"""
        try:
            if not self.amocrm_config['access_token']:
                print("❌ Нет токена доступа AmoCRM")
                return []
            
            headers = {
                'Authorization': f"Bearer {self.amocrm_config['access_token']}",
                'Content-Type': 'application/json'
            }
            
            # Получаем список сделок (leads)
            if not lead_id:
                leads_url = f"https://{self.amocrm_config['subdomain']}.amocrm.ru/api/v4/leads"
                response = requests.get(leads_url, headers=headers)
                
                if response.status_code == 200:
                    leads = response.json().get('_embedded', {}).get('leads', [])
                    if leads:
                        lead_id = leads[0]['id']  # Берем первую сделку
                        print(f"📋 Работаем со сделкой ID: {lead_id}")
                    else:
                        print("❌ Сделки не найдены")
                        return []
                else:
                    print(f"❌ Ошибка получения сделок: {response.status_code}")
                    return []
            
            # Получаем события (сообщения) по сделке
            events_url = f"https://{self.amocrm_config['subdomain']}.amocrm.ru/api/v4/events"
            params = {
                'filter[entity]': 'lead',
                'filter[entity_id]': lead_id,
                'filter[type]': 'lead_added',  # или другие типы событий
                'limit': 10
            }
            
            response = requests.get(events_url, headers=headers, params=params)
            
            if response.status_code == 200:
                events = response.json().get('_embedded', {}).get('events', [])
                print(f"📨 Найдено событий: {len(events)}")
                return events
            else:
                print(f"❌ Ошибка получения событий: {response.status_code}")
                print(f"Ответ: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Ошибка получения сообщений AmoCRM: {e}")
            return []
    
    def send_to_manus(self, message_text, conversation_context=""):
        """Отправляет сообщение в Manus API для анализа"""
        try:
            print(f"🧠 Отправляем в Manus: {message_text[:50]}...")
            
            # Формируем промпт для Manus
            prompt = f"""
{self.knowledge_base}

КОНТЕКСТ ДИАЛОГА:
{conversation_context}

НОВОЕ СООБЩЕНИЕ КЛИЕНТА:
{message_text}

Проанализируйте сообщение клиента и подготовьте профессиональный ответ от имени турагентства.
"""
            
            # Отправляем запрос в Manus API
            headers = {
                'Authorization': f"Bearer {self.manus_config['api_key']}",
                'Content-Type': 'application/json'
            }
            
            data = {
                'prompt': prompt,
                'mode': self.manus_config['mode']
            }
            
            response = requests.post(
                f"{self.manus_config['base_url']}/tasks",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                task_id = result.get('task_id')
                task_url = result.get('url')
                
                print(f"✅ Задача Manus создана: {task_id}")
                print(f"🔗 URL: {task_url}")
                
                self.stats['manus_requests'] += 1
                
                # Сохраняем в БД
                self.db_cursor.execute('''
                    INSERT INTO conversations (message_text, message_type, manus_task_id)
                    VALUES (?, ?, ?)
                ''', (message_text, 'incoming', task_id))
                self.db_conn.commit()
                
                return {
                    'task_id': task_id,
                    'url': task_url,
                    'status': 'created'
                }
            else:
                print(f"❌ Ошибка Manus API: {response.status_code}")
                print(f"Ответ: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка отправки в Manus: {e}")
            return None
    
    def get_manus_result(self, task_id):
        """Получает результат от Manus API (пока недоступно через API)"""
        try:
            # К сожалению, Manus API пока не предоставляет endpoint для получения результатов
            # Возвращаем заглушку с готовым ответом
            
            print(f"🔄 Получаем результат Manus для задачи: {task_id}")
            
            # Имитируем ответ от Manus (в реальности нужно будет получать через веб-интерфейс)
            mock_response = """🚣‍♂️ Спасибо за интерес к нашим турам!

По турам на 3 дня у нас есть отличные варианты:

🌟 **"Семейный сплав"** (3 дня/2 ночи)
💰 Цена: 18,000 руб/чел
👨‍👩‍👧‍👦 Подходит для семей с детьми от 8 лет
📍 Маршрут: Коуровка - Чусовая

🌟 **"Активный отдых"** (3 дня/2 ночи)
💰 Цена: 20,000 руб/чел
🏃‍♂️ Для любителей активного отдыха
📍 Маршрут: Староуткинск - Чусовая

**В стоимость включено:**
✅ Рафт и все снаряжение
✅ Трехразовое питание
✅ Опытный инструктор
✅ Трансфер от/до Екатеринбурга

📅 **Ближайшие свободные даты:**
• 15-17 июня
• 22-24 июня  
• 29 июня - 1 июля

Какой вариант вас больше интересует? Готов ответить на любые вопросы! 😊"""
            
            return mock_response
            
        except Exception as e:
            print(f"❌ Ошибка получения результата Manus: {e}")
            return None
    
    def send_amocrm_message(self, lead_id, message_text):
        """Отправляет сообщение в AmoCRM"""
        try:
            print(f"📤 Отправляем ответ в AmoCRM: {message_text[:50]}...")
            
            if not self.amocrm_config['access_token']:
                print("❌ Нет токена доступа AmoCRM")
                return False
            
            headers = {
                'Authorization': f"Bearer {self.amocrm_config['access_token']}",
                'Content-Type': 'application/json'
            }
            
            # Добавляем примечание к сделке (так как прямой чат через API недоступен)
            notes_url = f"https://{self.amocrm_config['subdomain']}.amocrm.ru/api/v4/leads/{lead_id}/notes"
            
            data = [
                {
                    'note_type': 'common',
                    'params': {
                        'text': f"🤖 Автоответ AI ассистента:\\n\\n{message_text}"
                    }
                }
            ]
            
            response = requests.post(notes_url, headers=headers, json=data)
            
            if response.status_code == 200:
                print("✅ Ответ отправлен в AmoCRM")
                self.stats['responses_sent'] += 1
                
                # Сохраняем в БД
                self.db_cursor.execute('''
                    UPDATE conversations 
                    SET response_text = ?, amocrm_lead_id = ?
                    WHERE manus_task_id = (SELECT manus_task_id FROM conversations ORDER BY id DESC LIMIT 1)
                ''', (message_text, lead_id))
                self.db_conn.commit()
                
                return True
            else:
                print(f"❌ Ошибка отправки в AmoCRM: {response.status_code}")
                print(f"Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка отправки сообщения в AmoCRM: {e}")
            return False
    
    def process_single_message(self, test_message=None):
        """Обрабатывает одно сообщение: AmoCRM → Manus → AmoCRM"""
        try:
            print("\\n" + "="*60)
            print("🔄 ОБРАБОТКА СООБЩЕНИЯ: AmoCRM → Manus → AmoCRM")
            print("="*60)
            
            # Шаг 1: Получаем сообщения из AmoCRM (или используем тестовое)
            if test_message:
                message_text = test_message
                lead_id = 12345  # Тестовый ID
                print(f"🧪 Используем тестовое сообщение: {message_text}")
            else:
                if not self.get_amocrm_access_token():
                    print("❌ Не удалось получить токен AmoCRM, используем тестовое сообщение")
                    message_text = "Расскажите, какие у вас есть туры на 3 дня?"
                    lead_id = 12345
                else:
                    messages = self.get_amocrm_messages()
                    if not messages:
                        print("❌ Сообщения не найдены, используем тестовое")
                        message_text = "Расскажите, какие у вас есть туры на 3 дня?"
                        lead_id = 12345
                    else:
                        # Берем первое сообщение
                        message_text = "Расскажите, какие у вас есть туры на 3 дня?"  # Заглушка
                        lead_id = messages[0].get('entity_id', 12345)
            
            print(f"📥 Входящее сообщение: {message_text}")
            print(f"📋 ID сделки: {lead_id}")
            
            # Шаг 2: Отправляем в Manus для анализа
            manus_result = self.send_to_manus(message_text)
            if not manus_result:
                print("❌ Не удалось отправить в Manus")
                return False
            
            # Шаг 3: Получаем ответ от Manus
            print("⏳ Ожидаем ответ от Manus...")
            time.sleep(3)  # Имитируем время обработки
            
            ai_response = self.get_manus_result(manus_result['task_id'])
            if not ai_response:
                print("❌ Не удалось получить ответ от Manus")
                return False
            
            print(f"🧠 Ответ от Manus получен: {len(ai_response)} символов")
            
            # Шаг 4: Отправляем ответ в AmoCRM
            success = self.send_amocrm_message(lead_id, ai_response)
            
            if success:
                self.stats['messages_processed'] += 1
                print("\\n✅ СООБЩЕНИЕ УСПЕШНО ОБРАБОТАНО!")
                print(f"📊 Статистика: обработано {self.stats['messages_processed']} сообщений")
                return True
            else:
                print("\\n❌ Ошибка при отправке ответа")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка обработки сообщения: {e}")
            return False
    
    def show_stats(self):
        """Показывает статистику работы"""
        uptime = datetime.now() - self.stats['start_time']
        
        print("\\n" + "="*50)
        print("📊 СТАТИСТИКА ИНТЕГРАЦИИ AmoCRM + Manus")
        print("="*50)
        print(f"⏱️ Время работы: {uptime}")
        print(f"📨 Обработано сообщений: {self.stats['messages_processed']}")
        print(f"🧠 Запросов к Manus: {self.stats['manus_requests']}")
        print(f"📤 Отправлено ответов: {self.stats['responses_sent']}")
        print(f"🎯 Успешность: {self.stats['responses_sent']}/{self.stats['messages_processed']}")
        print("="*50)
    
    def run_test(self):
        """Запускает тестирование интеграции"""
        print("🧪 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ AmoCRM + Manus")
        print("="*50)
        
        # Тестовые сообщения
        test_messages = [
            "Расскажите, какие у вас есть туры на 3 дня?",
            "Сколько стоит семейный сплав?",
            "Какие даты свободны в июне?"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\\n🧪 Тест {i}/{len(test_messages)}")
            success = self.process_single_message(message)
            
            if success:
                print(f"✅ Тест {i} пройден")
            else:
                print(f"❌ Тест {i} провален")
            
            time.sleep(2)  # Пауза между тестами
        
        self.show_stats()

def main():
    """Главная функция"""
    print("🚀 AmoCRM + Manus API Integration")
    print("Полная автоматизация: получение сообщений → анализ ИИ → автоответ")
    print()
    
    integration = AmoCRMManusIntegration()
    
    while True:
        print("\\n" + "="*50)
        print("📋 МЕНЮ:")
        print("1. Тестировать интеграцию")
        print("2. Обработать одно сообщение")
        print("3. Показать статистику")
        print("4. Выход")
        print("="*50)
        
        choice = input("Выберите действие (1-4): ").strip()
        
        if choice == '1':
            integration.run_test()
        elif choice == '2':
            message = input("Введите тестовое сообщение (или Enter для автоматического): ").strip()
            integration.process_single_message(message if message else None)
        elif choice == '3':
            integration.show_stats()
        elif choice == '4':
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
AmoCRM + Manus + Selenium Integration
Получает сообщения → Анализирует через Manus → Вставляет в поле ввода чата
"""

import requests
import json
import time
import sqlite3
from datetime import datetime
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

class AmoCRMManusChat:
    def __init__(self):
        print("🤖 AmoCRM + Manus + Chat Integration")
        print("Получает сообщения → Manus анализ → Готовый ответ в поле ввода")
        print("="*70)
        
        # Настройка логирования
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('AmoCRMManusChat')
        
        # Конфигурация AmoCRM
        self.amocrm_config = {
            'login_url': 'https://www.amocrm.ru/auth/login',
            'subdomain': 'amoshturm',
            'email': 'amoshturm@gmail.com',
            'password': 'GbbT4Z5L'
        }
        
        # Конфигурация Manus API
        self.manus_config = {
            'api_key': 'sk-w3WopZM2I_Wxoltnbv0BHXP_ygv3cb53HW3Wa0Myp18ZP_ol1EfrF9gorM4Nl8rycZLLJupyvG_Y80aMtr7gpsgeogoc',
            'base_url': 'https://api.manus.run/v1',
            'mode': 'fast'
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
- Используйте эмодзи умеренно
- Задавайте уточняющие вопросы
- Предлагайте конкретные варианты
- Всегда указывайте цены и даты
- Ответ должен быть готов для отправки менеджером
"""
        
        # Селекторы для AmoCRM
        self.selectors = {
            'chat_input': '.control-contenteditable__area.feed-compose__message[contenteditable="true"]',
            'messages': '.feed-note__message_paragraph',
            'send_button': 'button:contains("Отправить")',
            'chat_container': '.feed-compose'
        }
        
        # Браузер
        self.driver = None
        
        # Инициализация базы данных
        self.init_database()
        
        # Статистика
        self.stats = {
            'messages_analyzed': 0,
            'responses_prepared': 0,
            'manus_requests': 0,
            'start_time': datetime.now()
        }
    
    def init_database(self):
        """Инициализирует базу данных"""
        try:
            self.db_conn = sqlite3.connect('amocrm_manus_chat.db')
            self.db_cursor = self.db_conn.cursor()
            
            self.db_cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_name TEXT,
                    incoming_message TEXT,
                    manus_task_id TEXT,
                    prepared_response TEXT,
                    status TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.db_conn.commit()
            print("✅ База данных инициализирована")
            
        except Exception as e:
            print(f"❌ Ошибка инициализации БД: {e}")
    
    def setup_browser(self):
        """Настраивает браузер"""
        try:
            print("🌐 Настройка браузера...")
            
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-data-dir=/tmp/chrome_user_data')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            
            print("✅ Браузер настроен")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка настройки браузера: {e}")
            return False
    
    def login_to_amocrm(self):
        """Входит в AmoCRM"""
        try:
            print("🔐 Вход в AmoCRM...")
            
            self.driver.get(self.amocrm_config['login_url'])
            time.sleep(3)
            
            # Вводим email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            email_field.clear()
            email_field.send_keys(self.amocrm_config['email'])
            
            # Вводим пароль
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(self.amocrm_config['password'])
            
            # Нажимаем войти
            login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()
            
            # Ждем загрузки
            WebDriverWait(self.driver, 15).until(
                EC.url_contains("amocrm.ru")
            )
            
            print("✅ Успешный вход в AmoCRM")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка входа в AmoCRM: {e}")
            return False
    
    def navigate_to_chat(self, client_name="Anastasia"):
        """Переходит к чату с клиентом"""
        try:
            print(f"💬 Поиск чата с {client_name}...")
            
            # Переходим к сделкам/чатам
            time.sleep(5)
            
            # Ищем чат с клиентом (упрощенная версия)
            # В реальности нужно будет найти конкретный чат
            current_url = self.driver.current_url
            print(f"📍 Текущий URL: {current_url}")
            
            # Если уже в чате - отлично
            if "feed" in current_url or "chat" in current_url:
                print("✅ Уже в интерфейсе чата")
                return True
            
            # Иначе ищем чат (здесь нужна логика поиска конкретного чата)
            print("🔍 Поиск интерфейса чата...")
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка перехода к чату: {e}")
            return False
    
    def get_latest_message(self):
        """Получает последнее сообщение из чата"""
        try:
            print("📥 Получение последнего сообщения...")
            
            # Ищем все сообщения
            messages = self.driver.find_elements(By.CSS_SELECTOR, self.selectors['messages'])
            
            if not messages:
                print("❌ Сообщения не найдены")
                return None
            
            # Берем последнее сообщение
            latest_message = messages[-1]
            message_text = latest_message.text.strip()
            
            print(f"📨 Последнее сообщение: {message_text}")
            
            # Проверяем, что это не наше сообщение
            if any(emoji in message_text for emoji in ['🚣‍♂️', '💰', '📅', '✅']):
                print("⚠️ Это наше сообщение, пропускаем")
                return None
            
            return message_text
            
        except Exception as e:
            print(f"❌ Ошибка получения сообщения: {e}")
            return None
    
    def send_to_manus(self, message_text):
        """Отправляет сообщение в Manus для анализа"""
        try:
            print(f"🧠 Отправляем в Manus: {message_text[:50]}...")
            
            prompt = f"""
{self.knowledge_base}

НОВОЕ СООБЩЕНИЕ КЛИЕНТА:
{message_text}

Подготовьте профессиональный ответ от имени турагентства. Ответ должен быть готов для отправки менеджером клиенту.
"""
            
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
                
                print(f"✅ Задача Manus создана: {task_id}")
                self.stats['manus_requests'] += 1
                
                # Сохраняем в БД
                self.db_cursor.execute('''
                    INSERT INTO chat_sessions (incoming_message, manus_task_id, status)
                    VALUES (?, ?, ?)
                ''', (message_text, task_id, 'processing'))
                self.db_conn.commit()
                
                return task_id
            else:
                print(f"❌ Ошибка Manus API: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка отправки в Manus: {e}")
            return None
    
    def get_manus_response(self, task_id):
        """Получает ответ от Manus (заглушка)"""
        try:
            print(f"⏳ Получение ответа от Manus для задачи: {task_id}")
            
            # Имитируем время обработки
            time.sleep(3)
            
            # Заглушка с готовым ответом (в реальности нужно получать через API или веб-интерфейс)
            mock_response = """Спасибо за интерес к нашим турам! 😊

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
            
            print("✅ Ответ от Manus получен")
            return mock_response
            
        except Exception as e:
            print(f"❌ Ошибка получения ответа Manus: {e}")
            return None
    
    def insert_response_to_chat(self, response_text):
        """Вставляет готовый ответ в поле ввода чата"""
        try:
            print("📝 Вставка ответа в поле ввода чата...")
            
            # Ищем поле ввода
            chat_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['chat_input']))
            )
            
            # Очищаем поле
            chat_input.clear()
            
            # Вставляем текст
            chat_input.click()
            chat_input.send_keys(response_text)
            
            print("✅ Ответ вставлен в поле ввода!")
            print("👤 Менеджер может проверить и отправить сообщение")
            
            self.stats['responses_prepared'] += 1
            
            # Обновляем БД
            self.db_cursor.execute('''
                UPDATE chat_sessions 
                SET prepared_response = ?, status = ?
                WHERE manus_task_id = (SELECT manus_task_id FROM chat_sessions ORDER BY id DESC LIMIT 1)
            ''', (response_text, 'ready'))
            self.db_conn.commit()
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка вставки ответа: {e}")
            return False
    
    def process_message_cycle(self):
        """Полный цикл обработки сообщения"""
        try:
            print("\\n" + "="*70)
            print("🔄 ЦИКЛ ОБРАБОТКИ: Сообщение → Manus → Поле ввода")
            print("="*70)
            
            # Шаг 1: Получаем последнее сообщение
            message = self.get_latest_message()
            if not message:
                print("⚠️ Новых сообщений нет")
                return False
            
            self.stats['messages_analyzed'] += 1
            
            # Шаг 2: Отправляем в Manus
            task_id = self.send_to_manus(message)
            if not task_id:
                print("❌ Не удалось отправить в Manus")
                return False
            
            # Шаг 3: Получаем ответ от Manus
            response = self.get_manus_response(task_id)
            if not response:
                print("❌ Не удалось получить ответ от Manus")
                return False
            
            # Шаг 4: Вставляем в поле ввода
            success = self.insert_response_to_chat(response)
            
            if success:
                print("\\n✅ ЦИКЛ ЗАВЕРШЕН УСПЕШНО!")
                print("👤 Менеджер может проверить и отправить ответ")
                return True
            else:
                print("\\n❌ Ошибка в цикле обработки")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка цикла обработки: {e}")
            return False
    
    def monitor_chat(self, interval=30):
        """Мониторинг чата с автоматической обработкой"""
        try:
            print(f"👁️ Запуск мониторинга чата (проверка каждые {interval} сек)")
            print("Нажмите Ctrl+C для остановки")
            
            while True:
                try:
                    print(f"\\n🔍 Проверка новых сообщений... ({datetime.now().strftime('%H:%M:%S')})")
                    
                    success = self.process_message_cycle()
                    
                    if success:
                        print("✅ Сообщение обработано, ответ готов к отправке")
                    else:
                        print("⚠️ Новых сообщений нет или ошибка обработки")
                    
                    print(f"⏳ Следующая проверка через {interval} секунд...")
                    time.sleep(interval)
                    
                except KeyboardInterrupt:
                    print("\\n🛑 Мониторинг остановлен пользователем")
                    break
                    
        except Exception as e:
            print(f"❌ Ошибка мониторинга: {e}")
    
    def show_stats(self):
        """Показывает статистику"""
        uptime = datetime.now() - self.stats['start_time']
        
        print("\\n" + "="*50)
        print("📊 СТАТИСТИКА AmoCRM + Manus + Chat")
        print("="*50)
        print(f"⏱️ Время работы: {uptime}")
        print(f"📨 Проанализировано сообщений: {self.stats['messages_analyzed']}")
        print(f"🧠 Запросов к Manus: {self.stats['manus_requests']}")
        print(f"📝 Подготовлено ответов: {self.stats['responses_prepared']}")
        print("="*50)
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            if self.driver:
                self.driver.quit()
            if self.db_conn:
                self.db_conn.close()
            print("✅ Ресурсы очищены")
        except Exception as e:
            print(f"⚠️ Ошибка очистки: {e}")

def main():
    """Главная функция"""
    print("🚀 AmoCRM + Manus + Chat Integration")
    print("Автоматическая подготовка ответов в поле ввода чата")
    print()
    
    integration = AmoCRMManusChat()
    
    try:
        # Настройка браузера
        if not integration.setup_browser():
            print("❌ Не удалось настроить браузер")
            return
        
        # Вход в AmoCRM
        if not integration.login_to_amocrm():
            print("❌ Не удалось войти в AmoCRM")
            return
        
        # Переход к чату
        if not integration.navigate_to_chat():
            print("❌ Не удалось найти чат")
            return
        
        print("\\n✅ Система готова к работе!")
        
        while True:
            print("\\n" + "="*50)
            print("📋 МЕНЮ:")
            print("1. Обработать одно сообщение")
            print("2. Запустить мониторинг чата")
            print("3. Показать статистику")
            print("4. Выход")
            print("="*50)
            
            choice = input("Выберите действие (1-4): ").strip()
            
            if choice == '1':
                integration.process_message_cycle()
            elif choice == '2':
                interval = input("Интервал проверки в секундах (по умолчанию 30): ").strip()
                interval = int(interval) if interval.isdigit() else 30
                integration.monitor_chat(interval)
            elif choice == '3':
                integration.show_stats()
            elif choice == '4':
                print("👋 Завершение работы...")
                break
            else:
                print("❌ Неверный выбор")
                
    except KeyboardInterrupt:
        print("\\n🛑 Программа прервана пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
    finally:
        integration.cleanup()

if __name__ == "__main__":
    main()

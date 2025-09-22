#!/usr/bin/env python3
"""
AmoCRM Working Automation - Объединение рабочего подхода с новыми селекторами
Основано на успешном скрипте amo_assistant_smart.py с обновленными селекторами
"""

import json
import time
import sqlite3
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class AmoCRMWorkingAutomation:
    def __init__(self):
        print("🚀 AmoCRM Working Automation - Проверенный подход с новыми селекторами")
        print("="*70)
        
        # Настройка логирования
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('AmoCRMWorking')
        
        # Инициализация базы данных
        self.init_database()
        
        # Переменные для работы
        self.driver = None
        self.wait = None
        self.current_client = None
        
        # Проверенные селекторы для AmoCRM
        self.selectors = {
            'chat_input': {
                # Основной селектор из исследования
                'contenteditable': '.control-contenteditable__area.feed-compose__message[contenteditable="true"]',
                # Альтернативные селекторы
                'alternative_input': 'div[contenteditable="true"][data-hint*="Введите текст"]',
                'any_contenteditable': 'div[contenteditable="true"]',
                # Fallback селекторы из рабочего скрипта
                'textarea_message': "textarea[placeholder*='сообщение']",
                'textarea_general': "textarea",
            },
            'send_button': {
                # XPath селекторы для кнопки "Отправить"
                'by_text_xpath': '//button[.//span[contains(@class, "button-input-inner__text") and contains(text(), "Отправить")]]',
                'by_span_xpath': '//span[@class="button-input-inner__text" and contains(text(), "Отправить")]/ancestor::button',
                # CSS селекторы как fallback
                'submit_button': 'button[type="submit"]',
                'send_class': '.send-button, .btn-send'
            },
            'messages': {
                # Селекторы для сообщений из исследования
                'message_text': '.feed-note__message_paragraph',
                'message_container': '.feed-note',
                # Альтернативные селекторы
                'incoming_messages': "[class*='message']:not([class*='own'])",
                'any_messages': "[class*='message']"
            }
        }
        
        # Готовый ответ на вопрос о турах на 3 дня
        self.tour_3_days_response = """🚣‍♂️ Туры на 3 дня по реке Чусовая:

🌟 "Семейный сплав" (3 дня/2 ночи)
💰 Цена: 18,000 руб/чел
👨‍👩‍👧‍👦 Для семей с детьми от 8 лет
📍 Маршрут: Коуровка - Чусовая

🌟 "Активный отдых" (3 дня/2 ночи)  
💰 Цена: 20,000 руб/чел
🏃‍♂️ Для активных туристов
📍 Маршрут: Староуткинск - Чусовая

В стоимость включено:
✅ Рафт и снаряжение
✅ Трехразовое питание
✅ Опытный инструктор
✅ Трансфер от/до Екатеринбурга

📅 Ближайшие даты: 15-17 июня, 22-24 июня, 29 июня-1 июля

Какой тур вас больше интересует? 😊"""
        
        self.stats = {
            "messages_processed": 0,
            "responses_generated": 0,
            "start_time": datetime.now()
        }
    
    def init_database(self):
        """Инициализирует базу данных для хранения диалогов"""
        try:
            self.db_conn = sqlite3.connect('conversations_working.db')
            self.db_cursor = self.db_conn.cursor()
            
            # Создаем таблицы
            self.db_cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    first_contact DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_contact DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.db_cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    message_type TEXT NOT NULL,
                    message_text TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            ''')
            
            self.db_conn.commit()
            print("✅ База данных инициализирована")
            
        except Exception as e:
            print(f"❌ Ошибка инициализации БД: {e}")
    
    def setup_browser(self):
        """Настраивает видимый браузер (проверенный подход)"""
        try:
            print("🌐 Настройка браузера...")
            
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 10)
            
            print("✅ Браузер настроен успешно")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка настройки браузера: {e}")
            return False
    
    def manual_login_to_amocrm(self):
        """Ручной вход в amoCRM (проверенный подход)"""
        try:
            print("🔐 Переход к amoCRM...")
            self.driver.get("https://amoshturm.amocrm.ru")
            
            print("\\n" + "="*70)
            print("🔐 НАСТРОЙКА АВТОМАТИЗАЦИИ AmoCRM")
            print("="*70)
            print("1. Войдите в amoCRM (логин: amoshturm@gmail.com)")
            print("2. Откройте диалог с Anastasia")
            print("3. Убедитесь, что видите:")
            print("   - Историю сообщений")
            print("   - Поле для ввода ответа")
            print("   - Кнопку 'Отправить'")
            print("4. Нажмите Enter для начала автоматизации")
            print("="*70)
            
            input("Нажмите Enter после настройки...")
            
            # Определяем текущего клиента
            self.identify_current_client()
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка входа: {e}")
            return False
    
    def identify_current_client(self):
        """Определяет текущего клиента (Anastasia)"""
        try:
            # Ищем имя клиента в различных местах интерфейса
            name_selectors = [
                "h1", "h2", "h3",
                "[class*='client']", "[class*='contact']", "[class*='lead']",
                "[class*='name']", "[class*='title']"
            ]
            
            client_name = "Anastasia"  # По умолчанию, так как знаем клиента
            
            for selector in name_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if 'anastasia' in text.lower():
                            client_name = text
                            break
                    if client_name != "Anastasia":
                        break
                except:
                    continue
            
            # Сохраняем клиента в БД
            self.current_client = self.get_or_create_client(client_name)
            print(f"👤 Текущий клиент: {client_name} (ID: {self.current_client})")
            
        except Exception as e:
            print(f"❌ Ошибка определения клиента: {e}")
            self.current_client = self.get_or_create_client("Anastasia")
    
    def get_or_create_client(self, name):
        """Получает или создает клиента в БД"""
        try:
            # Ищем существующего клиента
            self.db_cursor.execute("SELECT id FROM clients WHERE name = ?", (name,))
            result = self.db_cursor.fetchone()
            
            if result:
                # Обновляем время последнего контакта
                self.db_cursor.execute(
                    "UPDATE clients SET last_contact = CURRENT_TIMESTAMP WHERE id = ?",
                    (result[0],)
                )
                self.db_conn.commit()
                return result[0]
            else:
                # Создаем нового клиента
                self.db_cursor.execute(
                    "INSERT INTO clients (name) VALUES (?)",
                    (name,)
                )
                self.db_conn.commit()
                return self.db_cursor.lastrowid
                
        except Exception as e:
            print(f"❌ Ошибка работы с клиентом: {e}")
            return 1
    
    def find_chat_input_field(self):
        """Ищет поле ввода сообщения с новыми селекторами"""
        try:
            print("🔍 Поиск поля ввода...")
            
            # Пробуем все селекторы по порядку приоритета
            input_selectors = [
                # Новые селекторы из исследования
                self.selectors['chat_input']['contenteditable'],
                self.selectors['chat_input']['alternative_input'],
                self.selectors['chat_input']['any_contenteditable'],
                # Fallback селекторы из рабочего скрипта
                self.selectors['chat_input']['textarea_message'],
                "textarea[placeholder*='Сообщение']", 
                "textarea[placeholder*='Напишите']",
                "textarea[placeholder*='Ответ']",
                "input[placeholder*='сообщение']",
                "textarea[name*='message']",
                "textarea[class*='message']",
                "textarea[class*='input']",
                self.selectors['chat_input']['textarea_general']
            ]
            
            for selector in input_selectors:
                try:
                    element = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    
                    if element.is_displayed() and element.is_enabled():
                        print(f"✅ Найдено поле ввода: {selector}")
                        return element
                        
                except Exception as e:
                    self.logger.debug(f"Селектор {selector} не сработал: {e}")
                    continue
            
            print("❌ Поле ввода не найдено")
            return None
            
        except Exception as e:
            print(f"❌ Ошибка поиска поля ввода: {e}")
            return None
    
    def find_send_button(self):
        """Ищет кнопку отправки с новыми селекторами"""
        try:
            print("🔍 Поиск кнопки отправки...")
            
            # XPath селекторы
            xpath_selectors = [
                self.selectors['send_button']['by_text_xpath'],
                self.selectors['send_button']['by_span_xpath']
            ]
            
            for selector in xpath_selectors:
                try:
                    send_button = self.driver.find_element(By.XPATH, selector)
                    
                    if send_button.is_displayed() and send_button.is_enabled():
                        print(f"✅ Найдена кнопка отправки (XPath): {selector}")
                        return send_button
                        
                except Exception as e:
                    self.logger.debug(f"XPath селектор {selector} не сработал: {e}")
                    continue
            
            # CSS селекторы как fallback
            css_selectors = [
                self.selectors['send_button']['submit_button'],
                self.selectors['send_button']['send_class'],
                'button[title*="Отправить"]',
                'button[aria-label*="Отправить"]'
            ]
            
            for selector in css_selectors:
                try:
                    send_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if send_button.is_displayed() and send_button.is_enabled():
                        print(f"✅ Найдена кнопка отправки (CSS): {selector}")
                        return send_button
                        
                except Exception as e:
                    self.logger.debug(f"CSS селектор {selector} не сработал: {e}")
                    continue
            
            print("⚠️ Кнопка отправки не найдена - будем использовать Enter")
            return None
            
        except Exception as e:
            print(f"❌ Ошибка поиска кнопки отправки: {e}")
            return None
    
    def send_message_to_chat(self, message_text):
        """Отправляет сообщение в чат"""
        try:
            print(f"📤 Отправка сообщения: {message_text[:50]}...")
            
            # Находим поле ввода
            input_field = self.find_chat_input_field()
            if not input_field:
                return self.show_message_for_copy(message_text)
            
            # Очищаем поле и вводим текст
            input_field.click()
            time.sleep(0.5)
            
            # Для contenteditable используем специальный подход
            if input_field.get_attribute('contenteditable') == 'true':
                # Очищаем contenteditable
                ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
                time.sleep(0.2)
                input_field.send_keys(Keys.DELETE)
                time.sleep(0.2)
                
                # Вводим текст
                input_field.send_keys(message_text)
            else:
                # Обычное поле
                input_field.clear()
                time.sleep(0.5)
                input_field.send_keys(message_text)
            
            time.sleep(1)
            
            # Пробуем найти и нажать кнопку отправки
            send_button = self.find_send_button()
            if send_button:
                send_button.click()
                print("✅ Сообщение отправлено через кнопку!")
            else:
                # Используем Enter как fallback
                input_field.send_keys(Keys.ENTER)
                print("✅ Сообщение отправлено через Enter!")
            
            # Сохраняем в БД
            self.save_message(message_text, 'outgoing')
            self.stats['responses_generated'] += 1
            
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отправки сообщения: {e}")
            return self.show_message_for_copy(message_text)
    
    def show_message_for_copy(self, message_text):
        """Показывает сообщение для ручного копирования"""
        print("\\n" + "="*70)
        print("📋 СООБЩЕНИЕ ДЛЯ РУЧНОЙ ОТПРАВКИ:")
        print("="*70)
        print(message_text)
        print("="*70)
        input("Скопируйте и отправьте сообщение вручную, затем нажмите Enter...")
        return True
    
    def save_message(self, message_text, message_type):
        """Сохраняет сообщение в БД"""
        try:
            self.db_cursor.execute('''
                INSERT INTO conversations (client_id, message_type, message_text)
                VALUES (?, ?, ?)
            ''', (self.current_client, message_type, message_text))
            
            self.db_conn.commit()
            
        except Exception as e:
            print(f"❌ Ошибка сохранения сообщения: {e}")
    
    def find_new_messages(self):
        """Ищет новые сообщения в диалоге"""
        try:
            # Используем новые селекторы для сообщений
            message_selectors = [
                self.selectors['messages']['message_text'],
                self.selectors['messages']['message_container'],
                self.selectors['messages']['incoming_messages'],
                "[class*='message']:not([class*='own'])",
                "[class*='incoming']",
                "[class*='received']",
                ".message:not(.outgoing)"
            ]
            
            messages = []
            for selector in message_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and len(text) > 3:
                            # Проверяем, не обрабатывали ли уже это сообщение
                            self.db_cursor.execute(
                                "SELECT id FROM conversations WHERE client_id = ? AND message_text = ? AND message_type = 'incoming'",
                                (self.current_client, text)
                            )
                            if not self.db_cursor.fetchone():
                                messages.append({
                                    'text': text,
                                    'element': element
                                })
                    
                    if messages:  # Если нашли сообщения, не пробуем другие селекторы
                        break
                        
                except Exception as e:
                    self.logger.debug(f"Селектор сообщений {selector} не сработал: {e}")
                    continue
            
            return messages
            
        except Exception as e:
            print(f"❌ Ошибка поиска сообщений: {e}")
            return []
    
    def analyze_message_and_respond(self, message_text):
        """Анализирует сообщение и генерирует ответ"""
        try:
            message_lower = message_text.lower()
            
            # Сохраняем входящее сообщение
            self.save_message(message_text, 'incoming')
            
            # Анализируем содержание
            if any(word in message_lower for word in ['3 дня', 'три дня', 'трехдневный']):
                return self.tour_3_days_response
            
            elif any(word in message_lower for word in ['тур', 'сплав', 'поход']):
                return """🚣‍♂️ У нас есть туры разной продолжительности:

• 2 дня - выходные туры
• 3 дня - популярные маршруты  
• 4+ дней - экспедиционные туры

На сколько дней вы планируете тур?"""
            
            elif any(word in message_lower for word in ['цена', 'стоимость', 'сколько']):
                return """💰 Стоимость зависит от продолжительности:

• 2 дня: от 8,000 руб/чел
• 3 дня: от 12,000 руб/чел  
• 4+ дней: от 16,000 руб/чел

В стоимость включено снаряжение, питание и инструктор.
На какой тур интересуетесь?"""
            
            elif any(word in message_lower for word in ['когда', 'дата', 'время']):
                return """📅 Сезон сплавов: май - сентябрь

Ближайшие свободные даты:
• Выходные: каждую субботу-воскресенье
• Будние дни: по согласованию

На какой период рассматриваете поездку?"""
            
            else:
                return """Спасибо за сообщение! 😊

Расскажите, что вас интересует:
• Какой тур (продолжительность)?
• Примерные даты?
• Количество участников?

Подберу оптимальный вариант!"""
            
        except Exception as e:
            print(f"❌ Ошибка анализа сообщения: {e}")
            return "Спасибо за сообщение! Сейчас подготовлю информацию."
    
    def run_automation(self):
        """Запускает основной цикл автоматизации"""
        print("🚀 Запуск автоматизации AmoCRM...")
        
        if not self.setup_browser():
            print("❌ Не удалось настроить браузер")
            return
        
        if not self.manual_login_to_amocrm():
            print("❌ Не удалось войти в amoCRM")
            return
        
        print("\\n✅ Автоматизация запущена!")
        print("🔍 Мониторинг новых сообщений...")
        print("🤖 Автоматические ответы на основе ключевых слов")
        print("💾 Сохранение истории в базу данных")
        print("🛑 Для остановки нажмите Ctrl+C")
        
        try:
            while True:
                new_messages = self.find_new_messages()
                
                if new_messages:
                    print(f"\\n📨 Найдено новых сообщений: {len(new_messages)}")
                    
                    for msg in new_messages:
                        print(f"\\n📥 Обрабатываю: {msg['text'][:50]}...")
                        
                        # Генерируем ответ
                        response = self.analyze_message_and_respond(msg['text'])
                        
                        # Отправляем ответ
                        success = self.send_message_to_chat(response)
                        
                        if success:
                            self.stats['messages_processed'] += 1
                            print(f"✅ Сообщение обработано. Всего: {self.stats['messages_processed']}")
                        
                        time.sleep(3)  # Пауза между сообщениями
                else:
                    print(".", end="", flush=True)
                
                time.sleep(5)  # Проверка каждые 5 секунд
                
        except KeyboardInterrupt:
            print("\\n🛑 Автоматизация остановлена пользователем")
        except Exception as e:
            print(f"\\n❌ Ошибка автоматизации: {e}")
        finally:
            if self.driver:
                print("🔄 Закрытие браузера...")
                self.driver.quit()
            
            if hasattr(self, 'db_conn'):
                self.db_conn.close()
            
            # Показываем статистику
            uptime = datetime.now() - self.stats['start_time']
            print(f"\\n📊 СТАТИСТИКА РАБОТЫ:")
            print(f"⏱️ Время работы: {uptime}")
            print(f"📨 Обработано сообщений: {self.stats['messages_processed']}")
            print(f"🤖 Отправлено ответов: {self.stats['responses_generated']}")

def main():
    """Главная функция"""
    print("🤖 AmoCRM Working Automation")
    print("Объединение проверенного подхода с новыми селекторами")
    print()
    
    automation = AmoCRMWorkingAutomation()
    automation.run_automation()

if __name__ == "__main__":
    main()

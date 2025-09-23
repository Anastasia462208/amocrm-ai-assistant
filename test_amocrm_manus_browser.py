#!/usr/bin/env python3
"""
AmoCRM + Manus Integration через Browser Tools
Тестирование на открытом окне AmoCRM
"""

import requests
import json
import time
from datetime import datetime

class AmoCRMManusTest:
    def __init__(self):
        print("🧪 ТЕСТ: AmoCRM + Manus Integration")
        print("Использует уже открытое окно AmoCRM")
        print("="*50)
        
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
- Ответ должен быть готов для вставки в поле ввода чата
"""
        
        self.stats = {
            'manus_requests': 0,
            'responses_generated': 0,
            'start_time': datetime.now()
        }
    
    def send_to_manus(self, message_text):
        """Отправляет сообщение в Manus для анализа"""
        try:
            print(f"🧠 Отправляем в Manus: {message_text}")
            print("-" * 50)
            
            prompt = f"""
{self.knowledge_base}

НОВОЕ СООБЩЕНИЕ КЛИЕНТА:
"{message_text}"

Подготовьте профессиональный ответ от имени турагентства. Ответ должен быть готов для отправки клиенту через чат AmoCRM.
"""
            
            headers = {
                'Authorization': f"Bearer {self.manus_config['api_key']}",
                'Content-Type': 'application/json'
            }
            
            data = {
                'prompt': prompt,
                'mode': self.manus_config['mode']
            }
            
            print("📤 Отправляем запрос в Manus API...")
            
            response = requests.post(
                f"{self.manus_config['base_url']}/tasks",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                task_id = result.get('task_id')
                task_url = result.get('url')
                
                print(f"✅ Задача Manus создана успешно!")
                print(f"📋 Task ID: {task_id}")
                print(f"🔗 URL: {task_url}")
                
                self.stats['manus_requests'] += 1
                
                return {
                    'task_id': task_id,
                    'url': task_url,
                    'status': 'created'
                }
            else:
                print(f"❌ Ошибка Manus API: {response.status_code}")
                print(f"📄 Ответ: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("⏰ Таймаут запроса к Manus API")
            return None
        except Exception as e:
            print(f"❌ Ошибка отправки в Manus: {e}")
            return None
    
    def get_mock_manus_response(self, task_id, original_message):
        """Получает заглушку ответа от Manus (имитация)"""
        try:
            print(f"⏳ Имитируем получение ответа от Manus для задачи: {task_id}")
            
            # Имитируем время обработки
            time.sleep(2)
            
            # Анализируем сообщение и генерируем соответствующий ответ
            message_lower = original_message.lower()
            
            if "3 дня" in message_lower or "три дня" in message_lower:
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
            
            elif "цена" in message_lower or "стоимость" in message_lower:
                mock_response = """Цены на наши туры:

💰 "Семейный сплав" (3 дня/2 ночи) - 18,000 руб/чел
💰 "Активный отдых" (3 дня/2 ночи) - 20,000 руб/чел

В стоимость уже включено ВСЕ необходимое:
✅ Рафт и снаряжение
✅ Трехразовое питание  
✅ Опытный инструктор
✅ Трансфер от/до Екатеринбурга

Никаких доплат! Какой тур вас интересует?"""
            
            elif "дата" in message_lower or "когда" in message_lower:
                mock_response = """📅 Ближайшие свободные даты для туров:

🗓️ 15-17 июня (пятница-воскресенье)
🗓️ 22-24 июня (пятница-воскресенье)  
🗓️ 29 июня - 1 июля (пятница-воскресенье)

Все туры начинаются в пятницу утром, возвращение в воскресенье вечером.

Какая дата вам подходит больше?"""
            
            else:
                mock_response = """Здравствуйте! Спасибо за обращение в "Все на сплав" 😊

Мы организуем незабываемые сплавы по реке Чусовая. У нас есть туры разной продолжительности и сложности.

Расскажите, что вас интересует:
• Продолжительность тура?
• Количество участников?
• Примерные даты?

Подберу для вас идеальный вариант!"""
            
            print("✅ Ответ от Manus (имитация) получен")
            self.stats['responses_generated'] += 1
            
            return mock_response
            
        except Exception as e:
            print(f"❌ Ошибка получения ответа: {e}")
            return None
    
    def test_full_cycle(self, test_message):
        """Тестирует полный цикл обработки"""
        try:
            print("\\n" + "="*70)
            print("🔄 ПОЛНЫЙ ТЕСТ ЦИКЛА: Сообщение → Manus → Готовый ответ")
            print("="*70)
            
            print(f"📥 Тестовое сообщение клиента:")
            print(f'"{test_message}"')
            print()
            
            # Шаг 1: Отправляем в Manus
            manus_result = self.send_to_manus(test_message)
            if not manus_result:
                print("❌ Не удалось отправить в Manus")
                return False
            
            print()
            
            # Шаг 2: Получаем ответ (имитация)
            ai_response = self.get_mock_manus_response(manus_result['task_id'], test_message)
            if not ai_response:
                print("❌ Не удалось получить ответ")
                return False
            
            print()
            print("📝 ГОТОВЫЙ ОТВЕТ ДЛЯ ВСТАВКИ В ПОЛЕ ВВОДА:")
            print("=" * 50)
            print(ai_response)
            print("=" * 50)
            print()
            
            print("✅ ТЕСТ УСПЕШНО ЗАВЕРШЕН!")
            print("👤 Этот ответ готов для вставки в поле ввода AmoCRM")
            print("🔗 Manus Task URL:", manus_result['url'])
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка теста: {e}")
            return False
    
    def show_stats(self):
        """Показывает статистику тестирования"""
        uptime = datetime.now() - self.stats['start_time']
        
        print("\\n" + "="*50)
        print("📊 СТАТИСТИКА ТЕСТИРОВАНИЯ")
        print("="*50)
        print(f"⏱️ Время работы: {uptime}")
        print(f"🧠 Запросов к Manus: {self.stats['manus_requests']}")
        print(f"📝 Ответов сгенерировано: {self.stats['responses_generated']}")
        print("="*50)

def main():
    """Главная функция тестирования"""
    print("🧪 ТЕСТИРОВАНИЕ AmoCRM + Manus Integration")
    print("Работает с уже открытым окном AmoCRM")
    print()
    
    tester = AmoCRMManusTest()
    
    # Тестовые сообщения
    test_messages = [
        "Расскажите, какие у вас есть туры на 3 дня?",
        "Сколько стоит семейный сплав?", 
        "Какие даты свободны в июне?",
        "Здравствуйте, интересуют сплавы для семьи"
    ]
    
    print("📋 Доступные тестовые сообщения:")
    for i, msg in enumerate(test_messages, 1):
        print(f"{i}. {msg}")
    print()
    
    while True:
        print("\\n" + "="*50)
        print("📋 МЕНЮ ТЕСТИРОВАНИЯ:")
        print("1-4. Тестировать готовое сообщение")
        print("5. Ввести свое сообщение")
        print("6. Показать статистику")
        print("7. Выход")
        print("="*50)
        
        choice = input("Выберите действие (1-7): ").strip()
        
        if choice in ['1', '2', '3', '4']:
            idx = int(choice) - 1
            message = test_messages[idx]
            print(f"\\n🧪 Тестируем сообщение {choice}: {message}")
            tester.test_full_cycle(message)
            
        elif choice == '5':
            custom_message = input("\\nВведите сообщение для тестирования: ").strip()
            if custom_message:
                tester.test_full_cycle(custom_message)
            else:
                print("❌ Пустое сообщение")
                
        elif choice == '6':
            tester.show_stats()
            
        elif choice == '7':
            print("👋 Тестирование завершено!")
            break
            
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    main()

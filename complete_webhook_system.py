#!/usr/bin/env python3
"""
Полная система интеграции AmoCRM + Manus API через Webhooks
Двойной webhook handler для полной автоматизации
"""

import json
import time
import logging
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from urllib.parse import parse_qs
import sqlite3
import threading
from typing import Dict, Any, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация
class Config:
    # Manus API
    MANUS_API_URL = "https://api.manus.im/v1/tasks"
    MANUS_API_KEY = "sk-fNQLWaD5AHLplRB2fVDZ8lfKxVbbEEHWCzl_z016aM4_2EMtOSPtEfCUzhUOZq1DCufwtAAmfIeCn0QFZaS9DkBp2QS3"
    
    # AmoCRM API
    AMOCRM_DOMAIN = "amoshturm.amocrm.ru"
    AMOCRM_ACCESS_TOKEN = "YOUR_AMOCRM_TOKEN"  # Нужно получить
    
    # База данных
    DB_PATH = "webhook_system.db"

app = Flask(__name__)

class DatabaseManager:
    """Управление базой данных для отслеживания задач"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                lead_id TEXT NOT NULL,
                original_message TEXT NOT NULL,
                manus_response TEXT,
                status TEXT DEFAULT 'created',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("База данных инициализирована")
    
    def save_task(self, task_id: str, lead_id: str, message: str) -> bool:
        """Сохранение новой задачи"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO tasks 
                (task_id, lead_id, original_message, status) 
                VALUES (?, ?, ?, 'created')
            ''', (task_id, lead_id, message))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения задачи: {e}")
            return False
    
    def update_task_response(self, task_id: str, response: str, status: str = 'completed') -> bool:
        """Обновление ответа задачи"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE tasks 
                SET manus_response = ?, status = ?, completed_at = CURRENT_TIMESTAMP
                WHERE task_id = ?
            ''', (response, status, task_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Ошибка обновления задачи: {e}")
            return False
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict]:
        """Получение задачи по ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT task_id, lead_id, original_message, manus_response, status, created_at
                FROM tasks WHERE task_id = ?
            ''', (task_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'task_id': result[0],
                    'lead_id': result[1],
                    'original_message': result[2],
                    'manus_response': result[3],
                    'status': result[4],
                    'created_at': result[5]
                }
            return None
        except Exception as e:
            logger.error(f"Ошибка получения задачи: {e}")
            return None
    
    def log_event(self, event_type: str, details: str = ""):
        """Логирование событий"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO statistics (event_type, details) 
                VALUES (?, ?)
            ''', (event_type, details))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка логирования: {e}")

class ManusAPI:
    """Работа с Manus API"""
    
    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def create_task(self, message: str, lead_id: str) -> Optional[str]:
        """Создание задачи в Manus"""
        
        # Промпт с базой знаний
        knowledge_base_prompt = f"""
Ты - AI ассистент турагентства "Все на сплав". 

БАЗА ЗНАНИЙ:
- Туры на 3 дня по реке Чусовая:
  * "Семейный сплав" (3 дня/2 ночи) - 18,000 руб/чел
  * "Активный отдых" (3 дня/2 ночи) - 20,000 руб/чел
- Включено: питание, инструктор, снаряжение, трансфер
- Даты: 15-17 июня, 22-24 июня, 1-3 июля
- Подходит для семей с детьми от 8 лет

ЗАДАЧА: Ответь на вопрос клиента профессионально и подробно.

СООБЩЕНИЕ КЛИЕНТА: {message}

Ответь как опытный менеджер турагентства с эмодзи и конкретными предложениями.
"""
        
        payload = {
            "prompt": knowledge_base_prompt,
            "mode": "quality"
        }
        
        try:
            logger.info(f"Отправляем задачу в Manus для сделки {lead_id}")
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get('task_id')
                logger.info(f"Задача создана: {task_id}")
                return task_id
            else:
                logger.error(f"Ошибка Manus API: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка создания задачи: {e}")
            return None

class AmoCRMAPI:
    """Работа с AmoCRM API"""
    
    def __init__(self, domain: str, access_token: str):
        self.domain = domain
        self.access_token = access_token
        self.base_url = f"https://{domain}/api/v4"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def add_note_to_lead(self, lead_id: str, message: str) -> bool:
        """Добавление примечания к сделке"""
        
        note_data = {
            "note_type": "common",
            "params": {
                "text": f"🤖 AI Ассистент:\\n\\n{message}"
            }
        }
        
        try:
            url = f"{self.base_url}/leads/{lead_id}/notes"
            response = requests.post(
                url,
                headers=self.headers,
                json=[note_data],
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Примечание добавлено к сделке {lead_id}")
                return True
            else:
                logger.error(f"Ошибка добавления примечания: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка AmoCRM API: {e}")
            return False

# Инициализация компонентов
db_manager = DatabaseManager(Config.DB_PATH)
manus_api = ManusAPI(Config.MANUS_API_KEY, Config.MANUS_API_URL)
amocrm_api = AmoCRMAPI(Config.AMOCRM_DOMAIN, Config.AMOCRM_ACCESS_TOKEN)

@app.route('/amocrm-webhook', methods=['POST'])
def handle_amocrm_webhook():
    """Обработка webhook от AmoCRM"""
    
    try:
        # Получение данных от AmoCRM
        raw_data = request.get_data(as_text=True)
        logger.info(f"Получен webhook от AmoCRM: {raw_data[:200]}...")
        
        # Парсинг данных
        parsed_data = parse_qs(raw_data)
        
        # Извлечение сообщения
        message_text = None
        lead_id = None
        
        for key, values in parsed_data.items():
            if 'message[add]' in key and '[text]' in key:
                message_text = values[0] if values else None
            elif 'message[add]' in key and '[entity_id]' in key:
                lead_id = values[0] if values else None
        
        if not message_text or not lead_id:
            logger.warning("Не удалось извлечь сообщение или ID сделки")
            return jsonify({"status": "error", "message": "Invalid data"}), 400
        
        logger.info(f"📥 Новое сообщение для сделки {lead_id}: '{message_text}'")
        
        # Отправка задачи в Manus
        task_id = manus_api.create_task(message_text, lead_id)
        
        if task_id:
            # Сохранение в базу данных
            db_manager.save_task(task_id, lead_id, message_text)
            db_manager.log_event("amocrm_message_received", f"Lead: {lead_id}, Task: {task_id}")
            
            logger.info(f"✅ Задача отправлена в Manus: {task_id}")
            return jsonify({
                "status": "success", 
                "task_id": task_id,
                "message": "Task sent to Manus"
            })
        else:
            logger.error("❌ Не удалось создать задачу в Manus")
            return jsonify({"status": "error", "message": "Failed to create Manus task"}), 500
            
    except Exception as e:
        logger.error(f"Ошибка обработки AmoCRM webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/manus-webhook', methods=['POST'])
def handle_manus_webhook():
    """Обработка webhook от Manus"""
    
    try:
        data = request.get_json()
        logger.info(f"Получен webhook от Manus: {json.dumps(data, indent=2)}")
        
        event_type = data.get('event_type')
        task_detail = data.get('task_detail', {})
        task_id = task_detail.get('task_id')
        
        if event_type == 'task_stopped':
            stop_reason = task_detail.get('stop_reason')
            message = task_detail.get('message', '')
            
            if stop_reason == 'finish' and task_id:
                logger.info(f"🎉 Задача завершена: {task_id}")
                
                # Получение информации о задаче из БД
                task_info = db_manager.get_task_by_id(task_id)
                
                if task_info:
                    lead_id = task_info['lead_id']
                    
                    # Обновление задачи в БД
                    db_manager.update_task_response(task_id, message, 'completed')
                    
                    # Отправка ответа в AmoCRM
                    success = amocrm_api.add_note_to_lead(lead_id, message)
                    
                    if success:
                        logger.info(f"✅ Ответ отправлен в AmoCRM для сделки {lead_id}")
                        db_manager.log_event("response_sent", f"Lead: {lead_id}, Task: {task_id}")
                    else:
                        logger.error(f"❌ Не удалось отправить ответ в AmoCRM")
                        db_manager.log_event("response_failed", f"Lead: {lead_id}, Task: {task_id}")
                    
                    return jsonify({
                        "status": "success",
                        "message": "Response processed",
                        "sent_to_amocrm": success
                    })
                else:
                    logger.warning(f"Задача {task_id} не найдена в БД")
            
            elif stop_reason == 'ask':
                logger.info(f"🤔 Задача требует уточнения: {task_id}")
                # Можно добавить логику для обработки вопросов
        
        elif event_type == 'task_created':
            logger.info(f"📝 Задача создана: {task_id}")
            db_manager.log_event("task_created", f"Task: {task_id}")
        
        return jsonify({"status": "success", "message": "Webhook processed"})
        
    except Exception as e:
        logger.error(f"Ошибка обработки Manus webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Статус системы"""
    
    try:
        conn = sqlite3.connect(Config.DB_PATH)
        cursor = conn.cursor()
        
        # Статистика задач
        cursor.execute("SELECT COUNT(*) FROM tasks")
        total_tasks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")
        completed_tasks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'created'")
        pending_tasks = cursor.fetchone()[0]
        
        # Последние события
        cursor.execute("""
            SELECT event_type, timestamp, details 
            FROM statistics 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        recent_events = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            "status": "running",
            "statistics": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": pending_tasks
            },
            "recent_events": [
                {
                    "type": event[0],
                    "timestamp": event[1],
                    "details": event[2]
                }
                for event in recent_events
            ]
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья системы"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

def print_startup_info():
    """Информация о запуске"""
    print("\\n" + "="*60)
    print("🚀 ПОЛНАЯ СИСТЕМА AmoCRM + Manus ИНТЕГРАЦИИ")
    print("="*60)
    print(f"🌐 Сервер запущен на порту 5000")
    print(f"🔗 AmoCRM Webhook: http://your-domain.com:5000/amocrm-webhook")
    print(f"🔗 Manus Webhook: http://your-domain.com:5000/manus-webhook")
    print(f"📊 Статус системы: http://your-domain.com:5000/status")
    print(f"💚 Health Check: http://your-domain.com:5000/health")
    print("="*60)
    print("✅ Готов к обработке сообщений!")
    print("🔄 Полная автоматизация: AmoCRM → Manus → AmoCRM")
    print("📚 База знаний: GitHub Repository")
    print("🤖 AI ответы: Manus API")
    print("="*60)
    print("Нажмите Ctrl+C для остановки\\n")

if __name__ == '__main__':
    print_startup_info()
    
    # Запуск сервера
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )

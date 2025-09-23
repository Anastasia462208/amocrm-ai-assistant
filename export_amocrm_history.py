#!/usr/bin/env python3
"""
Скрипт для экспорта истории переписки из amoCRM API
Получает все примечания по сделкам и сохраняет в JSON файл для последующего импорта
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import argparse

# Конфигурация amoCRM API
SUBDOMAIN = 'amoshturm'
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjBjYjliYjRhZmI3ODNiOWNiMDA2Mzg5NWE1Nzg5MjhjMGViNDZlZTcxYzc2MGUwNGFjNTE3OGUzNWE4Mzk2MWZjNWI2NzQ2NDRjN2U5YmRlIn0.eyJhdWQiOiI3NWMyYjNlYi1kODM3LTQwNzktYjNkYS04YzJmOWU0OTRkNjYiLCJqdGkiOiIwY2I5YmI0YWZiNzgzYjljYjAwNjM4OTVhNTc4OTI4YzBlYjQ2ZWU3MWM3NjBlMDRhYzUxNzhlMzVhODM5NjFmYzViNjc0NjQ0YzdlOWJkZSIsImlhdCI6MTc0NTg0ODE4MiwibmJmIjoxNzQ1ODQ4MTgyLCJleHAiOjE4ODU0MjA4MDAsInN1YiI6IjEwNzg5NjU4IiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMxNjI2NTMwLCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiZjdkNTczZWYtNWI0Zi00MjU2LWI1OGYtNjE3ODdmN2Q1ZmNlIiwiYXBpX2RvbWFpbiI6ImFwaS1iLmFtb2NybS5ydSJ9.GWNXTAz3_DPtNHZbBAiPkg9k77cwfhAnMZeMIfU15r9XMQ5g6r8EyH90xU4PLluNoi5kRRWxyimVELfuoK8JWS8fSYSEezxjwlPUsp2rBEbAlvD0AVVVtMcjRjicUSQ-qB7avcTHCsOSXR-P-ZkMkGcE0B_2RA-DqsxqYGHxnuQHtzDSmw8lgnl0aVrbBULhVIZEAK7gTufQTWJDDmcMttEYqYU-Bd2XReJ0f96K6k68b7CErnjp-uyRmjLEgKhkpdsF8Cx6bioqACXUqSPUNRmd6sRTU5RYC3J3SlTJONcx6TFToAfnXof0cjwnlxluetl8rwafrAulTr1kTrJeXQ"

# Типы примечаний, которые содержат сообщения
MESSAGE_NOTE_TYPES = [
    'common',           # Обычные примечания
    'call_in',          # Входящие звонки
    'call_out',         # Исходящие звонки
    'service_message',  # Служебные сообщения
    'mail_message',     # Email сообщения
    'sms_in',          # Входящие SMS
    'sms_out',         # Исходящие SMS
    'message_cashier'   # Сообщения кассира
]

class AmoCRMExporter:
    def __init__(self, subdomain: str, access_token: str):
        self.subdomain = subdomain
        self.access_token = access_token
        self.base_url = f"https://{subdomain}.amocrm.ru/api/v4"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        self.stats = {
            'leads_processed': 0,
            'notes_found': 0,
            'messages_extracted': 0,
            'api_requests': 0,
            'errors': 0
        }
    
    def make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Выполняет запрос к API amoCRM с обработкой ошибок"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            self.stats['api_requests'] += 1
            response = requests.get(url, headers=self.headers, params=params)
            
            # Обработка лимитов API
            if response.status_code == 429:
                print("⚠️ Достигнут лимит API, ожидание 1 секунды...")
                time.sleep(1)
                return self.make_request(endpoint, params)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка API запроса к {endpoint}: {e}")
            self.stats['errors'] += 1
            return None
    
    def get_all_leads(self, limit: int = None) -> List[Dict]:
        """Получает список всех сделок"""
        print("📋 Получение списка сделок...")
        
        leads = []
        page = 1
        
        while True:
            params = {
                'page': page,
                'limit': 250  # Максимум за запрос
            }
            
            if limit and len(leads) >= limit:
                break
            
            data = self.make_request("leads", params)
            if not data or '_embedded' not in data or 'leads' not in data['_embedded']:
                break
            
            page_leads = data['_embedded']['leads']
            if not page_leads:
                break
            
            leads.extend(page_leads)
            print(f"  📄 Страница {page}: получено {len(page_leads)} сделок")
            
            # Если есть лимит, обрезаем список
            if limit and len(leads) >= limit:
                leads = leads[:limit]
                break
            
            page += 1
            time.sleep(0.2)  # Небольшая пауза между запросами
        
        print(f"✅ Всего получено сделок: {len(leads)}")
        return leads
    
    def get_lead_notes(self, lead_id: int) -> List[Dict]:
        """Получает все примечания для конкретной сделки"""
        notes = []
        page = 1
        
        while True:
            params = {
                'page': page,
                'limit': 250
            }
            
            data = self.make_request(f"leads/{lead_id}/notes", params)
            if not data or '_embedded' not in data or 'notes' not in data['_embedded']:
                break
            
            page_notes = data['_embedded']['notes']
            if not page_notes:
                break
            
            notes.extend(page_notes)
            page += 1
            time.sleep(0.1)  # Пауза между запросами
        
        return notes
    
    def extract_message_from_note(self, note: Dict) -> Optional[Dict]:
        """Извлекает текст сообщения из примечания"""
        note_type = note.get('note_type', '')
        
        # Проверяем, содержит ли примечание сообщение
        if note_type not in MESSAGE_NOTE_TYPES:
            return None
        
        # Извлекаем текст в зависимости от типа примечания
        text = None
        sender_type = 'unknown'
        
        if 'params' in note:
            params = note['params']
            
            if note_type == 'common':
                text = params.get('text', '')
                sender_type = 'client'  # Обычно обычные примечания от клиентов
                
            elif note_type in ['call_in', 'call_out']:
                # Для звонков может быть описание разговора
                text = params.get('text', '') or f"Звонок ({note_type})"
                sender_type = 'client' if note_type == 'call_in' else 'assistant'
                
            elif note_type in ['sms_in', 'sms_out']:
                text = params.get('text', '')
                sender_type = 'client' if note_type == 'sms_in' else 'assistant'
                
            elif note_type == 'mail_message':
                text = params.get('text', '') or params.get('subject', '')
                sender_type = 'client'  # Обычно входящие письма
                
            elif note_type == 'service_message':
                text = params.get('text', '')
                sender_type = 'system'
        
        if not text or not text.strip():
            return None
        
        return {
            'id': note['id'],
            'text': text.strip(),
            'sender_type': sender_type,
            'note_type': note_type,
            'created_at': note.get('created_at', 0),
            'updated_at': note.get('updated_at', 0),
            'created_by': note.get('created_by', 0)
        }
    
    def export_lead_history(self, lead_id: int) -> Dict:
        """Экспортирует историю переписки для одной сделки"""
        print(f"📝 Обработка сделки {lead_id}...")
        
        notes = self.get_lead_notes(lead_id)
        self.stats['notes_found'] += len(notes)
        
        messages = []
        for note in notes:
            message = self.extract_message_from_note(note)
            if message:
                messages.append(message)
                self.stats['messages_extracted'] += 1
        
        # Сортируем сообщения по времени создания
        messages.sort(key=lambda x: x['created_at'])
        
        print(f"  📋 Найдено примечаний: {len(notes)}")
        print(f"  💬 Извлечено сообщений: {len(messages)}")
        
        return {
            'lead_id': lead_id,
            'total_notes': len(notes),
            'messages': messages,
            'exported_at': int(datetime.now().timestamp())
        }
    
    def export_all_history(self, output_file: str = 'amocrm_history.json', limit: int = None) -> bool:
        """Экспортирует историю переписки для всех сделок"""
        print("🚀 ЭКСПОРТ ИСТОРИИ ПЕРЕПИСКИ ИЗ AMOCRM")
        print("=" * 60)
        
        # Получаем список сделок
        leads = self.get_all_leads(limit)
        if not leads:
            print("❌ Не удалось получить список сделок")
            return False
        
        # Экспортируем историю для каждой сделки
        export_data = {
            'export_info': {
                'subdomain': self.subdomain,
                'exported_at': datetime.now().isoformat(),
                'total_leads': len(leads),
                'api_requests': 0,
                'version': '1.0'
            },
            'leads': []
        }
        
        for i, lead in enumerate(leads, 1):
            lead_id = lead['id']
            print(f"\\n📊 Прогресс: {i}/{len(leads)} ({i/len(leads)*100:.1f}%)")
            
            lead_history = self.export_lead_history(lead_id)
            export_data['leads'].append(lead_history)
            
            self.stats['leads_processed'] += 1
            
            # Небольшая пауза между сделками
            time.sleep(0.3)
        
        # Обновляем статистику в экспорте
        export_data['export_info']['api_requests'] = self.stats['api_requests']
        export_data['export_info']['stats'] = self.stats
        
        # Сохраняем в файл
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"\\n✅ Экспорт завершен успешно!")
            print(f"📁 Файл сохранен: {output_file}")
            self.print_stats()
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при сохранении файла: {e}")
            return False
    
    def print_stats(self):
        """Выводит статистику экспорта"""
        print("\\n📊 СТАТИСТИКА ЭКСПОРТА:")
        print("=" * 40)
        print(f"📋 Обработано сделок: {self.stats['leads_processed']}")
        print(f"📝 Найдено примечаний: {self.stats['notes_found']}")
        print(f"💬 Извлечено сообщений: {self.stats['messages_extracted']}")
        print(f"🌐 API запросов: {self.stats['api_requests']}")
        print(f"❌ Ошибок: {self.stats['errors']}")

def main():
    parser = argparse.ArgumentParser(description='Экспорт истории переписки из amoCRM')
    parser.add_argument('--output', '-o', default='amocrm_history.json', 
                       help='Имя выходного файла (по умолчанию: amocrm_history.json)')
    parser.add_argument('--limit', '-l', type=int, 
                       help='Ограничить количество сделок для экспорта (для тестирования)')
    parser.add_argument('--lead-id', type=int,
                       help='Экспортировать только одну конкретную сделку')
    
    args = parser.parse_args()
    
    # Создаем экспортер
    exporter = AmoCRMExporter(SUBDOMAIN, ACCESS_TOKEN)
    
    if args.lead_id:
        # Экспорт одной сделки
        print(f"🎯 Экспорт сделки {args.lead_id}")
        lead_history = exporter.export_lead_history(args.lead_id)
        
        export_data = {
            'export_info': {
                'subdomain': SUBDOMAIN,
                'exported_at': datetime.now().isoformat(),
                'total_leads': 1,
                'single_lead_export': True,
                'version': '1.0'
            },
            'leads': [lead_history]
        }
        
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            print(f"✅ Экспорт сделки {args.lead_id} завершен: {args.output}")
        except Exception as e:
            print(f"❌ Ошибка при сохранении: {e}")
    else:
        # Экспорт всех сделок
        success = exporter.export_all_history(args.output, args.limit)
        if not success:
            exit(1)

if __name__ == '__main__':
    main()

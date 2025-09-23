#!/usr/bin/env python3
"""
Инструмент для импорта истории переписки из amoCRM в базу данных
Читает JSON файл, созданный export_amocrm_history.py, и импортирует данные в SQLite базу
"""

import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional
from database_manager import DatabaseManager

class HistoryImporter:
    def __init__(self, db_path: str = 'conversations.db'):
        self.db = DatabaseManager(db_path)
        self.stats = {
            'leads_processed': 0,
            'clients_created': 0,
            'conversations_created': 0,
            'messages_imported': 0,
            'messages_skipped': 0,
            'errors': 0
        }
    
    def load_export_data(self, file_path: str) -> Optional[Dict]:
        """Загружает данные экспорта из JSON файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"📁 Загружен файл: {file_path}")
            
            if 'export_info' in data:
                info = data['export_info']
                print(f"📊 Информация об экспорте:")
                print(f"  🏢 Поддомен: {info.get('subdomain', 'неизвестно')}")
                print(f"  📅 Дата экспорта: {info.get('exported_at', 'неизвестно')}")
                print(f"  📋 Сделок в файле: {info.get('total_leads', 0)}")
            
            return data
            
        except FileNotFoundError:
            print(f"❌ Файл не найден: {file_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка чтения JSON: {e}")
            return None
        except Exception as e:
            print(f"❌ Ошибка загрузки файла: {e}")
            return None
    
    def determine_sender_type(self, message: Dict) -> str:
        """Определяет тип отправителя сообщения"""
        sender_type = message.get('sender_type', 'unknown')
        note_type = message.get('note_type', '')
        
        # Уточняем тип отправителя на основе типа примечания
        if note_type == 'call_in' or note_type == 'sms_in':
            return 'client'
        elif note_type == 'call_out' or note_type == 'sms_out':
            return 'assistant'
        elif note_type == 'service_message':
            return 'system'
        elif sender_type in ['client', 'assistant', 'system']:
            return sender_type
        else:
            # По умолчанию считаем, что это сообщение от клиента
            return 'client'
    
    def import_lead_history(self, lead_data: Dict) -> bool:
        """Импортирует историю переписки для одной сделки"""
        lead_id = lead_data['lead_id']
        messages = lead_data.get('messages', [])
        
        if not messages:
            print(f"  ⚠️ Сделка {lead_id}: нет сообщений для импорта")
            return True
        
        try:
            # Создаем или находим клиента
            client_id = self.db.get_or_create_client(
                amocrm_contact_id=lead_id,
                name=f"Клиент из сделки {lead_id}"
            )
            
            if client_id is None:
                print(f"❌ Не удалось создать клиента для сделки {lead_id}")
                self.stats['errors'] += 1
                return False
            
            # Проверяем, новый ли это клиент (упрощенная проверка)
            # В данном случае мы не можем легко проверить, был ли создан новый клиент
            # поэтому просто увеличиваем счетчик при первом обращении к клиенту
            
            # Создаем или находим разговор
            conversation_id = self.db.get_or_create_conversation(
                client_id=client_id,
                amocrm_lead_id=lead_id
            )
            
            if conversation_id is None:
                print(f"❌ Не удалось создать разговор для сделки {lead_id}")
                self.stats['errors'] += 1
                return False
            
            # Проверяем, новый ли это разговор (упрощенная проверка)
            # Аналогично с разговорами - увеличиваем счетчик при первом обращении
            
            # Проверяем, есть ли уже сообщения в этом разговоре
            existing_messages = self.db.get_conversation_context(conversation_id, limit=1)
            if existing_messages:
                print(f"  ⚠️ Сделка {lead_id}: разговор уже содержит сообщения, пропускаем")
                self.stats['messages_skipped'] += len(messages)
                return True
            
            # Импортируем сообщения
            imported_count = 0
            for message in messages:
                sender_type = self.determine_sender_type(message)
                
                # Создаем метаданные
                metadata = {
                    'amocrm_lead_id': lead_id,
                    'amocrm_note_id': message.get('id'),
                    'note_type': message.get('note_type'),
                    'amocrm_timestamp': message.get('created_at', 0),
                    'source': 'history_import',
                    'created_by': message.get('created_by')
                }
                
                # Добавляем сообщение в базу
                message_id = self.db.add_message(
                    conversation_id=conversation_id,
                    sender_type=sender_type,
                    content=message['text'],
                    message_type='text',
                    metadata=metadata
                )
                
                if message_id:
                    imported_count += 1
                    self.stats['messages_imported'] += 1
                else:
                    print(f"  ⚠️ Не удалось импортировать сообщение: {message['text'][:50]}...")
                    self.stats['errors'] += 1
            
            print(f"  ✅ Сделка {lead_id}: импортировано {imported_count}/{len(messages)} сообщений")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при импорте сделки {lead_id}: {e}")
            self.stats['errors'] += 1
            return False
    
    def import_history(self, file_path: str, dry_run: bool = False) -> bool:
        """Импортирует всю историю переписки из файла"""
        print("📥 ИМПОРТ ИСТОРИИ ПЕРЕПИСКИ В БАЗУ ДАННЫХ")
        print("=" * 60)
        
        if dry_run:
            print("🧪 РЕЖИМ ТЕСТИРОВАНИЯ (изменения не будут сохранены)")
            print("=" * 60)
        
        # Загружаем данные экспорта
        export_data = self.load_export_data(file_path)
        if not export_data:
            return False
        
        leads = export_data.get('leads', [])
        if not leads:
            print("❌ В файле нет данных о сделках")
            return False
        
        print(f"\\n📋 Начинаем импорт {len(leads)} сделок...")
        
        # Импортируем каждую сделку
        for i, lead_data in enumerate(leads, 1):
            lead_id = lead_data['lead_id']
            message_count = len(lead_data.get('messages', []))
            
            print(f"\\n📊 Прогресс: {i}/{len(leads)} ({i/len(leads)*100:.1f}%)")
            print(f"📝 Сделка {lead_id}: {message_count} сообщений")
            
            if not dry_run:
                success = self.import_lead_history(lead_data)
                if not success:
                    print(f"⚠️ Ошибка при импорте сделки {lead_id}")
            else:
                # В режиме тестирования просто показываем что будет импортировано
                print(f"  🧪 Будет импортировано: {message_count} сообщений")
                self.stats['messages_imported'] += message_count
            
            self.stats['leads_processed'] += 1
        
        if not dry_run:
            # Изменения автоматически коммитятся в DatabaseManager
            pass
        
        print(f"\\n✅ Импорт завершен!")
        self.print_stats()
        return True
    
    def print_stats(self):
        """Выводит статистику импорта"""
        print("\\n📊 СТАТИСТИКА ИМПОРТА:")
        print("=" * 40)
        print(f"📋 Обработано сделок: {self.stats['leads_processed']}")
        print(f"👥 Создано клиентов: {self.stats['clients_created']}")
        print(f"💬 Создано разговоров: {self.stats['conversations_created']}")
        print(f"📝 Импортировано сообщений: {self.stats['messages_imported']}")
        print(f"⏭️ Пропущено сообщений: {self.stats['messages_skipped']}")
        print(f"❌ Ошибок: {self.stats['errors']}")
    
    def check_import_status(self) -> Dict:
        """Проверяет текущее состояние базы данных"""
        print("🔍 ПРОВЕРКА СОСТОЯНИЯ БАЗЫ ДАННЫХ")
        print("=" * 50)
        
        # Получаем статистику из базы
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Количество клиентов
            cursor.execute("SELECT COUNT(*) FROM clients")
            clients_count = cursor.fetchone()[0]
            
            # Количество разговоров
            cursor.execute("SELECT COUNT(*) FROM conversations")
            conversations_count = cursor.fetchone()[0]
            
            # Количество сообщений
            cursor.execute("SELECT COUNT(*) FROM messages")
            messages_count = cursor.fetchone()[0]
            
            # Сообщения по типам отправителей
            cursor.execute("""
                SELECT sender_type, COUNT(*) 
                FROM messages 
                GROUP BY sender_type
            """)
            sender_stats = dict(cursor.fetchall())
            
            # Разговоры с сообщениями
            cursor.execute("""
                SELECT COUNT(DISTINCT conversation_id) 
                FROM messages
            """)
            active_conversations = cursor.fetchone()[0]
        
        print(f"👥 Всего клиентов: {clients_count}")
        print(f"💬 Всего разговоров: {conversations_count}")
        print(f"📝 Всего сообщений: {messages_count}")
        print(f"🔄 Активных разговоров: {active_conversations}")
        
        print("\\n📊 Сообщения по типам отправителей:")
        for sender_type, count in sender_stats.items():
            icon = "👤" if sender_type == "client" else "🤖" if sender_type == "assistant" else "⚙️"
            print(f"  {icon} {sender_type}: {count}")
        
        return {
            'clients': clients_count,
            'conversations': conversations_count,
            'messages': messages_count,
            'active_conversations': active_conversations,
            'sender_stats': sender_stats
        }

def main():
    parser = argparse.ArgumentParser(description='Импорт истории переписки из amoCRM в базу данных')
    parser.add_argument('file', nargs='?', default='amocrm_history.json',
                       help='JSON файл с экспортированной историей')
    parser.add_argument('--db', '-d', default='conversations.db',
                       help='Путь к файлу базы данных (по умолчанию: conversations.db)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Режим тестирования (не вносить изменения в базу)')
    parser.add_argument('--status', action='store_true',
                       help='Показать текущее состояние базы данных')
    
    args = parser.parse_args()
    
    # Создаем импортер
    importer = HistoryImporter(args.db)
    
    if args.status:
        # Показываем статус базы данных
        importer.check_import_status()
    else:
        # Выполняем импорт
        success = importer.import_history(args.file, args.dry_run)
        if not success:
            exit(1)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Просмотр содержимого базы данных с историей переписки
"""

import sqlite3
from datetime import datetime
import json

def view_database(db_path='conversations.db'):
    """Показывает содержимое базы данных"""
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("📊 СОДЕРЖИМОЕ БАЗЫ ДАННЫХ")
        print("=" * 80)
        
        # Клиенты
        print("\\n👥 КЛИЕНТЫ:")
        cursor.execute("SELECT * FROM clients ORDER BY created_at")
        clients = cursor.fetchall()
        
        if clients:
            for client in clients:
                print(f"  ID: {client['id']} | AmoCRM Contact: {client['amocrm_contact_id']} | Имя: {client['name']}")
        else:
            print("  Нет клиентов")
        
        # Разговоры
        print("\\n💬 РАЗГОВОРЫ:")
        cursor.execute("""
            SELECT c.*, cl.name as client_name 
            FROM conversations c 
            JOIN clients cl ON c.client_id = cl.id 
            ORDER BY c.created_at
        """)
        conversations = cursor.fetchall()
        
        if conversations:
            for conv in conversations:
                print(f"  ID: {conv['id']} | Клиент: {conv['client_name']} | AmoCRM Lead: {conv['amocrm_lead_id']} | Статус: {conv['status']}")
        else:
            print("  Нет разговоров")
        
        # Сообщения по разговорам
        print("\\n📝 ИСТОРИЯ СООБЩЕНИЙ:")
        
        for conv in conversations:
            print(f"\\n🗂️ Разговор {conv['id']} (AmoCRM Lead: {conv['amocrm_lead_id']}):")
            
            cursor.execute("""
                SELECT * FROM messages 
                WHERE conversation_id = ? 
                ORDER BY timestamp
            """, (conv['id'],))
            messages = cursor.fetchall()
            
            if messages:
                for msg in messages:
                    sender_icon = "👤" if msg['sender_type'] == 'client' else "🤖"
                    timestamp = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
                    
                    print(f"    {sender_icon} {msg['sender_type'].upper()}: {msg['content']}")
                    print(f"       📅 {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    if msg['metadata']:
                        try:
                            metadata = json.loads(msg['metadata'])
                            print(f"       📋 Метаданные: {metadata}")
                        except:
                            print(f"       📋 Метаданные: {msg['metadata']}")
                    print()
            else:
                print("    Нет сообщений")
        
        # Статистика
        print("\\n📈 СТАТИСТИКА:")
        
        cursor.execute("SELECT COUNT(*) as count FROM clients")
        clients_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM conversations")
        conversations_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM messages")
        messages_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM messages WHERE sender_type = 'client'")
        client_messages = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM messages WHERE sender_type = 'assistant'")
        assistant_messages = cursor.fetchone()['count']
        
        print(f"  👥 Всего клиентов: {clients_count}")
        print(f"  💬 Всего разговоров: {conversations_count}")
        print(f"  📝 Всего сообщений: {messages_count}")
        print(f"  👤 Сообщений от клиентов: {client_messages}")
        print(f"  🤖 Ответов ассистента: {assistant_messages}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
    except FileNotFoundError:
        print(f"❌ Файл базы данных не найден: {db_path}")
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")

def search_messages_by_lead(lead_id, db_path='conversations.db'):
    """Поиск всех сообщений по ID сделки"""
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print(f"🔍 ПОИСК СООБЩЕНИЙ ДЛЯ СДЕЛКИ {lead_id}")
        print("=" * 60)
        
        cursor.execute("""
            SELECT m.*, c.amocrm_lead_id, cl.name as client_name
            FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            JOIN clients cl ON c.client_id = cl.id
            WHERE c.amocrm_lead_id = ?
            ORDER BY m.timestamp
        """, (lead_id,))
        
        messages = cursor.fetchall()
        
        if messages:
            print(f"Найдено {len(messages)} сообщений:")
            print()
            
            for msg in messages:
                sender_icon = "👤" if msg['sender_type'] == 'client' else "🤖"
                timestamp = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
                
                print(f"{sender_icon} {msg['sender_type'].upper()}: {msg['content']}")
                print(f"   📅 {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
        else:
            print(f"Сообщений для сделки {lead_id} не найдено")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Поиск по конкретной сделке
        lead_id = int(sys.argv[1])
        search_messages_by_lead(lead_id)
    else:
        # Показать всю базу данных
        view_database()

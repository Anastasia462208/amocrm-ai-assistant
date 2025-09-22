#!/usr/bin/env python3
"""
Database Manager for AI Assistant Conversation System
Handles all database operations for managing 200+ parallel conversations
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager
import threading

class DatabaseManager:
    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_database()
        
    def init_database(self):
        """Initialize database with schema"""
        with self.get_connection() as conn:
            # Check if tables exist
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='clients'
            """)
            
            if cursor.fetchone():
                logging.info("Database already initialized")
                return
            
            # Read and execute schema
            try:
                with open('database_schema.sql', 'r', encoding='utf-8') as f:
                    schema = f.read()
                conn.executescript(schema)
                logging.info("Database initialized successfully")
            except FileNotFoundError:
                logging.error("database_schema.sql not found")
                raise
    
    @contextmanager
    def get_connection(self):
        """Thread-safe database connection context manager"""
        with self.lock:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
    
    # Client Management
    def get_or_create_client(self, amocrm_contact_id: int, name: str = None, 
                           phone: str = None, email: str = None) -> int:
        """Get existing client or create new one"""
        with self.get_connection() as conn:
            # Try to find existing client
            cursor = conn.execute(
                "SELECT id FROM clients WHERE amocrm_contact_id = ?",
                (amocrm_contact_id,)
            )
            row = cursor.fetchone()
            
            if row:
                # Update client info if provided
                if any([name, phone, email]):
                    conn.execute("""
                        UPDATE clients 
                        SET name = COALESCE(?, name),
                            phone = COALESCE(?, phone),
                            email = COALESCE(?, email),
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (name, phone, email, row['id']))
                return row['id']
            else:
                # Create new client
                cursor = conn.execute("""
                    INSERT INTO clients (amocrm_contact_id, name, phone, email)
                    VALUES (?, ?, ?, ?)
                """, (amocrm_contact_id, name, phone, email))
                return cursor.lastrowid
    
    # Conversation Management
    def get_or_create_conversation(self, client_id: int, amocrm_lead_id: int = None) -> int:
        """Get active conversation or create new one"""
        with self.get_connection() as conn:
            # Look for active conversation
            cursor = conn.execute("""
                SELECT id FROM conversations 
                WHERE client_id = ? AND status = 'active'
                ORDER BY last_activity DESC LIMIT 1
            """, (client_id,))
            row = cursor.fetchone()
            
            if row:
                # Update last activity
                conn.execute("""
                    UPDATE conversations 
                    SET last_activity = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (row['id'],))
                return row['id']
            else:
                # Create new conversation
                cursor = conn.execute("""
                    INSERT INTO conversations (client_id, amocrm_lead_id, status)
                    VALUES (?, ?, 'active')
                """, (client_id, amocrm_lead_id))
                return cursor.lastrowid
    
    def get_conversation_context(self, conversation_id: int, limit: int = 20) -> List[Dict]:
        """Get recent messages for conversation context"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT sender_type, content, message_type, metadata, timestamp
                FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (conversation_id, limit))
            
            messages = []
            for row in cursor.fetchall():
                message = dict(row)
                if message['metadata']:
                    message['metadata'] = json.loads(message['metadata'])
                messages.append(message)
            
            return list(reversed(messages))  # Return in chronological order
    
    def update_conversation_summary(self, conversation_id: int, summary: str):
        """Update conversation context summary"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE conversations 
                SET context_summary = ?, last_activity = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (summary, conversation_id))
    
    # Message Management
    def add_message(self, conversation_id: int, sender_type: str, content: str,
                   message_type: str = 'text', metadata: Dict = None) -> int:
        """Add new message to conversation"""
        metadata_json = json.dumps(metadata) if metadata else None
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO messages (conversation_id, sender_type, content, message_type, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (conversation_id, sender_type, content, message_type, metadata_json))
            
            # Update conversation last activity
            conn.execute("""
                UPDATE conversations 
                SET last_activity = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (conversation_id,))
            
            return cursor.lastrowid
    
    # AI Task Management
    def create_ai_task(self, conversation_id: int, task_type: str, prompt: str,
                      api_provider: str = 'openai') -> int:
        """Create new AI task"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO ai_tasks (conversation_id, task_type, prompt, api_provider, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (conversation_id, task_type, prompt, api_provider))
            return cursor.lastrowid
    
    def update_ai_task(self, task_id: int, response: str = None, status: str = None,
                      api_task_id: str = None, processing_time_ms: int = None):
        """Update AI task with response"""
        with self.get_connection() as conn:
            updates = []
            params = []
            
            if response is not None:
                updates.append("response = ?")
                params.append(response)
            
            if status is not None:
                updates.append("status = ?")
                params.append(status)
                
            if status == 'completed':
                updates.append("completed_at = CURRENT_TIMESTAMP")
            
            if api_task_id is not None:
                updates.append("api_task_id = ?")
                params.append(api_task_id)
            
            if processing_time_ms is not None:
                updates.append("processing_time_ms = ?")
                params.append(processing_time_ms)
            
            if updates:
                params.append(task_id)
                conn.execute(f"""
                    UPDATE ai_tasks 
                    SET {', '.join(updates)}
                    WHERE id = ?
                """, params)
    
    # Knowledge Base Management
    def search_knowledge_base(self, query: str, category: str = None, limit: int = 5) -> List[Dict]:
        """Search knowledge base for relevant information"""
        with self.get_connection() as conn:
            query_words = query.lower().split()
            
            if category:
                cursor = conn.execute("""
                    SELECT title, content, category, priority
                    FROM knowledge_base
                    WHERE category = ? AND is_active = 1
                    ORDER BY priority DESC, id
                    LIMIT ?
                """, (category, limit))
            else:
                # Search by keywords
                like_conditions = []
                params = []
                for word in query_words:
                    like_conditions.append("(LOWER(keywords) LIKE ? OR LOWER(content) LIKE ?)")
                    params.extend([f"%{word}%", f"%{word}%"])
                
                if like_conditions:
                    params.append(limit)
                    cursor = conn.execute(f"""
                        SELECT title, content, category, priority
                        FROM knowledge_base
                        WHERE is_active = 1 AND ({' OR '.join(like_conditions)})
                        ORDER BY priority DESC, id
                        LIMIT ?
                    """, params)
                else:
                    return []
            
            return [dict(row) for row in cursor.fetchall()]
    
    # Booking Management
    def create_booking_request(self, conversation_id: int, tour_name: str = None,
                             tour_date: str = None, participants_count: int = None,
                             client_preferences: str = None) -> int:
        """Create new booking request"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO booking_requests 
                (conversation_id, tour_name, tour_date, participants_count, client_preferences)
                VALUES (?, ?, ?, ?, ?)
            """, (conversation_id, tour_name, tour_date, participants_count, client_preferences))
            return cursor.lastrowid
    
    def update_booking_request(self, booking_id: int, **kwargs):
        """Update booking request"""
        with self.get_connection() as conn:
            updates = []
            params = []
            
            for key, value in kwargs.items():
                if value is not None:
                    updates.append(f"{key} = ?")
                    params.append(value)
            
            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(booking_id)
                conn.execute(f"""
                    UPDATE booking_requests 
                    SET {', '.join(updates)}
                    WHERE id = ?
                """, params)
    
    # System Configuration
    def get_config(self, key: str) -> Optional[str]:
        """Get system configuration value"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT config_value FROM system_config WHERE config_key = ?",
                (key,)
            )
            row = cursor.fetchone()
            return row['config_value'] if row else None
    
    def set_config(self, key: str, value: str, description: str = None):
        """Set system configuration value"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO system_config (config_key, config_value, description, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, value, description))
    
    # Performance Monitoring
    def log_performance_metric(self, metric_name: str, metric_value: float, additional_data: Dict = None):
        """Log performance metric"""
        additional_json = json.dumps(additional_data) if additional_data else None
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO performance_metrics (metric_name, metric_value, additional_data)
                VALUES (?, ?, ?)
            """, (metric_name, metric_value, additional_json))
    
    def get_active_conversations_count(self) -> int:
        """Get number of currently active conversations"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) as count
                FROM conversations
                WHERE status = 'active' 
                AND last_activity > datetime('now', '-1 hour')
            """)
            return cursor.fetchone()['count']
    
    def cleanup_old_conversations(self, days: int = 7):
        """Mark old conversations as completed"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE conversations 
                SET status = 'completed'
                WHERE status = 'active' 
                AND last_activity < datetime('now', '-{} days')
            """.format(days))
            
            affected = conn.total_changes
            logging.info(f"Cleaned up {affected} old conversations")
            return affected

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize database manager
    db = DatabaseManager("test_conversations.db")
    
    # Test client creation
    client_id = db.get_or_create_client(
        amocrm_contact_id=12345,
        name="Иван Петров",
        phone="+7-900-123-45-67",
        email="ivan@example.com"
    )
    print(f"Client ID: {client_id}")
    
    # Test conversation creation
    conv_id = db.get_or_create_conversation(client_id, amocrm_lead_id=67890)
    print(f"Conversation ID: {conv_id}")
    
    # Test message adding
    msg_id = db.add_message(conv_id, "client", "Здравствуйте! Интересует сплав по Чусовой")
    print(f"Message ID: {msg_id}")
    
    # Test knowledge base search
    kb_results = db.search_knowledge_base("чусовая сплав")
    print(f"Knowledge base results: {len(kb_results)}")
    for result in kb_results:
        print(f"- {result['title']}")
    
    # Test performance metrics
    db.log_performance_metric("response_time_ms", 250.5)
    
    print(f"Active conversations: {db.get_active_conversations_count()}")
    print("Database manager test completed successfully!")

#!/usr/bin/env python3
"""
Conversation Context Management System
Handles context preservation and intelligent conversation flow for 20+ parallel conversations
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from database_manager import DatabaseManager
import re

class ConversationContextManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Context analysis patterns
        self.intent_patterns = {
            'booking_inquiry': [
                r'забронировать', r'бронирование', r'заказать', r'записаться',
                r'хочу поехать', r'планирую', r'интересует тур'
            ],
            'price_inquiry': [
                r'сколько стоит', r'цена', r'стоимость', r'цены',
                r'во сколько обойдется', r'прайс'
            ],
            'tour_comparison': [
                r'сравни', r'что лучше', r'какой выбрать', r'посоветуй',
                r'чем отличается', r'разница между'
            ],
            'equipment_inquiry': [
                r'снаряжение', r'что взять', r'экипировка', r'одежда',
                r'что нужно', r'что брать с собой'
            ],
            'safety_inquiry': [
                r'безопасность', r'опасно', r'риски', r'страховка',
                r'безопасно ли', r'что если'
            ],
            'logistics_inquiry': [
                r'как добраться', r'трансфер', r'где встреча',
                r'откуда старт', r'логистика'
            ],
            'date_inquiry': [
                r'когда', r'даты', r'расписание', r'график',
                r'в июне', r'в июле', r'летом'
            ]
        }
        
        # Context states for conversation flow
        self.conversation_states = {
            'initial': 'Начальное состояние',
            'tour_selection': 'Выбор тура',
            'details_discussion': 'Обсуждение деталей',
            'booking_process': 'Процесс бронирования',
            'confirmation': 'Подтверждение',
            'completed': 'Завершено'
        }
    
    def analyze_message_intent(self, message: str) -> List[str]:
        """Analyze message to determine user intent"""
        message_lower = message.lower()
        detected_intents = []
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    detected_intents.append(intent)
                    break
        
        return detected_intents
    
    def extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities from message (dates, numbers, tour names, etc.)"""
        entities = {}
        message_lower = message.lower()
        
        # Extract tour names
        tour_patterns = {
            'чусовая': r'чусов[а-я]*',
            'серга': r'серг[а-я]*'
        }
        
        for tour, pattern in tour_patterns.items():
            if re.search(pattern, message_lower):
                entities['tour_name'] = tour
                break
        
        # Extract numbers (participants, days, prices)
        numbers = re.findall(r'\b(\d+)\b', message)
        if numbers:
            entities['numbers'] = [int(n) for n in numbers]
        
        # Extract months
        months = {
            'январь': 1, 'февраль': 2, 'март': 3, 'апрель': 4,
            'май': 5, 'июнь': 6, 'июль': 7, 'август': 8,
            'сентябрь': 9, 'октябрь': 10, 'ноябрь': 11, 'декабрь': 12
        }
        
        for month_name, month_num in months.items():
            if month_name in message_lower:
                entities['month'] = month_num
                entities['month_name'] = month_name
                break
        
        # Extract participant types
        participant_patterns = {
            'adults': r'взрослы[х|е]',
            'children': r'дет[е|и|ей]',
            'family': r'семь[я|ей]'
        }
        
        for participant_type, pattern in participant_patterns.items():
            if re.search(pattern, message_lower):
                if 'participants' not in entities:
                    entities['participants'] = []
                entities['participants'].append(participant_type)
        
        return entities
    
    def update_conversation_context(self, conversation_id: int, message: str, 
                                  sender_type: str) -> Dict[str, Any]:
        """Update conversation context with new message"""
        
        # Analyze message if from client
        context_update = {
            'timestamp': datetime.now().isoformat(),
            'sender_type': sender_type,
            'message_length': len(message)
        }
        
        if sender_type == 'client':
            # Analyze intent and entities
            intents = self.analyze_message_intent(message)
            entities = self.extract_entities(message)
            
            context_update.update({
                'intents': intents,
                'entities': entities
            })
            
            # Update conversation state based on intents
            new_state = self._determine_conversation_state(conversation_id, intents)
            if new_state:
                context_update['conversation_state'] = new_state
        
        # Get current context
        current_context = self.get_conversation_context_summary(conversation_id)
        
        # Update context in database
        self._update_context_metadata(conversation_id, context_update)
        
        return context_update
    
    def _determine_conversation_state(self, conversation_id: int, intents: List[str]) -> Optional[str]:
        """Determine new conversation state based on intents"""
        
        # Get current messages to understand conversation flow
        messages = self.db.get_conversation_context(conversation_id, limit=5)
        
        if not messages:
            return 'initial'
        
        # State transition logic
        if 'booking_inquiry' in intents:
            return 'booking_process'
        elif any(intent in intents for intent in ['tour_comparison', 'price_inquiry']):
            return 'tour_selection'
        elif any(intent in intents for intent in ['equipment_inquiry', 'safety_inquiry', 'logistics_inquiry']):
            return 'details_discussion'
        
        # Keep current state if no clear transition
        return None
    
    def _update_context_metadata(self, conversation_id: int, context_update: Dict):
        """Update conversation metadata in database"""
        
        # Get existing metadata
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT context_summary FROM conversations WHERE id = ?
            """, (conversation_id,))
            row = cursor.fetchone()
            
            if row and row['context_summary']:
                try:
                    existing_context = json.loads(row['context_summary'])
                except:
                    existing_context = {}
            else:
                existing_context = {}
            
            # Merge updates
            existing_context.update(context_update)
            
            # Update in database
            conn.execute("""
                UPDATE conversations 
                SET context_summary = ?, last_activity = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (json.dumps(existing_context), conversation_id))
    
    def get_conversation_context_summary(self, conversation_id: int) -> Dict[str, Any]:
        """Get comprehensive conversation context summary"""
        
        # Get basic conversation info
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT c.*, cl.name, cl.phone, cl.email
                FROM conversations c
                JOIN clients cl ON c.client_id = cl.id
                WHERE c.id = ?
            """, (conversation_id,))
            conv_row = cursor.fetchone()
            
            if not conv_row:
                return {}
            
            # Parse context summary
            context_summary = {}
            if conv_row['context_summary']:
                try:
                    context_summary = json.loads(conv_row['context_summary'])
                except:
                    pass
            
            # Get recent messages
            messages = self.db.get_conversation_context(conversation_id, limit=10)
            
            # Analyze conversation patterns
            analysis = self._analyze_conversation_patterns(messages)
            
            return {
                'conversation_id': conversation_id,
                'client_info': {
                    'name': conv_row['name'],
                    'phone': conv_row['phone'],
                    'email': conv_row['email']
                },
                'conversation_state': context_summary.get('conversation_state', 'initial'),
                'last_activity': conv_row['last_activity'],
                'message_count': len(messages),
                'detected_intents': context_summary.get('intents', []),
                'extracted_entities': context_summary.get('entities', {}),
                'conversation_analysis': analysis,
                'metadata': context_summary
            }
    
    def _analyze_conversation_patterns(self, messages: List[Dict]) -> Dict[str, Any]:
        """Analyze conversation patterns and trends"""
        
        if not messages:
            return {}
        
        analysis = {
            'total_messages': len(messages),
            'client_messages': len([m for m in messages if m['sender_type'] == 'client']),
            'assistant_messages': len([m for m in messages if m['sender_type'] == 'assistant']),
            'conversation_duration': None,
            'topics_discussed': [],
            'booking_readiness_score': 0
        }
        
        # Calculate conversation duration
        if len(messages) > 1:
            first_msg = datetime.fromisoformat(messages[0]['timestamp'])
            last_msg = datetime.fromisoformat(messages[-1]['timestamp'])
            duration = last_msg - first_msg
            analysis['conversation_duration'] = str(duration)
        
        # Analyze topics and booking readiness
        booking_indicators = 0
        topics = set()
        
        for message in messages:
            if message['sender_type'] == 'client':
                content = message['content'].lower()
                
                # Detect topics
                if 'чусов' in content:
                    topics.add('Чусовая')
                if 'серг' in content:
                    topics.add('Серга')
                if any(word in content for word in ['цена', 'стоимость', 'сколько']):
                    topics.add('Цены')
                if any(word in content for word in ['дата', 'когда', 'июнь', 'июль']):
                    topics.add('Даты')
                if any(word in content for word in ['снаряжение', 'что взять']):
                    topics.add('Снаряжение')
                
                # Booking readiness indicators
                if any(word in content for word in ['забронировать', 'заказать', 'хочу поехать']):
                    booking_indicators += 3
                elif any(word in content for word in ['планирую', 'собираемся']):
                    booking_indicators += 2
                elif any(word in content for word in ['интересует', 'рассматриваю']):
                    booking_indicators += 1
        
        analysis['topics_discussed'] = list(topics)
        analysis['booking_readiness_score'] = min(booking_indicators, 10)  # Max 10
        
        return analysis
    
    def generate_context_aware_prompt(self, conversation_id: int, current_message: str) -> str:
        """Generate context-aware prompt for AI assistant"""
        
        context = self.get_conversation_context_summary(conversation_id)
        
        # Base prompt
        base_prompt = """
Ты профессиональный ассистент турагентства "Все на сплав".

Информация о клиенте и разговоре:
"""
        
        # Add client info if available
        if context.get('client_info', {}).get('name'):
            base_prompt += f"Имя клиента: {context['client_info']['name']}\n"
        
        # Add conversation state
        state = context.get('conversation_state', 'initial')
        base_prompt += f"Этап разговора: {self.conversation_states.get(state, state)}\n"
        
        # Add topics discussed
        topics = context.get('conversation_analysis', {}).get('topics_discussed', [])
        if topics:
            base_prompt += f"Обсуждаемые темы: {', '.join(topics)}\n"
        
        # Add booking readiness
        readiness = context.get('conversation_analysis', {}).get('booking_readiness_score', 0)
        if readiness >= 5:
            base_prompt += "Клиент проявляет высокую готовность к бронированию!\n"
        elif readiness >= 2:
            base_prompt += "Клиент рассматривает возможность бронирования.\n"
        
        # Add extracted entities
        entities = context.get('extracted_entities', {})
        if entities:
            base_prompt += f"Выявленные предпочтения: {json.dumps(entities, ensure_ascii=False)}\n"
        
        # Add recent context
        messages = self.db.get_conversation_context(conversation_id, limit=3)
        if messages:
            base_prompt += "\nПоследние сообщения:\n"
            for msg in messages:
                role = "Клиент" if msg['sender_type'] == 'client' else "Ассистент"
                base_prompt += f"{role}: {msg['content']}\n"
        
        # Current message and instructions
        base_prompt += f"""
Текущий вопрос: {current_message}

Инструкции:
1. Учитывай контекст разговора и предыдущие сообщения
2. Если клиент готов к бронированию - предложи конкретные шаги
3. Отвечай персонализированно, используя имя клиента если известно
4. Предлагай конкретные туры с ценами и датами
5. Будь дружелюбным и профессиональным

Ответь с учетом всего контекста:"""
        
        return base_prompt
    
    def suggest_next_actions(self, conversation_id: int) -> List[str]:
        """Suggest next actions based on conversation context"""
        
        context = self.get_conversation_context_summary(conversation_id)
        suggestions = []
        
        state = context.get('conversation_state', 'initial')
        readiness = context.get('conversation_analysis', {}).get('booking_readiness_score', 0)
        topics = context.get('conversation_analysis', {}).get('topics_discussed', [])
        
        # State-based suggestions
        if state == 'initial':
            suggestions.append("Выяснить предпочтения клиента по турам")
            suggestions.append("Предложить популярные направления")
        
        elif state == 'tour_selection':
            suggestions.append("Предоставить детальную информацию о турах")
            suggestions.append("Сравнить варианты по критериям клиента")
        
        elif state == 'details_discussion':
            if 'Снаряжение' not in topics:
                suggestions.append("Рассказать о необходимом снаряжении")
            suggestions.append("Обсудить логистику и трансфер")
        
        elif state == 'booking_process':
            suggestions.append("Предложить заполнить форму бронирования")
            suggestions.append("Уточнить финальные детали")
        
        # Readiness-based suggestions
        if readiness >= 7:
            suggestions.append("🔥 ПРИОРИТЕТ: Предложить бронирование")
            suggestions.append("Предоставить контакты для быстрого оформления")
        elif readiness >= 4:
            suggestions.append("Узнать что еще нужно для принятия решения")
        
        # Topic-based suggestions
        if not topics:
            suggestions.append("Выяснить интересы клиента")
        elif 'Цены' not in topics:
            suggestions.append("Предоставить информацию о ценах")
        elif 'Даты' not in topics:
            suggestions.append("Обсудить доступные даты")
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def get_conversation_metrics(self, conversation_id: int) -> Dict[str, Any]:
        """Get detailed conversation metrics"""
        
        context = self.get_conversation_context_summary(conversation_id)
        
        return {
            'conversation_health': self._calculate_conversation_health(context),
            'engagement_level': self._calculate_engagement_level(context),
            'conversion_probability': self._calculate_conversion_probability(context),
            'response_quality_score': self._calculate_response_quality(conversation_id),
            'next_actions': self.suggest_next_actions(conversation_id)
        }
    
    def _calculate_conversation_health(self, context: Dict) -> float:
        """Calculate conversation health score (0-1)"""
        score = 0.5  # Base score
        
        analysis = context.get('conversation_analysis', {})
        
        # Message balance
        client_msgs = analysis.get('client_messages', 0)
        assistant_msgs = analysis.get('assistant_messages', 0)
        
        if client_msgs > 0 and assistant_msgs > 0:
            balance = min(client_msgs, assistant_msgs) / max(client_msgs, assistant_msgs)
            score += balance * 0.3
        
        # Topic coverage
        topics = len(analysis.get('topics_discussed', []))
        score += min(topics * 0.1, 0.2)
        
        return min(score, 1.0)
    
    def _calculate_engagement_level(self, context: Dict) -> float:
        """Calculate client engagement level (0-1)"""
        analysis = context.get('conversation_analysis', {})
        
        # Message count
        msg_score = min(analysis.get('client_messages', 0) * 0.1, 0.4)
        
        # Booking readiness
        readiness_score = analysis.get('booking_readiness_score', 0) * 0.06
        
        # Topic diversity
        topic_score = len(analysis.get('topics_discussed', [])) * 0.1
        
        return min(msg_score + readiness_score + topic_score, 1.0)
    
    def _calculate_conversion_probability(self, context: Dict) -> float:
        """Calculate probability of conversion to booking (0-1)"""
        analysis = context.get('conversation_analysis', {})
        
        # Booking readiness is primary factor
        readiness = analysis.get('booking_readiness_score', 0)
        base_score = readiness * 0.08
        
        # State bonus
        state = context.get('conversation_state', 'initial')
        state_bonus = {
            'booking_process': 0.3,
            'details_discussion': 0.2,
            'tour_selection': 0.1,
            'initial': 0
        }.get(state, 0)
        
        # Topic coverage bonus
        topics = analysis.get('topics_discussed', [])
        if 'Цены' in topics and 'Даты' in topics:
            topic_bonus = 0.2
        elif 'Цены' in topics or 'Даты' in topics:
            topic_bonus = 0.1
        else:
            topic_bonus = 0
        
        return min(base_score + state_bonus + topic_bonus, 1.0)
    
    def _calculate_response_quality(self, conversation_id: int) -> float:
        """Calculate average response quality score"""
        # This would analyze assistant responses for quality
        # For now, return a placeholder
        return 0.8

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize with existing database
    db = DatabaseManager("test_conversations.db")
    context_manager = ConversationContextManager(db)
    
    print("🧠 Conversation Context Manager Test")
    print("=" * 50)
    
    # Test message analysis
    test_message = "Планирую семейный сплав по Чусовой на 3 дня в июне для 2 взрослых и 2 детей"
    
    print(f"\nAnalyzing message: '{test_message}'")
    intents = context_manager.analyze_message_intent(test_message)
    entities = context_manager.extract_entities(test_message)
    
    print(f"Detected intents: {intents}")
    print(f"Extracted entities: {entities}")
    
    # Test context update
    conversation_id = 1  # From previous test
    context_update = context_manager.update_conversation_context(
        conversation_id, test_message, 'client'
    )
    print(f"\nContext update: {json.dumps(context_update, ensure_ascii=False, indent=2)}")
    
    # Test context summary
    summary = context_manager.get_conversation_context_summary(conversation_id)
    print(f"\nConversation summary:")
    for key, value in summary.items():
        if key != 'metadata':
            print(f"  {key}: {value}")
    
    # Test suggestions
    suggestions = context_manager.suggest_next_actions(conversation_id)
    print(f"\nSuggested next actions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    # Test metrics
    metrics = context_manager.get_conversation_metrics(conversation_id)
    print(f"\nConversation metrics:")
    for key, value in metrics.items():
        if key != 'next_actions':
            print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")
    
    print("\n✅ Context manager test completed!")

-- Database Schema for AI Assistant Conversation Management
-- Supports 200+ parallel conversations with context preservation

-- Clients table - stores client information from AmoCRM
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amocrm_contact_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversations table - tracks individual conversation sessions
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    amocrm_lead_id INTEGER,
    status VARCHAR(50) DEFAULT 'active', -- active, completed, paused
    context_summary TEXT, -- Brief summary of conversation context
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- Messages table - stores all conversation messages
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    sender_type VARCHAR(20) NOT NULL, -- 'client', 'assistant', 'system'
    content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text', -- text, booking_request, tour_info
    metadata JSON, -- Additional data like tour preferences, booking details
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- AI Tasks table - tracks AI API calls and responses
CREATE TABLE ai_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    task_type VARCHAR(50) NOT NULL, -- 'openai_chat', 'manus_research', 'booking_assist'
    prompt TEXT NOT NULL,
    response TEXT,
    api_provider VARCHAR(50), -- 'openai', 'manus', 'local'
    api_task_id VARCHAR(255), -- External task ID for tracking
    status VARCHAR(50) DEFAULT 'pending', -- pending, completed, failed
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- Knowledge Base table - stores tour information and FAQs
CREATE TABLE knowledge_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category VARCHAR(100) NOT NULL, -- 'tours', 'pricing', 'faq', 'policies'
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    keywords TEXT, -- Comma-separated keywords for search
    priority INTEGER DEFAULT 1, -- Higher priority items shown first
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Booking Requests table - tracks booking form submissions
CREATE TABLE booking_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    tour_name VARCHAR(255),
    tour_date DATE,
    participants_count INTEGER,
    client_preferences TEXT,
    total_price DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'draft', -- draft, submitted, confirmed, cancelled
    jotform_submission_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- System Configuration table - stores API keys and settings
CREATE TABLE system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    is_encrypted BOOLEAN DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance Metrics table - tracks system performance
CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,4),
    measurement_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    additional_data JSON
);

-- Indexes for performance optimization
CREATE INDEX idx_conversations_client_id ON conversations(client_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_last_activity ON conversations(last_activity);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);
CREATE INDEX idx_messages_sender_type ON messages(sender_type);

CREATE INDEX idx_ai_tasks_conversation_id ON ai_tasks(conversation_id);
CREATE INDEX idx_ai_tasks_status ON ai_tasks(status);
CREATE INDEX idx_ai_tasks_created_at ON ai_tasks(created_at);

CREATE INDEX idx_knowledge_base_category ON knowledge_base(category);
CREATE INDEX idx_knowledge_base_keywords ON knowledge_base(keywords);
CREATE INDEX idx_knowledge_base_is_active ON knowledge_base(is_active);

CREATE INDEX idx_booking_requests_conversation_id ON booking_requests(conversation_id);
CREATE INDEX idx_booking_requests_status ON booking_requests(status);

-- Insert initial system configuration
INSERT INTO system_config (config_key, config_value, description) VALUES
('openai_api_key', '', 'OpenAI API key for chat responses'),
('manus_api_key', 'sk-w3WopZM2I_Wxoltnbv0BHXP_ygv3cb53HW3Wa0Myp18ZP_ol1EfrF9gorM4Nl8rycZLLJupyvG_Y80aMtr7gpsgeogoc', 'Manus API key for complex tasks'),
('amocrm_api_url', '', 'AmoCRM API endpoint'),
('amocrm_access_token', '', 'AmoCRM access token'),
('jotform_api_key', '', 'JotForm API key for booking integration'),
('max_parallel_conversations', '200', 'Maximum number of parallel conversations'),
('response_timeout_seconds', '30', 'Maximum time to wait for AI response'),
('context_window_messages', '20', 'Number of recent messages to include in context');

-- Insert sample knowledge base entries
INSERT INTO knowledge_base (category, title, content, keywords, priority) VALUES
('tours', 'Сплав по Чусовой', 'Семейные сплавы по реке Чусовая от 2 до 5 дней. Цены от 15000 рублей. Подходит для начинающих и семей с детьми.', 'чусовая,семейный,сплав,дети,начинающие', 5),
('tours', 'Сплав по Серге', 'Однодневные сплавы по реке Серга. Цены от 3500 рублей. Идеально для первого опыта сплава.', 'серга,однодневный,сплав,новички', 4),
('faq', 'Что взять с собой', 'Необходимо взять: сменную одежду, обувь, которую не жалко намочить, солнцезащитный крем, головной убор.', 'снаряжение,одежда,что взять', 3),
('policies', 'Отмена бронирования', 'Отмена за 7 дней до сплава - полный возврат. За 3-7 дней - 50% возврат. Менее 3 дней - без возврата.', 'отмена,возврат,бронирование', 2);

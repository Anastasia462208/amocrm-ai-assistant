#!/usr/bin/env python3
"""
Configuration template for AmoCRM AI Assistant
Copy this file to config.py and fill in your actual values
"""

# AmoCRM Configuration
AMOCRM_CONFIG = {
    'url': 'https://your-domain.amocrm.ru',  # Replace with your AmoCRM domain
    'login': 'your-login',                   # Replace with your login
    'password': 'your-password',             # Replace with your password
    'check_interval': 10,                    # Seconds between message checks
    'max_parallel_conversations': 20,        # Maximum parallel conversations
}

# Manus API Configuration
MANUS_CONFIG = {
    'api_key': 'sk-your-manus-api-key',     # Replace with your Manus API key
    'base_url': 'https://api.manus.im/v1/tasks',
    'mode': 'fast',                          # 'fast' or 'quality'
    'timeout': 60,                           # Request timeout in seconds
}

# Database Configuration
DATABASE_CONFIG = {
    'path': 'amocrm_conversations.db',       # Database file path
    'backup_interval': 3600,                 # Backup interval in seconds (1 hour)
    'cleanup_days': 30,                      # Days to keep old conversations
}

# Browser Configuration
BROWSER_CONFIG = {
    'headless': False,                       # Set to True for production
    'window_size': (1920, 1080),
    'page_load_timeout': 30,
    'implicit_wait': 10,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',                         # DEBUG, INFO, WARNING, ERROR
    'file': 'amocrm_assistant.log',
    'max_file_size': 10 * 1024 * 1024,      # 10 MB
    'backup_count': 5,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# Response Configuration
RESPONSE_CONFIG = {
    'typing_delay': 1.0,                     # Seconds to simulate typing
    'response_delay_min': 2.0,               # Minimum delay before response
    'response_delay_max': 5.0,               # Maximum delay before response
    'max_response_length': 1000,             # Maximum characters in response
}

# Monitoring Configuration
MONITORING_CONFIG = {
    'health_check_interval': 300,            # Health check every 5 minutes
    'restart_on_error': True,                # Auto-restart on critical errors
    'max_restart_attempts': 3,               # Maximum restart attempts
    'notification_webhook': None,            # Webhook for notifications (optional)
}

# Company Information (for responses)
COMPANY_INFO = {
    'name': 'Все на сплав',
    'website': 'vsenasplav.ru',
    'phone': '+7-XXX-XXX-XX-XX',            # Replace with actual phone
    'email': 'info@vsenasplav.ru',          # Replace with actual email
    'working_hours': '9:00-18:00 (МСК)',
}

# Tour Information
TOURS_INFO = {
    'chusovaya': {
        'name': 'Сплав по Чусовой',
        'duration_days': [2, 3, 5],
        'price_from': 15000,
        'description': 'Семейные сплавы по реке Чусовая. Подходит для начинающих и семей с детьми.',
        'difficulty': 'Легкий',
        'season': 'Май-Сентябрь'
    },
    'serga': {
        'name': 'Сплав по Серге', 
        'duration_days': [1],
        'price_from': 3500,
        'description': 'Однодневные сплавы по реке Серга. Идеально для первого опыта.',
        'difficulty': 'Очень легкий',
        'season': 'Май-Сентябрь'
    }
}

# Security Configuration
SECURITY_CONFIG = {
    'encrypt_database': False,               # Enable database encryption
    'session_timeout': 3600,                # Session timeout in seconds
    'max_login_attempts': 3,                # Maximum login attempts
    'lockout_duration': 300,                # Lockout duration in seconds
}

# Development Configuration
DEV_CONFIG = {
    'debug_mode': False,                     # Enable debug mode
    'test_mode': False,                      # Enable test mode
    'mock_responses': False,                 # Use mock responses for testing
    'save_screenshots': True,                # Save screenshots on errors
}

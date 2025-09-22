#!/usr/bin/env python3
"""
Test Configuration for Real AmoCRM Environment
"""

# Real AmoCRM Configuration for Testing
AMOCRM_CONFIG = {
    'login': 'amoshturm@gmail.com',
    'password': 'GbbT4Z5L',
    'check_interval': 15,  # Longer interval for testing
    'max_parallel_conversations': 1,  # Start with just one conversation
    'target_contact': 'Anastasia',  # Specific contact for testing
}

# Browser Configuration for Testing
BROWSER_CONFIG = {
    'headless': True,  # Use headless for now to avoid conflicts
    'window_size': (1920, 1080),
    'page_load_timeout': 30,
    'implicit_wait': 10,
    'debug_mode': True,  # Enable debug output
    'save_screenshots': True,  # Save screenshots for analysis
}

# Logging Configuration for Testing
LOGGING_CONFIG = {
    'level': 'DEBUG',  # Detailed logging
    'console_output': True,  # Show logs in console
    'file': 'test_assistant.log',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# Test Response Templates (simplified)
TEST_RESPONSE_TEMPLATES = {
    'greeting': [
        "Привет! Это тестовый AI ассистент турагентства 'Все на сплав'. Как дела? 😊"
    ],
    'test_response': [
        "Это тестовое сообщение от AI ассистента. Система работает!"
    ],
    'tours_info': [
        """🚣‍♂️ Наши туры:
        
📍 Чусовая - семейные сплавы 2-5 дней (от 15,000 руб)
📍 Серга - однодневные сплавы (от 3,500 руб)

Что вас интересует?"""
    ],
    'fallback': [
        "Спасибо за сообщение! Это тестовый режим AI ассистента."
    ]
}

# Manus API Configuration (if needed)
MANUS_CONFIG = {
    'api_key': 'sk-w3WopZM2I_Wxoltnbv0BHXP_ygv3cb53HW3Wa0Myp18ZP_ol1EfrF9gorM4Nl8rycZLLJupyvG_Y80aMtr7gpsgeogoc',
    'mode': 'fast',
    'timeout': 60,
    'use_for_testing': False,  # Disable Manus for initial testing
}

# Database Configuration for Testing
DATABASE_CONFIG = {
    'path': 'test_real_conversations.db',
    'backup_on_start': True,
}

# Safety Configuration
SAFETY_CONFIG = {
    'test_mode': True,
    'max_messages_per_session': 5,  # Limit messages in test mode
    'require_confirmation': True,  # Ask before sending messages
    'dry_run': False,  # Set to True to simulate without actually sending
}

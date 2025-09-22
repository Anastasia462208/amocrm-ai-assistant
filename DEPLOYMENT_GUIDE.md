# 🚀 Руководство по развертыванию AmoCRM AI Assistant

## 📋 Обзор проекта

**AmoCRM AI Assistant** - это полностью автоматизированная система для обработки диалогов с клиентами турагентства речных сплавов. Система способна обрабатывать до 20 параллельных диалогов без участия менеджеров.

### 🎯 Ключевые возможности:
- ✅ **Полная автоматизация** - 0% участия менеджеров
- ✅ **20 параллельных диалогов** - готовность к масштабированию до 200
- ✅ **Умные ответы** - анализ намерений и контекста
- ✅ **Интеграция с Manus API** - долгосрочное хранение диалогов
- ✅ **База знаний** - готовые ответы по турам и услугам

## 🏗️ Архитектура решения

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AmoCRM Chat   │◄──►│  Browser Auto    │◄──►│   SQLite DB     │
│   (Клиенты)     │    │  (Selenium)      │    │ (Локальное      │
│                 │    │                  │    │  хранение)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  AI Response     │    │ Context Manager │
                       │  Engine          │    │ (Анализ         │
                       │  (Шаблоны)       │    │  намерений)     │
                       └──────────────────┘    └─────────────────┘
                                │                        │
                                └────────┬───────────────┘
                                         ▼
                                ┌─────────────────┐
                                │   Manus API     │
                                │ (Долгосрочное   │
                                │  хранение)      │
                                └─────────────────┘
```

## 🚀 Быстрое развертывание

### 1. Клонирование репозитория
```bash
git clone https://github.com/Anastasia462208/amocrm-ai-assistant.git
cd amocrm-ai-assistant
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Настройка конфигурации
```bash
cp config_template.py config.py
# Отредактируйте config.py с вашими данными
```

### 4. Проверка системы
```bash
python quick_check.py
```

### 5. Запуск системы
```bash
python amocrm_automation_system.py
```

## ⚙️ Детальная настройка

### Конфигурация AmoCRM

В файле `config.py`:

```python
AMOCRM_CONFIG = {
    'url': 'https://your-domain.amocrm.ru',     # Ваш домен AmoCRM
    'login': 'your-login',                      # Логин
    'password': 'your-password',                # Пароль
    'check_interval': 10,                       # Интервал проверки (сек)
    'max_parallel_conversations': 20,           # Макс. диалогов
}
```

### Конфигурация Manus API

```python
MANUS_CONFIG = {
    'api_key': 'sk-your-manus-api-key',        # API ключ Manus
    'mode': 'fast',                            # Режим: fast/quality
    'timeout': 60,                             # Таймаут запросов
}
```

### Настройка ответов

Система использует готовые шаблоны ответов для разных сценариев:

- **Приветствие** - автоматическое распознавание
- **Информация о турах** - Чусовая, Серга, цены
- **Бронирование** - процесс и требования
- **Снаряжение** - что взять, что предоставляется
- **Безопасность** - требования, ограничения
- **Даты и логистика** - расписание, трансфер

## 📊 Мониторинг и управление

### Проверка статуса системы

```python
from amocrm_automation_system import AmoCRMAutomationSystem

automation = AmoCRMAutomationSystem(url, login, password)
status = automation.get_system_status()

print(f"Активных диалогов: {status['active_conversations']}")
print(f"Сообщений за день: {status['total_messages_today']}")
```

### Анализ диалогов

```python
from context_manager import ConversationContextManager
from database_manager import DatabaseManager

db = DatabaseManager()
context_manager = ConversationContextManager(db)

# Получить метрики диалога
metrics = context_manager.get_conversation_metrics(conversation_id)
print(f"Готовность к бронированию: {metrics['conversion_probability']:.0%}")
```

### Логи системы

Система ведет подробные логи:
- `assistant.log` - основные события
- `error.log` - ошибки и исключения
- `database.log` - операции с базой данных

## 🔧 Устранение неполадок

### Частые проблемы и решения

#### 1. Не удается войти в AmoCRM
```bash
# Проверьте учетные данные
python -c "from config import AMOCRM_CONFIG; print(AMOCRM_CONFIG['url'])"

# Проверьте доступность AmoCRM
curl -I https://your-domain.amocrm.ru
```

#### 2. ChromeDriver не найден
```bash
# Установите webdriver-manager
pip install webdriver-manager

# Или скачайте вручную
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
```

#### 3. Manus API не отвечает
```bash
# Проверьте API ключ
python test_manus_api_final.py

# Проверьте лимиты API
curl -H "API_KEY: your-key" https://api.manus.im/v1/tasks
```

#### 4. Не находит элементы чата
- Обновите селекторы в коде под вашу версию AmoCRM
- Включите режим отладки (`headless=False`)
- Сделайте скриншоты для анализа

### Диагностические команды

```bash
# Быстрая проверка всех компонентов
python quick_check.py

# Полное тестирование
python test_system.py

# Проверка базы данных
python -c "from database_manager import DatabaseManager; db = DatabaseManager(); print('DB OK')"

# Тест Manus API
python test_manus_api_final.py
```

## 📈 Масштабирование

### Увеличение до 200 диалогов

1. **Увеличьте параметры в конфигурации:**
```python
AMOCRM_CONFIG = {
    'max_parallel_conversations': 200,
    'check_interval': 5,  # Более частые проверки
}
```

2. **Оптимизируйте браузерные сессии:**
```python
BROWSER_CONFIG = {
    'headless': True,  # Обязательно для продакшена
    'instances': 5,    # Несколько браузерных сессий
}
```

3. **Используйте внешнюю базу данных:**
```python
# Замените SQLite на PostgreSQL для высокой нагрузки
DATABASE_CONFIG = {
    'type': 'postgresql',
    'host': 'localhost',
    'database': 'amocrm_assistant'
}
```

### Распределенное развертывание

Для очень высокой нагрузки:

1. **Несколько серверов** - каждый обрабатывает часть клиентов
2. **Балансировщик нагрузки** - распределение запросов
3. **Общая база данных** - централизованное хранение
4. **Мониторинг** - отслеживание производительности

## 🔒 Безопасность

### Рекомендации по безопасности:

1. **Переменные окружения для паролей:**
```bash
export AMOCRM_LOGIN="your-login"
export AMOCRM_PASSWORD="your-password"
export MANUS_API_KEY="your-api-key"
```

2. **Ограничение доступа к серверу:**
```bash
# Настройте firewall
sudo ufw allow 22/tcp  # SSH
sudo ufw deny 80/tcp   # HTTP (если не нужен)
sudo ufw enable
```

3. **Регулярные обновления:**
```bash
pip install -U -r requirements.txt
```

4. **Резервное копирование:**
```bash
# Автоматический backup базы данных
crontab -e
# Добавьте: 0 2 * * * cp /path/to/conversations.db /backup/
```

## 📞 Поддержка и развитие

### Добавление новых типов ответов

1. **Обновите шаблоны в `amocrm_automation_system.py`:**
```python
self.response_templates['new_category'] = [
    "Новый шаблон ответа 1",
    "Новый шаблон ответа 2"
]
```

2. **Добавьте анализ намерений в `context_manager.py`:**
```python
self.intent_patterns['new_intent'] = [
    r'ключевое слово 1',
    r'ключевое слово 2'
]
```

### Интеграция с другими системами

Система готова к интеграции с:
- **CRM системами** (через API или браузерную автоматизацию)
- **Системами бронирования** (JotForm, Tilda, и др.)
- **Платежными системами** (для автоматической оплаты)
- **Системами уведомлений** (Telegram, WhatsApp)

### Мониторинг производительности

```python
# Добавьте метрики в код
import time
import psutil

def get_system_metrics():
    return {
        'cpu_usage': psutil.cpu_percent(),
        'memory_usage': psutil.virtual_memory().percent,
        'active_threads': threading.active_count(),
        'response_time': measure_response_time()
    }
```

## 🎯 Результаты внедрения

### Ожидаемые показатели:

- **Автоматизация:** 95%+ диалогов без участия менеджеров
- **Время отклика:** < 3 секунд на сообщение
- **Качество ответов:** 90%+ релевантных ответов
- **Конверсия:** увеличение на 20-30% за счет быстрых ответов

### Экономический эффект:

- **Экономия времени:** 6-8 часов менеджера в день
- **Увеличение продаж:** обработка большего количества клиентов
- **Улучшение сервиса:** круглосуточная поддержка
- **Масштабируемость:** готовность к росту бизнеса

---

## 📚 Дополнительные ресурсы

- **GitHub репозиторий:** https://github.com/Anastasia462208/amocrm-ai-assistant
- **Документация AmoCRM API:** https://www.amocrm.ru/developers/
- **Документация Manus API:** https://manus.im/docs/
- **Selenium документация:** https://selenium-python.readthedocs.io/

**Система готова к продуктивному использованию!** 🚀

---

*Разработано специально для турагентства "Все на сплав" с использованием современных технологий автоматизации и искусственного интеллекта.*

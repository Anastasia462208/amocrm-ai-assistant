# Инструкция по установке AmoCRM AI Assistant

## 📋 Требования

- Python 3.8 или выше
- Google Chrome браузер
- AmoCRM аккаунт с правами администратора
- Manus API ключ

## 🔧 Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/Anastasia462208/amocrm-ai-assistant.git
cd amocrm-ai-assistant
```

### 2. Создание виртуального окружения

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Установка Chrome WebDriver

#### Автоматическая установка (рекомендуется):
```bash
pip install webdriver-manager
```

#### Ручная установка:
1. Скачайте ChromeDriver с https://chromedriver.chromium.org/
2. Поместите в PATH или в папку проекта

### 5. Настройка конфигурации

```bash
# Скопируйте шаблон конфигурации
cp config_template.py config.py

# Отредактируйте config.py с вашими данными
nano config.py
```

### 6. Инициализация базы данных

```python
python -c "from database_manager import DatabaseManager; DatabaseManager('conversations.db')"
```

## ⚙️ Конфигурация

### AmoCRM настройки

В файле `config.py` укажите:

```python
AMOCRM_CONFIG = {
    'url': 'https://your-domain.amocrm.ru',
    'login': 'your-login',
    'password': 'your-password',
    'check_interval': 10,
}
```

### Manus API настройки

```python
MANUS_CONFIG = {
    'api_key': 'sk-your-manus-api-key',
    'mode': 'fast',
}
```

### Получение Manus API ключа

1. Зарегистрируйтесь на https://manus.im/
2. Перейдите в настройки API
3. Создайте новый API ключ
4. Скопируйте ключ в конфигурацию

## 🚀 Запуск

### Тестовый запуск

```bash
# Тест подключения к базе данных
python database_manager.py

# Тест Manus API
python test_manus_api_final.py

# Тест анализа контекста
python context_manager.py
```

### Основной запуск

```bash
python amocrm_automation_system.py
```

### Запуск в фоновом режиме (Linux)

```bash
nohup python amocrm_automation_system.py > assistant.log 2>&1 &
```

## 🔍 Проверка работы

### 1. Проверка логов

```bash
tail -f assistant.log
```

### 2. Проверка базы данных

```python
from database_manager import DatabaseManager
db = DatabaseManager()
print(f"Активных диалогов: {db.get_active_conversations_count()}")
```

### 3. Проверка статуса системы

```python
from amocrm_automation_system import AmoCRMAutomationSystem
automation = AmoCRMAutomationSystem(url, login, password)
status = automation.get_system_status()
print(status)
```

## 🛠️ Устранение неполадок

### Проблема: Не удается войти в AmoCRM

**Решение:**
1. Проверьте правильность URL, логина и пароля
2. Убедитесь, что аккаунт не заблокирован
3. Проверьте настройки безопасности AmoCRM

### Проблема: ChromeDriver не найден

**Решение:**
```bash
# Установите webdriver-manager
pip install webdriver-manager

# Или скачайте ChromeDriver вручную
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
```

### Проблема: Manus API не отвечает

**Решение:**
1. Проверьте правильность API ключа
2. Убедитесь в наличии интернет-соединения
3. Проверьте лимиты API

### Проблема: Не находит элементы чата

**Решение:**
1. Обновите селекторы в коде под вашу версию AmoCRM
2. Включите режим отладки (headless=False)
3. Сделайте скриншоты для анализа

## 📊 Мониторинг

### Логи системы

Система создает следующие логи:
- `assistant.log` - основные события
- `error.log` - ошибки
- `database.log` - операции с БД

### Метрики

Доступные метрики:
- Количество активных диалогов
- Сообщений обработано за день
- Время отклика системы
- Ошибки и их частота

### Уведомления

Настройте webhook для получения уведомлений:

```python
MONITORING_CONFIG = {
    'notification_webhook': 'https://your-webhook-url.com'
}
```

## 🔒 Безопасность

### Рекомендации:

1. **Не храните пароли в коде** - используйте переменные окружения
2. **Ограничьте доступ к серверу** - настройте firewall
3. **Регулярно обновляйте зависимости** - `pip install -U -r requirements.txt`
4. **Делайте резервные копии БД** - настройте автоматический backup

### Переменные окружения:

```bash
export AMOCRM_LOGIN="your-login"
export AMOCRM_PASSWORD="your-password"
export MANUS_API_KEY="your-api-key"
```

## 📈 Масштабирование

### Для увеличения нагрузки:

1. **Увеличьте количество браузерных сессий**
2. **Настройте балансировку нагрузки**
3. **Используйте внешнюю базу данных** (PostgreSQL)
4. **Добавьте кэширование** (Redis)

### Пример конфигурации для высокой нагрузки:

```python
AMOCRM_CONFIG = {
    'max_parallel_conversations': 50,
    'check_interval': 5,
    'browser_instances': 3,
}
```

## 🆘 Поддержка

При возникновении проблем:

1. Проверьте логи системы
2. Создайте issue в GitHub репозитории
3. Приложите конфигурацию (без паролей)
4. Опишите шаги для воспроизведения проблемы

## 📚 Дополнительные ресурсы

- [Документация AmoCRM API](https://www.amocrm.ru/developers/)
- [Документация Selenium](https://selenium-python.readthedocs.io/)
- [Документация Manus API](https://manus.im/docs/)
- [Примеры использования](./examples/)

---

**Удачной автоматизации!** 🚀

# AmoCRM-Manus Integration System

Автоматическая система интеграции AmoCRM с Manus API через webhooks для турагентства "Все на сплав".

## 🚀 Быстрый запуск в GitHub Codespace

### 1. Создание Codespace

1. Откройте этот репозиторий на GitHub
2. Нажмите зеленую кнопку **"Code"**
3. Выберите вкладку **"Codespaces"**
4. Нажмите **"Create codespace on master"**

### 2. Запуск системы

После создания Codespace выполните:

```bash
# Установка зависимостей (автоматически при создании)
pip install -r requirements.txt

# Запуск webhook сервера
python3 start_webhook_server.py
```

### 3. Получение URL для webhooks

После запуска система покажет URL-адреса:

```
🚀 WEBHOOK SYSTEM STARTED
======================================================================
📍 Base URL: https://your-codespace-5000.preview.app.github.dev
🔗 AmoCRM Webhook: https://your-codespace-5000.preview.app.github.dev/amocrm-webhook
🔗 Manus Webhook: https://your-codespace-5000.preview.app.github.dev/manus-webhook
📊 System Status: https://your-codespace-5000.preview.app.github.dev/status
💚 Health Check: https://your-codespace-5000.preview.app.github.dev/health
======================================================================
```

## ⚙️ Конфигурация

### AmoCRM Webhook

1. Войдите в AmoCRM
2. Перейдите в **Настройки → Интеграции → Webhooks**
3. Добавьте новый webhook:
   - **URL**: `https://your-codespace-5000.preview.app.github.dev/amocrm-webhook`
   - **События**: Добавление сообщения в чат
   - **Метод**: POST

### Manus Webhook

1. Войдите в Manus Dashboard
2. Перейдите в **Settings → Webhooks**
3. Добавьте webhook:
   - **URL**: `https://your-codespace-5000.preview.app.github.dev/manus-webhook`
   - **События**: Task completed, Task stopped

## 🔄 Как работает система

1. **Клиент пишет сообщение** в AmoCRM чат
2. **AmoCRM отправляет webhook** на наш сервер
3. **Система создает задачу** в Manus API с базой знаний
4. **Manus обрабатывает** запрос и генерирует ответ
5. **Manus отправляет webhook** о завершении задачи
6. **Система получает ответ** и отправляет его в AmoCRM
7. **Клиент видит ответ** в чате AmoCRM

## 📊 База знаний

Система использует встроенную базу знаний турагентства:

- **Туры на реке Чусовая** (3 дня/2 ночи)
- **Семейный сплав**: 18,000 руб/чел
- **Активный отдых**: 20,000 руб/чел
- **Включено**: питание, инструктор, снаряжение, трансфер
- **Даты**: 15-17 июня, 22-24 июня, 1-3 июля
- **Возраст**: от 8 лет

## 🛠️ Мониторинг

### Проверка статуса системы

```bash
curl https://your-codespace-5000.preview.app.github.dev/health
```

### Просмотр статистики

```bash
curl https://your-codespace-5000.preview.app.github.dev/status
```

### Логи системы

```bash
tail -f webhook_system.log
```

## 🔧 Файлы системы

- `complete_webhook_system.py` - Основной сервер с webhook handlers
- `start_webhook_server.py` - Скрипт запуска
- `requirements.txt` - Зависимости Python
- `.devcontainer/devcontainer.json` - Конфигурация Codespace
- `webhook_system.db` - База данных SQLite (создается автоматически)
- `webhook_system.log` - Логи системы

## 🚨 Устранение неполадок

### Сервер не запускается

```bash
# Проверить зависимости
pip install -r requirements.txt

# Проверить порт
netstat -tlnp | grep 5000
```

### Webhooks не работают

1. Проверьте URL в настройках AmoCRM и Manus
2. Убедитесь, что Codespace активен
3. Проверьте логи: `tail -f webhook_system.log`

### База данных

```bash
# Проверить базу данных
sqlite3 webhook_system.db ".tables"
sqlite3 webhook_system.db "SELECT * FROM tasks LIMIT 5;"
```

## 📞 Поддержка

Система готова к работе с 20 параллельными диалогами.
Для масштабирования до 200 диалогов потребуется оптимизация базы данных и добавление кэширования.

---

**Система разработана для автоматизации ответов в AmoCRM с использованием AI от Manus**

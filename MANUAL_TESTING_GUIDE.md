# 🧪 Руководство по ручному тестированию AmoCRM автоматизации

## ✅ Найденные селекторы

На основе исследования вашей AmoCRM найдены следующие селекторы:

### 📝 Поле ввода сообщения
```css
.control-contenteditable__area.feed-compose__message[contenteditable="true"]
```
**Альтернативные:**
```css
div[contenteditable="true"][data-hint*="Введите текст"]
div[contenteditable="true"]
```

### 📤 Кнопка отправки
```xpath
//button[.//span[contains(@class, "button-input-inner__text") and contains(text(), "Отправить")]]
```
**Альтернативные:**
```xpath
//span[@class="button-input-inner__text" and contains(text(), "Отправить")]/ancestor::button
```

### 💬 Сообщения в чате
```css
.feed-note__message_paragraph
```

## 🔧 Тестирование в консоли браузера

### Шаг 1: Откройте диалог с Anastasia в AmoCRM

### Шаг 2: Откройте консоль браузера (F12 → Console)

### Шаг 3: Проверьте селекторы

#### Проверка поля ввода:
```javascript
// Найти поле ввода
const inputField = document.querySelector('.control-contenteditable__area.feed-compose__message[contenteditable="true"]');
console.log('Input field found:', inputField);

// Проверить, что поле активно
console.log('Input visible:', inputField?.offsetParent !== null);
console.log('Input enabled:', inputField?.contentEditable === 'true');
```

#### Проверка кнопки отправки:
```javascript
// Найти кнопку отправки
const sendButton = document.evaluate(
    '//button[.//span[contains(@class, "button-input-inner__text") and contains(text(), "Отправить")]]',
    document,
    null,
    XPathResult.FIRST_ORDERED_NODE_TYPE,
    null
).singleNodeValue;

console.log('Send button found:', sendButton);
console.log('Send button visible:', sendButton?.offsetParent !== null);
```

#### Проверка сообщений:
```javascript
// Найти все сообщения
const messages = document.querySelectorAll('.feed-note__message_paragraph');
console.log('Messages found:', messages.length);
console.log('Last message:', messages[messages.length - 1]?.textContent);
```

## 🤖 Автоматическая отправка сообщения

### Тест отправки сообщения через консоль:

```javascript
// Функция для отправки сообщения
function sendTestMessage(messageText) {
    // Найти поле ввода
    const inputField = document.querySelector('.control-contenteditable__area.feed-compose__message[contenteditable="true"]');
    
    if (!inputField) {
        console.error('Input field not found!');
        return false;
    }
    
    // Очистить поле и ввести текст
    inputField.focus();
    inputField.innerHTML = '';
    inputField.textContent = messageText;
    
    // Найти кнопку отправки
    const sendButton = document.evaluate(
        '//button[.//span[contains(@class, "button-input-inner__text") and contains(text(), "Отправить")]]',
        document,
        null,
        XPathResult.FIRST_ORDERED_NODE_TYPE,
        null
    ).singleNodeValue;
    
    if (sendButton) {
        // Нажать кнопку отправки
        sendButton.click();
        console.log('Message sent via button!');
        return true;
    } else {
        // Использовать Enter как запасной вариант
        const event = new KeyboardEvent('keydown', {
            key: 'Enter',
            code: 'Enter',
            keyCode: 13,
            which: 13,
            bubbles: true
        });
        inputField.dispatchEvent(event);
        console.log('Message sent via Enter key!');
        return true;
    }
}

// Отправить тестовое сообщение
sendTestMessage('🤖 Это тестовое сообщение от AI ассистента!');
```

## 📋 Готовый ответ на вопрос о турах

Скопируйте и вставьте этот ответ в функцию выше:

```javascript
const tourResponse = `🚣‍♂️ Туры на 3 дня по реке Чусовая:

🌟 "Семейный сплав" (3 дня/2 ночи)
💰 Цена: 18,000 руб/чел
👨‍👩‍👧‍👦 Для семей с детьми от 8 лет
📍 Маршрут: Коуровка - Чусовая

🌟 "Активный отдых" (3 дня/2 ночи)  
💰 Цена: 20,000 руб/чел
🏃‍♂️ Для активных туристов
📍 Маршрут: Староуткинск - Чусовая

В стоимость включено:
✅ Рафт и снаряжение
✅ Трехразовое питание
✅ Опытный инструктор
✅ Трансфер от/до Екатеринбурга

📅 Ближайшие даты: 15-17 июня, 22-24 июня, 29 июня-1 июля

Какой тур вас больше интересует? 😊`;

// Отправить ответ о турах
sendTestMessage(tourResponse);
```

## 🔄 Автоматический мониторинг новых сообщений

```javascript
// Функция для мониторинга новых сообщений
function startMessageMonitoring() {
    let lastMessageCount = document.querySelectorAll('.feed-note__message_paragraph').length;
    
    setInterval(() => {
        const currentMessages = document.querySelectorAll('.feed-note__message_paragraph');
        const currentCount = currentMessages.length;
        
        if (currentCount > lastMessageCount) {
            const newMessage = currentMessages[currentCount - 1];
            const messageText = newMessage.textContent.trim();
            
            console.log('New message detected:', messageText);
            
            // Здесь можно добавить логику автоответа
            if (messageText.includes('тур') || messageText.includes('сплав')) {
                setTimeout(() => {
                    sendTestMessage(tourResponse);
                }, 2000); // Задержка 2 секунды
            }
            
            lastMessageCount = currentCount;
        }
    }, 3000); // Проверка каждые 3 секунды
    
    console.log('Message monitoring started!');
}

// Запустить мониторинг
startMessageMonitoring();
```

## ✅ Проверочный список

- [ ] Поле ввода найдено и активно
- [ ] Кнопка отправки найдена и работает
- [ ] Тестовое сообщение отправлено успешно
- [ ] Ответ о турах отправлен корректно
- [ ] Мониторинг новых сообщений работает

## 🚀 Следующие шаги

После успешного ручного тестирования:

1. **Адаптировать Python код** с проверенными селекторами
2. **Создать полноценную автоматизацию** с обработкой разных типов сообщений
3. **Добавить базу данных** для хранения истории диалогов
4. **Интегрировать с Manus API** для сложных запросов

---

**Результат тестирования покажет, работают ли найденные селекторы в реальной AmoCRM!**

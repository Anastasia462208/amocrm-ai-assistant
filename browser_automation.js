// 🤖 AmoCRM Browser Automation - JavaScript для консоли браузера
// Простая автоматизация без установки Python

console.log('🤖 AmoCRM Browser Automation запущена!');

// Конфигурация
const CONFIG = {
    // Интервал проверки новых сообщений (в миллисекундах)
    checkInterval: 5000, // 5 секунд
    
    // Задержка перед отправкой ответа
    responseDelay: 2000, // 2 секунды
    
    // Максимальное количество обработанных сообщений
    maxMessages: 50
};

// Готовые ответы
const RESPONSES = {
    tour3Days: `🚣‍♂️ Туры на 3 дня по реке Чусовая:

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

Какой тур вас больше интересует? 😊`,

    generalTours: `🚣‍♂️ У нас есть туры разной продолжительности:

• 2 дня - выходные туры
• 3 дня - популярные маршруты  
• 4+ дней - экспедиционные туры

На сколько дней вы планируете тур?`,

    prices: `💰 Стоимость зависит от продолжительности:

• 2 дня: от 8,000 руб/чел
• 3 дня: от 12,000 руб/чел  
• 4+ дней: от 16,000 руб/чел

В стоимость включено снаряжение, питание и инструктор.
На какой тур интересуетесь?`,

    dates: `📅 Сезон сплавов: май - сентябрь

Ближайшие свободные даты:
• Выходные: каждую субботу-воскресенье
• Будние дни: по согласованию

На какой период рассматриваете поездку?`,

    default: `Спасибо за сообщение! 😊

Расскажите, что вас интересует:
• Какой тур (продолжительность)?
• Примерные даты?
• Количество участников?

Подберу оптимальный вариант!`
};

// Селекторы для AmoCRM
const SELECTORS = {
    // Поле ввода сообщения
    chatInput: [
        '.control-contenteditable__area.feed-compose__message[contenteditable="true"]',
        'div[contenteditable="true"][data-hint*="Введите текст"]',
        'div[contenteditable="true"]',
        'textarea[placeholder*="сообщение"]',
        'textarea'
    ],
    
    // Кнопка отправки
    sendButton: [
        '//button[.//span[contains(@class, "button-input-inner__text") and contains(text(), "Отправить")]]',
        '//span[@class="button-input-inner__text" and contains(text(), "Отправить")]/ancestor::button'
    ],
    
    // Сообщения в чате
    messages: [
        '.feed-note__message_paragraph',
        '.feed-note',
        '[class*="message"]:not([class*="own"])',
        '[class*="incoming"]'
    ]
};

// Глобальные переменные
let isRunning = false;
let processedMessages = new Set();
let messageCount = 0;
let intervalId = null;

// Функция поиска элемента по селекторам
function findElement(selectors, useXPath = false) {
    for (const selector of selectors) {
        try {
            let element;
            if (useXPath) {
                const result = document.evaluate(
                    selector,
                    document,
                    null,
                    XPathResult.FIRST_ORDERED_NODE_TYPE,
                    null
                );
                element = result.singleNodeValue;
            } else {
                element = document.querySelector(selector);
            }
            
            if (element && element.offsetParent !== null) {
                return element;
            }
        } catch (e) {
            console.debug(`Селектор ${selector} не сработал:`, e);
        }
    }
    return null;
}

// Функция поиска поля ввода
function findChatInput() {
    return findElement(SELECTORS.chatInput);
}

// Функция поиска кнопки отправки
function findSendButton() {
    // Сначала пробуем XPath селекторы
    const xpathButton = findElement(SELECTORS.sendButton, true);
    if (xpathButton) return xpathButton;
    
    // Затем CSS селекторы
    const cssSelectors = [
        'button[type="submit"]',
        'button[title*="Отправить"]',
        '.send-button'
    ];
    return findElement(cssSelectors);
}

// Функция отправки сообщения
function sendMessage(messageText) {
    try {
        console.log('📤 Отправка сообщения:', messageText.substring(0, 50) + '...');
        
        // Находим поле ввода
        const inputField = findChatInput();
        if (!inputField) {
            console.error('❌ Поле ввода не найдено');
            return false;
        }
        
        // Фокусируемся на поле
        inputField.focus();
        
        // Очищаем поле
        if (inputField.contentEditable === 'true') {
            // Для contenteditable
            inputField.innerHTML = '';
            inputField.textContent = messageText;
        } else {
            // Для обычных полей
            inputField.value = '';
            inputField.value = messageText;
        }
        
        // Имитируем ввод
        const inputEvent = new Event('input', { bubbles: true });
        inputField.dispatchEvent(inputEvent);
        
        // Ждем немного
        setTimeout(() => {
            // Пробуем найти и нажать кнопку отправки
            const sendButton = findSendButton();
            if (sendButton) {
                sendButton.click();
                console.log('✅ Сообщение отправлено через кнопку');
            } else {
                // Используем Enter как fallback
                const enterEvent = new KeyboardEvent('keydown', {
                    key: 'Enter',
                    code: 'Enter',
                    keyCode: 13,
                    which: 13,
                    bubbles: true
                });
                inputField.dispatchEvent(enterEvent);
                console.log('✅ Сообщение отправлено через Enter');
            }
        }, 500);
        
        return true;
        
    } catch (error) {
        console.error('❌ Ошибка отправки сообщения:', error);
        return false;
    }
}

// Функция анализа сообщения и выбора ответа
function analyzeMessage(messageText) {
    const text = messageText.toLowerCase();
    
    // Проверяем на туры на 3 дня
    if (text.includes('3 дня') || text.includes('три дня') || text.includes('трехдневный')) {
        return RESPONSES.tour3Days;
    }
    
    // Проверяем на общие вопросы о турах
    if (text.includes('тур') || text.includes('сплав') || text.includes('поход')) {
        return RESPONSES.generalTours;
    }
    
    // Проверяем на вопросы о ценах
    if (text.includes('цена') || text.includes('стоимость') || text.includes('сколько')) {
        return RESPONSES.prices;
    }
    
    // Проверяем на вопросы о датах
    if (text.includes('когда') || text.includes('дата') || text.includes('время')) {
        return RESPONSES.dates;
    }
    
    // Возвращаем общий ответ
    return RESPONSES.default;
}

// Функция поиска новых сообщений
function findNewMessages() {
    const messages = [];
    
    for (const selector of SELECTORS.messages) {
        try {
            const elements = document.querySelectorAll(selector);
            
            for (const element of elements) {
                const text = element.textContent.trim();
                
                if (text && text.length > 3 && !processedMessages.has(text)) {
                    messages.push({
                        text: text,
                        element: element
                    });
                }
            }
            
            if (messages.length > 0) break; // Если нашли сообщения, не ищем дальше
            
        } catch (e) {
            console.debug(`Селектор сообщений ${selector} не сработал:`, e);
        }
    }
    
    return messages;
}

// Основная функция мониторинга
function monitorMessages() {
    if (!isRunning) return;
    
    try {
        const newMessages = findNewMessages();
        
        if (newMessages.length > 0) {
            console.log(`📨 Найдено новых сообщений: ${newMessages.length}`);
            
            newMessages.forEach((msg, index) => {
                setTimeout(() => {
                    console.log(`📥 Обрабатываю: ${msg.text.substring(0, 50)}...`);
                    
                    // Анализируем сообщение и генерируем ответ
                    const response = analyzeMessage(msg.text);
                    
                    // Отправляем ответ
                    if (sendMessage(response)) {
                        processedMessages.add(msg.text);
                        messageCount++;
                        console.log(`✅ Сообщение ${messageCount} обработано`);
                    }
                    
                    // Проверяем лимит
                    if (messageCount >= CONFIG.maxMessages) {
                        console.log('🛑 Достигнут лимит сообщений, останавливаю автоматизацию');
                        stopAutomation();
                    }
                    
                }, index * CONFIG.responseDelay);
            });
        }
        
    } catch (error) {
        console.error('❌ Ошибка мониторинга:', error);
    }
}

// Функция запуска автоматизации
function startAutomation() {
    if (isRunning) {
        console.log('⚠️ Автоматизация уже запущена');
        return;
    }
    
    console.log('🚀 Запуск автоматизации AmoCRM...');
    console.log('🔍 Мониторинг новых сообщений каждые', CONFIG.checkInterval / 1000, 'секунд');
    console.log('🛑 Для остановки выполните: stopAutomation()');
    
    isRunning = true;
    intervalId = setInterval(monitorMessages, CONFIG.checkInterval);
    
    // Показываем статус
    console.log('✅ Автоматизация запущена!');
    console.log('📊 Статистика: обработано сообщений -', messageCount);
}

// Функция остановки автоматизации
function stopAutomation() {
    if (!isRunning) {
        console.log('⚠️ Автоматизация не запущена');
        return;
    }
    
    console.log('🛑 Остановка автоматизации...');
    
    isRunning = false;
    if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
    }
    
    console.log('✅ Автоматизация остановлена');
    console.log('📊 Итоговая статистика:');
    console.log('  📨 Обработано сообщений:', messageCount);
    console.log('  💾 Сохранено в памяти:', processedMessages.size);
}

// Функция тестирования отправки сообщения
function testSendMessage() {
    const testMessage = '🤖 Тестовое сообщение от AI ассистента!';
    console.log('🧪 Тестирование отправки сообщения...');
    
    if (sendMessage(testMessage)) {
        console.log('✅ Тест прошел успешно!');
    } else {
        console.log('❌ Тест не прошел');
    }
}

// Функция показа статуса
function showStatus() {
    console.log('📊 СТАТУС АВТОМАТИЗАЦИИ:');
    console.log('  🔄 Запущена:', isRunning ? 'Да' : 'Нет');
    console.log('  📨 Обработано сообщений:', messageCount);
    console.log('  💾 В памяти сообщений:', processedMessages.size);
    console.log('  ⏱️ Интервал проверки:', CONFIG.checkInterval / 1000, 'сек');
    
    // Проверяем доступность элементов
    const inputField = findChatInput();
    const sendButton = findSendButton();
    
    console.log('  📝 Поле ввода:', inputField ? '✅ Найдено' : '❌ Не найдено');
    console.log('  📤 Кнопка отправки:', sendButton ? '✅ Найдена' : '❌ Не найдена');
}

// Экспортируем функции в глобальную область
window.startAutomation = startAutomation;
window.stopAutomation = stopAutomation;
window.testSendMessage = testSendMessage;
window.showStatus = showStatus;

// Приветственное сообщение
console.log(`
🤖 AmoCRM Browser Automation готова к работе!

📋 ДОСТУПНЫЕ КОМАНДЫ:
  startAutomation()  - Запустить автоматизацию
  stopAutomation()   - Остановить автоматизацию  
  testSendMessage()  - Тест отправки сообщения
  showStatus()       - Показать статус

🚀 Для начала работы выполните: startAutomation()
`);

// Автоматическая проверка готовности
setTimeout(() => {
    console.log('🔍 Проверка готовности системы...');
    showStatus();
}, 1000);

// 🤖 AmoCRM Browser Automation - ИСПРАВЛЕННАЯ ВЕРСИЯ
// Безопасная автоматизация без зацикливания

console.log('🛡️ AmoCRM Browser Automation - БЕЗОПАСНАЯ ВЕРСИЯ');

// Конфигурация
const CONFIG = {
    checkInterval: 10000, // Увеличено до 10 секунд
    responseDelay: 3000,  // Увеличено до 3 секунд
    maxMessages: 10,      // Уменьшено до 10 сообщений
    cooldownPeriod: 30000 // 30 секунд между ответами
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
    chatInput: [
        '.control-contenteditable__area.feed-compose__message[contenteditable="true"]',
        'div[contenteditable="true"][data-hint*="Введите текст"]',
        'div[contenteditable="true"]',
        'textarea[placeholder*="сообщение"]',
        'textarea'
    ],
    
    sendButton: [
        '//button[.//span[contains(@class, "button-input-inner__text") and contains(text(), "Отправить")]]',
        '//span[@class="button-input-inner__text" and contains(text(), "Отправить")]/ancestor::button'
    ],
    
    // УЛУЧШЕННЫЕ селекторы для сообщений
    incomingMessages: [
        '.feed-note__message_paragraph:not(.feed-note__message_paragraph--own)',
        '.feed-note:not(.feed-note--own) .feed-note__message_paragraph',
        '.message:not(.message--own)',
        '[class*="message"]:not([class*="own"]):not([class*="outgoing"])'
    ],
    
    // Селекторы для исходящих сообщений (чтобы их игнорировать)
    outgoingMessages: [
        '.feed-note__message_paragraph--own',
        '.feed-note--own .feed-note__message_paragraph',
        '.message--own',
        '[class*="message"][class*="own"]',
        '[class*="message"][class*="outgoing"]'
    ]
};

// Глобальные переменные
let isRunning = false;
let processedMessages = new Set();
let messageCount = 0;
let intervalId = null;
let lastResponseTime = 0;
let botMessages = new Set(); // Сообщения, отправленные ботом

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
    const xpathButton = findElement(SELECTORS.sendButton, true);
    if (xpathButton) return xpathButton;
    
    const cssSelectors = [
        'button[type="submit"]',
        'button[title*="Отправить"]',
        '.send-button'
    ];
    return findElement(cssSelectors);
}

// УЛУЧШЕННАЯ функция отправки сообщения
function sendMessage(messageText) {
    try {
        // Проверяем cooldown
        const now = Date.now();
        if (now - lastResponseTime < CONFIG.cooldownPeriod) {
            console.log('⏳ Cooldown активен, пропускаем отправку');
            return false;
        }
        
        console.log('📤 Отправка сообщения:', messageText.substring(0, 50) + '...');
        
        const inputField = findChatInput();
        if (!inputField) {
            console.error('❌ Поле ввода не найдено');
            return false;
        }
        
        // Сохраняем сообщение как отправленное ботом
        botMessages.add(messageText.trim());
        
        inputField.focus();
        
        if (inputField.contentEditable === 'true') {
            inputField.innerHTML = '';
            inputField.textContent = messageText;
        } else {
            inputField.value = '';
            inputField.value = messageText;
        }
        
        const inputEvent = new Event('input', { bubbles: true });
        inputField.dispatchEvent(inputEvent);
        
        setTimeout(() => {
            const sendButton = findSendButton();
            if (sendButton) {
                sendButton.click();
                console.log('✅ Сообщение отправлено через кнопку');
            } else {
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
            
            lastResponseTime = Date.now();
        }, 500);
        
        return true;
        
    } catch (error) {
        console.error('❌ Ошибка отправки сообщения:', error);
        return false;
    }
}

// Функция анализа сообщения
function analyzeMessage(messageText) {
    const text = messageText.toLowerCase();
    
    if (text.includes('3 дня') || text.includes('три дня') || text.includes('трехдневный')) {
        return RESPONSES.tour3Days;
    }
    
    if (text.includes('тур') || text.includes('сплав') || text.includes('поход')) {
        return RESPONSES.generalTours;
    }
    
    if (text.includes('цена') || text.includes('стоимость') || text.includes('сколько')) {
        return RESPONSES.prices;
    }
    
    if (text.includes('когда') || text.includes('дата') || text.includes('время')) {
        return RESPONSES.dates;
    }
    
    return RESPONSES.default;
}

// УЛУЧШЕННАЯ функция поиска новых сообщений
function findNewMessages() {
    const messages = [];
    
    try {
        // Ищем только входящие сообщения
        for (const selector of SELECTORS.incomingMessages) {
            try {
                const elements = document.querySelectorAll(selector);
                
                for (const element of elements) {
                    const text = element.textContent.trim();
                    
                    if (text && text.length > 3) {
                        // Проверяем, что это не наше сообщение
                        const isOurMessage = botMessages.has(text) || 
                                           text.includes('🚣‍♂️') || 
                                           text.includes('💰') || 
                                           text.includes('📅') ||
                                           text.includes('😊');
                        
                        // Проверяем, что не обрабатывали это сообщение
                        const alreadyProcessed = processedMessages.has(text);
                        
                        if (!isOurMessage && !alreadyProcessed) {
                            messages.push({
                                text: text,
                                element: element
                            });
                        }
                    }
                }
                
                if (messages.length > 0) break;
                
            } catch (e) {
                console.debug(`Селектор ${selector} не сработал:`, e);
            }
        }
        
    } catch (error) {
        console.error('❌ Ошибка поиска сообщений:', error);
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
            
            // Обрабатываем только первое сообщение
            const msg = newMessages[0];
            
            console.log(`📥 Обрабатываю: ${msg.text.substring(0, 50)}...`);
            
            const response = analyzeMessage(msg.text);
            
            if (sendMessage(response)) {
                processedMessages.add(msg.text);
                messageCount++;
                console.log(`✅ Сообщение ${messageCount} обработано`);
                
                if (messageCount >= CONFIG.maxMessages) {
                    console.log('🛑 Достигнут лимит сообщений, останавливаю автоматизацию');
                    stopAutomation();
                }
            }
        }
        
    } catch (error) {
        console.error('❌ Ошибка мониторинга:', error);
    }
}

// Функция запуска автоматизации
function startAutomationSafe() {
    if (isRunning) {
        console.log('⚠️ Автоматизация уже запущена');
        return;
    }
    
    console.log('🛡️ Запуск БЕЗОПАСНОЙ автоматизации AmoCRM...');
    console.log('🔍 Мониторинг каждые', CONFIG.checkInterval / 1000, 'секунд');
    console.log('⏳ Cooldown между ответами:', CONFIG.cooldownPeriod / 1000, 'секунд');
    console.log('🔢 Максимум сообщений:', CONFIG.maxMessages);
    console.log('🛑 Для остановки: stopAutomationSafe()');
    
    isRunning = true;
    intervalId = setInterval(monitorMessages, CONFIG.checkInterval);
    
    console.log('✅ Безопасная автоматизация запущена!');
}

// Функция остановки автоматизации
function stopAutomationSafe() {
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
    console.log('📊 Статистика:');
    console.log('  📨 Обработано сообщений:', messageCount);
    console.log('  💾 В памяти сообщений:', processedMessages.size);
    console.log('  🤖 Отправлено ботом:', botMessages.size);
}

// Функция тестирования (БЕЗОПАСНАЯ)
function testSendMessageSafe() {
    const testMessage = '🧪 Тест безопасной автоматизации';
    console.log('🧪 Безопасное тестирование...');
    
    if (sendMessage(testMessage)) {
        console.log('✅ Безопасный тест прошел успешно!');
    } else {
        console.log('❌ Тест не прошел');
    }
}

// Функция показа статуса
function showStatusSafe() {
    console.log('📊 СТАТУС БЕЗОПАСНОЙ АВТОМАТИЗАЦИИ:');
    console.log('  🔄 Запущена:', isRunning ? 'Да' : 'Нет');
    console.log('  📨 Обработано сообщений:', messageCount);
    console.log('  💾 В памяти сообщений:', processedMessages.size);
    console.log('  🤖 Отправлено ботом:', botMessages.size);
    console.log('  ⏱️ Интервал проверки:', CONFIG.checkInterval / 1000, 'сек');
    console.log('  ⏳ Cooldown:', CONFIG.cooldownPeriod / 1000, 'сек');
    console.log('  🔢 Лимит сообщений:', CONFIG.maxMessages);
    
    const inputField = findChatInput();
    const sendButton = findSendButton();
    
    console.log('  📝 Поле ввода:', inputField ? '✅ Найдено' : '❌ Не найдено');
    console.log('  📤 Кнопка отправки:', sendButton ? '✅ Найдена' : '❌ Не найдена');
    
    const lastResponse = lastResponseTime ? new Date(lastResponseTime).toLocaleTimeString() : 'Никогда';
    console.log('  🕐 Последний ответ:', lastResponse);
}

// Экспортируем функции
window.startAutomationSafe = startAutomationSafe;
window.stopAutomationSafe = stopAutomationSafe;
window.testSendMessageSafe = testSendMessageSafe;
window.showStatusSafe = showStatusSafe;

// Приветственное сообщение
console.log(`
🛡️ AmoCRM БЕЗОПАСНАЯ Автоматизация готова!

📋 КОМАНДЫ:
  startAutomationSafe()  - Запустить безопасную автоматизацию
  stopAutomationSafe()   - Остановить автоматизацию  
  testSendMessageSafe()  - Безопасный тест отправки
  showStatusSafe()       - Показать статус

🔒 БЕЗОПАСНОСТЬ:
  ✅ Игнорирует собственные сообщения
  ✅ Cooldown 30 секунд между ответами
  ✅ Лимит 10 сообщений
  ✅ Увеличенные интервалы проверки

🚀 Для начала: startAutomationSafe()
`);

setTimeout(() => {
    console.log('🔍 Проверка готовности безопасной системы...');
    showStatusSafe();
}, 1000);

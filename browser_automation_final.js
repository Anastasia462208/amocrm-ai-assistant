// 🛡️ AmoCRM ФИНАЛЬНАЯ БЕЗОПАСНАЯ Автоматизация
// Отслеживает ТОЛЬКО новые сообщения, появившиеся после запуска

console.log('🛡️ AmoCRM ФИНАЛЬНАЯ БЕЗОПАСНАЯ Автоматизация');

// Конфигурация
const CONFIG = {
    checkInterval: 15000,  // 15 секунд - еще больше
    responseDelay: 5000,   // 5 секунд задержка
    maxMessages: 5,        // Только 5 сообщений для безопасности
    cooldownPeriod: 60000  // 1 минута между ответами
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

    default: `Спасибо за сообщение! 😊

Расскажите, что вас интересует:
• Какой тур (продолжительность)?
• Примерные даты?
• Количество участников?

Подберу оптимальный вариант!`
};

// Глобальные переменные
let isRunning = false;
let intervalId = null;
let messageCount = 0;
let lastResponseTime = 0;

// НОВЫЙ ПОДХОД: Снимок состояния при запуске
let initialMessageCount = 0;
let initialMessages = [];
let startTime = 0;

// Функция поиска поля ввода
function findChatInput() {
    const selectors = [
        '.control-contenteditable__area.feed-compose__message[contenteditable="true"]',
        'div[contenteditable="true"][data-hint*="Введите текст"]',
        'div[contenteditable="true"]',
        'textarea[placeholder*="сообщение"]'
    ];
    
    for (const selector of selectors) {
        try {
            const element = document.querySelector(selector);
            if (element && element.offsetParent !== null) {
                return element;
            }
        } catch (e) {
            console.debug(`Селектор ${selector} не сработал`);
        }
    }
    return null;
}

// Функция отправки сообщения (ТОЛЬКО через Enter)
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
        
        inputField.focus();
        
        // Очищаем и вводим текст
        if (inputField.contentEditable === 'true') {
            inputField.innerHTML = '';
            inputField.textContent = messageText;
        } else {
            inputField.value = '';
            inputField.value = messageText;
        }
        
        // Имитируем ввод
        const inputEvent = new Event('input', { bubbles: true });
        inputField.dispatchEvent(inputEvent);
        
        // Отправляем через Enter
        setTimeout(() => {
            const enterEvent = new KeyboardEvent('keydown', {
                key: 'Enter',
                code: 'Enter',
                keyCode: 13,
                which: 13,
                bubbles: true
            });
            inputField.dispatchEvent(enterEvent);
            
            console.log('✅ Сообщение отправлено через Enter');
            lastResponseTime = Date.now();
        }, 1000);
        
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
    
    return RESPONSES.default;
}

// НОВАЯ функция: Создание снимка текущего состояния
function createInitialSnapshot() {
    try {
        const messageSelectors = [
            '.feed-note__message_paragraph',
            '.feed-note',
            '[class*="message"]'
        ];
        
        let allMessages = [];
        
        for (const selector of messageSelectors) {
            try {
                const elements = document.querySelectorAll(selector);
                for (const element of elements) {
                    const text = element.textContent.trim();
                    if (text && text.length > 3) {
                        allMessages.push({
                            text: text,
                            timestamp: Date.now(),
                            element: element
                        });
                    }
                }
                if (allMessages.length > 0) break;
            } catch (e) {
                console.debug(`Селектор ${selector} не сработал`);
            }
        }
        
        initialMessages = allMessages;
        initialMessageCount = allMessages.length;
        startTime = Date.now();
        
        console.log(`📸 Создан снимок: ${initialMessageCount} сообщений в истории`);
        console.log('🕐 Время запуска:', new Date(startTime).toLocaleTimeString());
        
        return true;
        
    } catch (error) {
        console.error('❌ Ошибка создания снимка:', error);
        return false;
    }
}

// НОВАЯ функция: Поиск ТОЛЬКО новых сообщений
function findTrulyNewMessages() {
    try {
        const messageSelectors = [
            '.feed-note__message_paragraph',
            '.feed-note',
            '[class*="message"]'
        ];
        
        let currentMessages = [];
        
        for (const selector of messageSelectors) {
            try {
                const elements = document.querySelectorAll(selector);
                for (const element of elements) {
                    const text = element.textContent.trim();
                    if (text && text.length > 3) {
                        currentMessages.push({
                            text: text,
                            element: element
                        });
                    }
                }
                if (currentMessages.length > 0) break;
            } catch (e) {
                console.debug(`Селектор ${selector} не сработал`);
            }
        }
        
        // Сравниваем с начальным снимком
        const newMessages = [];
        
        if (currentMessages.length > initialMessageCount) {
            // Берем только сообщения, которых не было в начальном снимке
            const newCount = currentMessages.length - initialMessageCount;
            const potentialNewMessages = currentMessages.slice(-newCount);
            
            for (const msg of potentialNewMessages) {
                // Проверяем, что это не наше сообщение
                const isOurMessage = msg.text.includes('🚣‍♂️') || 
                                   msg.text.includes('💰') || 
                                   msg.text.includes('📅') ||
                                   msg.text.includes('😊') ||
                                   msg.text.includes('Спасибо за сообщение');
                
                // Проверяем, что не было в начальном снимке
                const wasInInitial = initialMessages.some(initial => 
                    initial.text === msg.text
                );
                
                if (!isOurMessage && !wasInInitial) {
                    newMessages.push(msg);
                }
            }
        }
        
        return newMessages;
        
    } catch (error) {
        console.error('❌ Ошибка поиска новых сообщений:', error);
        return [];
    }
}

// Основная функция мониторинга
function monitorNewMessages() {
    if (!isRunning) return;
    
    try {
        const newMessages = findTrulyNewMessages();
        
        if (newMessages.length > 0) {
            console.log(`📨 Найдено ДЕЙСТВИТЕЛЬНО новых сообщений: ${newMessages.length}`);
            
            // Обрабатываем только первое новое сообщение
            const msg = newMessages[0];
            
            console.log(`📥 Обрабатываю новое сообщение: ${msg.text.substring(0, 50)}...`);
            
            const response = analyzeMessage(msg.text);
            
            if (sendMessage(response)) {
                messageCount++;
                console.log(`✅ Новое сообщение ${messageCount} обработано`);
                
                // Обновляем снимок
                initialMessageCount++;
                initialMessages.push({
                    text: msg.text,
                    timestamp: Date.now()
                });
                
                if (messageCount >= CONFIG.maxMessages) {
                    console.log('🛑 Достигнут лимит сообщений, останавливаю автоматизацию');
                    stopAutomationFinal();
                }
            }
        } else {
            console.log('🔍 Новых сообщений не найдено');
        }
        
    } catch (error) {
        console.error('❌ Ошибка мониторинга:', error);
    }
}

// Функция запуска автоматизации
function startAutomationFinal() {
    if (isRunning) {
        console.log('⚠️ Автоматизация уже запущена');
        return;
    }
    
    console.log('🛡️ Запуск ФИНАЛЬНОЙ БЕЗОПАСНОЙ автоматизации...');
    
    // Создаем снимок текущего состояния
    if (!createInitialSnapshot()) {
        console.error('❌ Не удалось создать снимок, автоматизация не запущена');
        return;
    }
    
    console.log('🔍 Мониторинг каждые', CONFIG.checkInterval / 1000, 'секунд');
    console.log('⏳ Cooldown между ответами:', CONFIG.cooldownPeriod / 1000, 'секунд');
    console.log('🔢 Максимум сообщений:', CONFIG.maxMessages);
    console.log('🛑 Для остановки: stopAutomationFinal()');
    
    isRunning = true;
    intervalId = setInterval(monitorNewMessages, CONFIG.checkInterval);
    
    console.log('✅ ФИНАЛЬНАЯ автоматизация запущена!');
    console.log('📸 Отслеживаются только сообщения, появившиеся ПОСЛЕ этого момента');
}

// Функция остановки автоматизации
function stopAutomationFinal() {
    if (!isRunning) {
        console.log('⚠️ Автоматизация не запущена');
        return;
    }
    
    console.log('🛑 Остановка финальной автоматизации...');
    
    isRunning = false;
    if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
    }
    
    console.log('✅ Автоматизация остановлена');
    console.log('📊 Финальная статистика:');
    console.log('  📨 Обработано НОВЫХ сообщений:', messageCount);
    console.log('  📸 Начальный снимок:', initialMessageCount, 'сообщений');
    console.log('  🕐 Время работы:', Math.round((Date.now() - startTime) / 1000), 'секунд');
}

// Функция показа статуса
function showStatusFinal() {
    console.log('📊 СТАТУС ФИНАЛЬНОЙ АВТОМАТИЗАЦИИ:');
    console.log('  🔄 Запущена:', isRunning ? 'Да' : 'Нет');
    console.log('  📨 Обработано НОВЫХ сообщений:', messageCount);
    console.log('  📸 Начальный снимок:', initialMessageCount, 'сообщений');
    console.log('  ⏱️ Интервал проверки:', CONFIG.checkInterval / 1000, 'сек');
    console.log('  ⏳ Cooldown:', CONFIG.cooldownPeriod / 1000, 'сек');
    console.log('  🔢 Лимит сообщений:', CONFIG.maxMessages);
    
    const inputField = findChatInput();
    console.log('  📝 Поле ввода:', inputField ? '✅ Найдено' : '❌ Не найдено');
    
    if (startTime > 0) {
        console.log('  🕐 Время запуска:', new Date(startTime).toLocaleTimeString());
        console.log('  ⏱️ Время работы:', Math.round((Date.now() - startTime) / 1000), 'сек');
    }
    
    const lastResponse = lastResponseTime ? new Date(lastResponseTime).toLocaleTimeString() : 'Никогда';
    console.log('  🕐 Последний ответ:', lastResponse);
}

// Функция тестирования
function testSendMessageFinal() {
    const testMessage = '🧪 Финальный тест автоматизации';
    console.log('🧪 Финальное тестирование...');
    
    if (sendMessage(testMessage)) {
        console.log('✅ Финальный тест прошел успешно!');
    } else {
        console.log('❌ Тест не прошел');
    }
}

// Экспортируем функции
window.startAutomationFinal = startAutomationFinal;
window.stopAutomationFinal = stopAutomationFinal;
window.showStatusFinal = showStatusFinal;
window.testSendMessageFinal = testSendMessageFinal;

// Приветственное сообщение
console.log(`
🛡️ AmoCRM ФИНАЛЬНАЯ БЕЗОПАСНАЯ Автоматизация готова!

📋 КОМАНДЫ:
  startAutomationFinal()  - Запустить финальную автоматизацию
  stopAutomationFinal()   - Остановить автоматизацию  
  testSendMessageFinal()  - Финальный тест отправки
  showStatusFinal()       - Показать статус

🔒 МАКСИМАЛЬНАЯ БЕЗОПАСНОСТЬ:
  ✅ Снимок состояния при запуске
  ✅ Отслеживание ТОЛЬКО новых сообщений
  ✅ Игнорирование всей истории чата
  ✅ Cooldown 1 минута между ответами
  ✅ Лимит 5 сообщений максимум
  ✅ Проверка каждые 15 секунд

🚀 Для начала: startAutomationFinal()
`);

setTimeout(() => {
    console.log('🔍 Проверка готовности финальной системы...');
    showStatusFinal();
}, 1000);

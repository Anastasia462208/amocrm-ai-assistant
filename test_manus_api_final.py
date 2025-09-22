#!/usr/bin/env python3
"""
Финальный тест Manus API с правильными режимами: fast, quality
"""

import requests
import json

# API ключ Manus
MANUS_API_KEY = "sk-w3WopZM2I_Wxoltnbv0BHXP_ygv3cb53HW3Wa0Myp18ZP_ol1EfrF9gorM4Nl8rycZLLJupyvG_Y80aMtr7gpsgeogoc"

def test_manus_api_final():
    """Тестируем API с правильными режимами: fast, quality"""
    
    url = "https://api.manus.im/v1/tasks"
    headers = {
        "API_KEY": MANUS_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Правильные режимы согласно ошибке API
    modes = ["fast", "quality"]
    
    prompt = """
    Ты ассистент турагентства по речным сплавам "Все на сплав".
    
    База знаний:
    - Чусовая: семейные сплавы 2-5 дней, цены от 15000 руб
    - Серга: однодневные сплавы, цены от 3500 руб
    
    Вопрос клиента: Здравствуйте! Интересует семейный сплав на 3 дня в июне. Сколько это будет стоить для 2 взрослых и 1 ребенка?
    
    Ответь профессионально и дружелюбно, предложи конкретные варианты.
    """
    
    print(f"🚀 Тестируем Manus API: {url}")
    print(f"🔑 API Key: {MANUS_API_KEY[:20]}...")
    print()
    
    for mode in modes:
        payload = {
            "prompt": prompt.strip(),
            "mode": mode,
            "attachments": []
        }
        
        print(f"🧪 Тестируем режим: {mode}")
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            print(f"   ✅ Статус: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"   🎉 УСПЕХ! Режим '{mode}' работает!")
                    print(f"   📝 Ответ: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    return mode, result
                except:
                    print(f"   📝 Ответ (текст): {response.text}")
                    return mode, response.text
            elif response.status_code == 401:
                print(f"   🔐 Ошибка авторизации: {response.text}")
            else:
                print(f"   ❌ Ошибка {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Исключение: {str(e)}")
        
        print()
    
    return None, None

def create_manus_client():
    """Создаем класс для работы с Manus API"""
    
    class ManusClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.base_url = "https://api.manus.im/v1/tasks"
            self.headers = {
                "API_KEY": api_key,
                "Content-Type": "application/json"
            }
        
        def send_request(self, prompt, mode="fast", attachments=None):
            """Отправляем запрос к Manus API"""
            if attachments is None:
                attachments = []
            
            payload = {
                "prompt": prompt,
                "mode": mode,
                "attachments": attachments
            }
            
            try:
                response = requests.post(
                    self.base_url, 
                    headers=self.headers, 
                    json=payload, 
                    timeout=60
                )
                
                if response.status_code == 200:
                    return True, response.json()
                else:
                    return False, f"Error {response.status_code}: {response.text}"
                    
            except Exception as e:
                return False, f"Exception: {str(e)}"
    
    return ManusClient(MANUS_API_KEY)

if __name__ == "__main__":
    # Тестируем API
    mode, result = test_manus_api_final()
    
    if result:
        print("\n" + "="*60)
        print("🎉 MANUS API РАБОТАЕТ!")
        print("="*60)
        print(f"Рабочий режим: {mode}")
        print(f"Результат: {json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, dict) else result}")
        
        # Создаем клиент для дальнейшего использования
        client = create_manus_client()
        print("\n🚀 Клиент Manus API создан и готов к использованию!")
        print("   Доступные режимы: fast, quality")
        print("   Можно создавать систему для 200 параллельных диалогов!")
        
    else:
        print("\n😞 API не работает. Проверьте ключ или обратитесь в поддержку Manus.")

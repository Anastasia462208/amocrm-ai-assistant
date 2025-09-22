#!/usr/bin/env python3
"""
Final AmoCRM Automation with Real Selectors
Based on actual AmoCRM contenteditable interface
"""

import time
import logging
import json
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class AmoCRMFinalAutomation:
    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password
        
        # Real AmoCRM selectors based on provided HTML
        self.selectors = {
            'chat_input': {
                'contenteditable': '.control-contenteditable__area.feed-compose__message[contenteditable="true"]',
                'alternative_input': 'div[contenteditable="true"][data-hint*="Введите текст"]',
                'container': '.feed-compose__message'
            },
            'send_button': {
                # Real AmoCRM send button selectors
                'primary': '.button-input-inner__text',
                'button_container': 'button:has(.button-input-inner__text)',
                'text_selector': 'span.button-input-inner__text',
                'submit': 'button[type="submit"]',
                'send_icon': '.icon-send, .send-button',
                'form_submit': '.feed-compose form button'
            },
            'messages': {
                'container': '.feed-note__message_paragraph',
                'text': '.feed-note__message_paragraph',
                'author': '.feed-note__author',
                'timestamp': '.feed-note__time'
            }
        }
        
        # Response for the 3-day tour inquiry
        self.tour_response = """🚣‍♂️ Туры на 3 дня по реке Чусовая:

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

Какой тур вас больше интересует? 😊"""
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.driver = None
    
    def initialize_browser(self):
        """Initialize Chrome browser"""
        chrome_options = Options()
        
        # Create unique user data directory
        import tempfile
        user_data_dir = tempfile.mkdtemp(prefix="amocrm_automation_")
        
        # Browser options for stability
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # For debugging - set to True to see browser
        headless = False
        if headless:
            chrome_options.add_argument('--headless=new')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            self.logger.info("Browser initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            return False
    
    def login_to_amocrm(self) -> bool:
        """Login to AmoCRM"""
        try:
            self.logger.info("Logging in to AmoCRM...")
            
            # Navigate to AmoCRM
            self.driver.get("https://amoshturm.amocrm.ru")
            time.sleep(3)
            
            # Find and fill login form
            login_selectors = [
                "input[name='USER_LOGIN']",
                "input[type='email']",
                "input[placeholder*='mail']"
            ]
            
            login_field = None
            for selector in login_selectors:
                try:
                    login_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not login_field:
                self.logger.error("Could not find login field")
                return False
            
            # Find password field
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            
            # Fill credentials
            login_field.clear()
            login_field.send_keys(self.login)
            
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Submit form
            password_field.send_keys(Keys.ENTER)
            
            # Wait for login
            time.sleep(5)
            
            # Check if logged in
            current_url = self.driver.current_url
            if 'amoshturm.amocrm.ru' in current_url and 'auth' not in current_url:
                self.logger.info("Successfully logged in to AmoCRM")
                return True
            else:
                self.logger.error(f"Login failed. Current URL: {current_url}")
                return False
                
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False
    
    def find_chat_input(self):
        """Find the chat input field using contenteditable selector"""
        try:
            self.logger.info("Looking for chat input field...")
            
            # Try different selectors for the contenteditable input
            input_selectors = [
                self.selectors['chat_input']['contenteditable'],
                self.selectors['chat_input']['alternative_input'],
                'div[contenteditable="true"]',
                '.feed-compose__message',
                '[data-hint*="Введите текст"]'
            ]
            
            for selector in input_selectors:
                try:
                    input_element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    
                    if input_element.is_displayed() and input_element.is_enabled():
                        self.logger.info(f"Found chat input with selector: {selector}")
                        return input_element
                        
                except Exception as e:
                    self.logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            self.logger.error("Could not find chat input field")
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding chat input: {e}")
            return None
    
    def find_send_button(self):
        """Find the send button"""
        try:
            self.logger.info("Looking for send button...")
            
            send_selectors = [
                # Find button by the text span inside it
                '//button[.//span[contains(@class, "button-input-inner__text") and contains(text(), "Отправить")]]',
                '//span[@class="button-input-inner__text" and contains(text(), "Отправить")]/ancestor::button',
                # CSS selectors as fallback
                'button:has(.button-input-inner__text)',
                self.selectors['send_button']['submit'],
                'button[title*="Отправить"]',
                'button[aria-label*="Отправить"]',
                '.send-button'
            ]
            
            for selector in send_selectors:
                try:
                    # Use XPath for selectors starting with //
                    if selector.startswith('//'):
                        send_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        send_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if send_button.is_displayed() and send_button.is_enabled():
                        self.logger.info(f"Found send button with selector: {selector}")
                        return send_button
                        
                except Exception as e:
                    self.logger.debug(f"Send button selector {selector} failed: {e}")
                    continue
            
            self.logger.warning("Could not find send button - will use Enter key")
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding send button: {e}")
            return None
    
    def send_message(self, message: str) -> bool:
        """Send a message using contenteditable field"""
        try:
            self.logger.info(f"Attempting to send message: {message[:50]}...")
            
            # Find input field
            input_element = self.find_chat_input()
            if not input_element:
                return False
            
            # Clear existing content
            input_element.click()
            time.sleep(0.5)
            
            # Select all and delete
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            time.sleep(0.2)
            input_element.send_keys(Keys.DELETE)
            time.sleep(0.2)
            
            # Type the message
            input_element.send_keys(message)
            time.sleep(1)
            
            # Try to find and click send button
            send_button = self.find_send_button()
            if send_button:
                send_button.click()
                self.logger.info("Message sent using send button")
            else:
                # Use Enter key as fallback
                input_element.send_keys(Keys.ENTER)
                self.logger.info("Message sent using Enter key")
            
            time.sleep(2)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    def navigate_to_anastasia_chat(self):
        """Navigate to Anastasia's chat"""
        try:
            self.logger.info("Looking for Anastasia's chat...")
            
            # Wait for page to load
            time.sleep(3)
            
            # Look for Anastasia in contact list
            contact_selectors = [
                "//div[contains(text(), 'Anastasia')]",
                "//span[contains(text(), 'Anastasia')]",
                "//*[contains(text(), 'Anastasia')]"
            ]
            
            for selector in contact_selectors:
                try:
                    contact_element = self.driver.find_element(By.XPATH, selector)
                    contact_element.click()
                    self.logger.info("Found and clicked Anastasia's chat")
                    time.sleep(3)
                    return True
                except:
                    continue
            
            self.logger.warning("Could not find Anastasia's chat - continuing with current chat")
            return True
            
        except Exception as e:
            self.logger.error(f"Error navigating to Anastasia's chat: {e}")
            return False
    
    def run_automation_test(self):
        """Run the complete automation test"""
        try:
            self.logger.info("Starting AmoCRM automation test...")
            
            # Initialize browser
            if not self.initialize_browser():
                return False
            
            # Login to AmoCRM
            if not self.login_to_amocrm():
                return False
            
            # Navigate to Anastasia's chat
            if not self.navigate_to_anastasia_chat():
                return False
            
            # Wait for chat interface to load
            time.sleep(3)
            
            # Send the tour response
            success = self.send_message(self.tour_response)
            
            if success:
                self.logger.info("✅ Automation test completed successfully!")
                print("✅ Message sent successfully!")
                
                # Keep browser open for verification
                input("Press Enter to close browser...")
            else:
                self.logger.error("❌ Failed to send message")
                print("❌ Failed to send message")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Automation test failed: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def get_debug_info(self):
        """Get debug information about page elements"""
        try:
            if not self.driver:
                return "Browser not initialized"
            
            debug_info = {
                'current_url': self.driver.current_url,
                'page_title': self.driver.title,
                'contenteditable_elements': [],
                'buttons': [],
                'forms': []
            }
            
            # Find all contenteditable elements
            contenteditable_elements = self.driver.find_elements(By.CSS_SELECTOR, '[contenteditable="true"]')
            for elem in contenteditable_elements:
                debug_info['contenteditable_elements'].append({
                    'tag': elem.tag_name,
                    'class': elem.get_attribute('class'),
                    'data-hint': elem.get_attribute('data-hint'),
                    'visible': elem.is_displayed()
                })
            
            # Find all buttons
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            for btn in buttons[:10]:  # Limit to first 10
                debug_info['buttons'].append({
                    'class': btn.get_attribute('class'),
                    'type': btn.get_attribute('type'),
                    'title': btn.get_attribute('title'),
                    'visible': btn.is_displayed()
                })
            
            return debug_info
            
        except Exception as e:
            return f"Error getting debug info: {e}"

def main():
    """Main function to run the automation"""
    print("🤖 AmoCRM Final Automation Test")
    print("=" * 50)
    print("Login: amoshturm@gmail.com")
    print("Target: Anastasia chat")
    print()
    
    automation = AmoCRMFinalAutomation("amoshturm@gmail.com", "GbbT4Z5L")
    
    try:
        success = automation.run_automation_test()
        
        if success:
            print("\n🎉 Test completed successfully!")
        else:
            print("\n❌ Test failed - check logs for details")
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()

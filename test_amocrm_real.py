#!/usr/bin/env python3
"""
Test AmoCRM Automation with Real Environment
Safe testing with Anastasia contact
"""

import time
import logging
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from test_config import AMOCRM_CONFIG, BROWSER_CONFIG, LOGGING_CONFIG, TEST_RESPONSE_TEMPLATES, SAFETY_CONFIG

class TestAmoCRMAutomation:
    def __init__(self):
        self.login = AMOCRM_CONFIG['login']
        self.password = AMOCRM_CONFIG['password']
        self.target_contact = AMOCRM_CONFIG['target_contact']
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, LOGGING_CONFIG['level']),
            format=LOGGING_CONFIG['format'],
            handlers=[
                logging.FileHandler(LOGGING_CONFIG['file']),
                logging.StreamHandler() if LOGGING_CONFIG['console_output'] else logging.NullHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.driver = None
        self.is_logged_in = False
        self.screenshots_dir = "test_screenshots"
        
        # Create screenshots directory
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        self.logger.info("Test AmoCRM Automation initialized")
    
    def initialize_browser(self):
        """Initialize Chrome browser for testing"""
        chrome_options = Options()
        
        # Create unique user data directory
        import tempfile
        user_data_dir = tempfile.mkdtemp(prefix="chrome_test_")
        
        if not BROWSER_CONFIG['headless']:
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument(f"--window-size={BROWSER_CONFIG['window_size'][0]},{BROWSER_CONFIG['window_size'][1]}")
        else:
            chrome_options.add_argument('--headless')
        
        # Additional options for stability and avoiding conflicts
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--remote-debugging-port=0')
        chrome_options.add_argument('--no-zygote')
        chrome_options.add_argument('--single-process')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        
        # Force headless if there are display issues
        if BROWSER_CONFIG['headless']:
            chrome_options.add_argument('--headless=new')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(BROWSER_CONFIG['implicit_wait'])
            self.driver.set_page_load_timeout(BROWSER_CONFIG['page_load_timeout'])
            
            self.logger.info("Browser initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            return False
    
    def take_screenshot(self, name: str):
        """Take screenshot for debugging"""
        if BROWSER_CONFIG['save_screenshots'] and self.driver:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{self.screenshots_dir}/{timestamp}_{name}.png"
                self.driver.save_screenshot(filename)
                self.logger.info(f"Screenshot saved: {filename}")
                return filename
            except Exception as e:
                self.logger.error(f"Failed to take screenshot: {e}")
        return None
    
    def login_to_amocrm(self) -> bool:
        """Login to AmoCRM"""
        try:
            self.logger.info("Attempting to login to AmoCRM...")
            
            # Try different possible AmoCRM URLs
            possible_urls = [
                "https://amoshturm.amocrm.ru",
                "https://amoshturm.amocrm.com", 
                "https://www.amocrm.ru/auth/login",
                "https://www.amocrm.com/auth/login"
            ]
            
            login_success = False
            
            for url in possible_urls:
                try:
                    self.logger.info(f"Trying URL: {url}")
                    self.driver.get(url)
                    time.sleep(3)
                    
                    self.take_screenshot("login_page")
                    
                    # Look for login form elements
                    login_selectors = [
                        "input[name='USER_LOGIN']",
                        "input[type='email']",
                        "input[placeholder*='mail']",
                        "input[placeholder*='логин']",
                        "#login",
                        ".login-input"
                    ]
                    
                    login_field = None
                    for selector in login_selectors:
                        try:
                            login_field = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            self.logger.info(f"Found login field with selector: {selector}")
                            break
                        except:
                            continue
                    
                    if login_field:
                        # Found login form
                        password_selectors = [
                            "input[name='USER_HASH']",
                            "input[type='password']",
                            "input[placeholder*='пароль']",
                            "#password",
                            ".password-input"
                        ]
                        
                        password_field = None
                        for selector in password_selectors:
                            try:
                                password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                                self.logger.info(f"Found password field with selector: {selector}")
                                break
                            except:
                                continue
                        
                        if password_field:
                            # Fill login form
                            login_field.clear()
                            login_field.send_keys(self.login)
                            
                            password_field.clear()
                            password_field.send_keys(self.password)
                            
                            self.take_screenshot("form_filled")
                            
                            # Submit form
                            submit_selectors = [
                                "button[type='submit']",
                                "input[type='submit']",
                                ".login-button",
                                ".submit-button"
                            ]
                            
                            for selector in submit_selectors:
                                try:
                                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                                    submit_button.click()
                                    self.logger.info(f"Clicked submit button: {selector}")
                                    break
                                except:
                                    continue
                            else:
                                # Try Enter key if no submit button found
                                password_field.send_keys(Keys.ENTER)
                                self.logger.info("Submitted form with Enter key")
                            
                            # Wait for login result
                            time.sleep(5)
                            self.take_screenshot("after_login")
                            
                            # Check if login was successful
                            current_url = self.driver.current_url
                            page_source = self.driver.page_source.lower()
                            
                            if any(indicator in current_url.lower() for indicator in ['dashboard', 'leads', 'contacts', 'main']):
                                login_success = True
                                self.logger.info(f"Login successful! Current URL: {current_url}")
                                break
                            elif any(indicator in page_source for indicator in ['dashboard', 'leads', 'contacts', 'сделки', 'контакты']):
                                login_success = True
                                self.logger.info("Login successful! Found dashboard elements")
                                break
                            else:
                                self.logger.warning(f"Login may have failed. URL: {current_url}")
                                continue
                    
                except Exception as e:
                    self.logger.warning(f"Failed to login with URL {url}: {e}")
                    continue
            
            if login_success:
                self.is_logged_in = True
                self.logger.info("Successfully logged in to AmoCRM")
                return True
            else:
                self.logger.error("Failed to login to AmoCRM with all attempted URLs")
                return False
                
        except Exception as e:
            self.logger.error(f"Login failed with exception: {e}")
            return False
    
    def find_anastasia_chat(self):
        """Find and open chat with Anastasia"""
        try:
            self.logger.info("Looking for Anastasia chat...")
            
            # Take screenshot of current page
            self.take_screenshot("looking_for_chat")
            
            # Common selectors for finding contacts/chats
            contact_selectors = [
                f"*[text()*='Anastasia']",
                f"*[contains(text(), 'Anastasia')]",
                ".contact-name",
                ".lead-name", 
                ".chat-contact",
                ".conversation-item"
            ]
            
            # Try to find Anastasia in various ways
            for selector in contact_selectors:
                try:
                    if selector.startswith("*["):
                        # XPath selector
                        elements = self.driver.find_elements(By.XPATH, f"//{selector}")
                    else:
                        # CSS selector
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if 'anastasia' in element.text.lower():
                            self.logger.info(f"Found Anastasia contact: {element.text}")
                            element.click()
                            time.sleep(2)
                            self.take_screenshot("anastasia_chat_opened")
                            return True
                            
                except Exception as e:
                    self.logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # If not found, try navigation to chats/messages section
            self.logger.info("Trying to navigate to chats section...")
            
            nav_selectors = [
                "a[href*='chat']",
                "a[href*='message']", 
                "*[text()*='Чат']",
                "*[text()*='Сообщения']",
                ".nav-chat",
                ".messages-nav"
            ]
            
            for selector in nav_selectors:
                try:
                    if selector.startswith("*["):
                        nav_element = self.driver.find_element(By.XPATH, f"//{selector}")
                    else:
                        nav_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    nav_element.click()
                    time.sleep(3)
                    self.take_screenshot("navigated_to_chats")
                    
                    # Try to find Anastasia again
                    return self.find_anastasia_chat()
                    
                except Exception as e:
                    self.logger.debug(f"Navigation selector {selector} failed: {e}")
                    continue
            
            self.logger.warning("Could not find Anastasia chat")
            return False
            
        except Exception as e:
            self.logger.error(f"Error finding Anastasia chat: {e}")
            return False
    
    def analyze_chat_structure(self):
        """Analyze the structure of the chat interface"""
        try:
            self.logger.info("Analyzing chat structure...")
            
            self.take_screenshot("chat_structure_analysis")
            
            # Look for common chat elements
            chat_elements = {
                'input_field': [
                    "textarea",
                    "input[type='text']",
                    "*[placeholder*='сообщение']",
                    "*[placeholder*='message']",
                    ".chat-input",
                    ".message-input"
                ],
                'send_button': [
                    "button[type='submit']",
                    "*[text()*='Отправить']",
                    "*[text()*='Send']",
                    ".send-button",
                    ".chat-send"
                ],
                'messages': [
                    ".message",
                    ".chat-message",
                    ".conversation-message",
                    ".msg"
                ]
            }
            
            found_elements = {}
            
            for element_type, selectors in chat_elements.items():
                self.logger.info(f"Looking for {element_type}...")
                
                for selector in selectors:
                    try:
                        if selector.startswith("*["):
                            elements = self.driver.find_elements(By.XPATH, f"//{selector}")
                        else:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        if elements:
                            found_elements[element_type] = {
                                'selector': selector,
                                'count': len(elements),
                                'elements': elements
                            }
                            self.logger.info(f"Found {len(elements)} {element_type} elements with selector: {selector}")
                            break
                            
                    except Exception as e:
                        self.logger.debug(f"Selector {selector} failed: {e}")
                        continue
            
            # Log findings
            self.logger.info("Chat structure analysis results:")
            for element_type, info in found_elements.items():
                self.logger.info(f"  {element_type}: {info['count']} elements found with '{info['selector']}'")
            
            return found_elements
            
        except Exception as e:
            self.logger.error(f"Error analyzing chat structure: {e}")
            return {}
    
    def send_test_message(self, message: str = None):
        """Send a test message to the chat"""
        try:
            if message is None:
                message = TEST_RESPONSE_TEMPLATES['test_response'][0]
            
            self.logger.info(f"Attempting to send test message: {message}")
            
            # Analyze chat structure first
            chat_elements = self.analyze_chat_structure()
            
            if 'input_field' not in chat_elements:
                self.logger.error("No input field found!")
                return False
            
            input_elements = chat_elements['input_field']['elements']
            
            # Try each input element
            for i, input_element in enumerate(input_elements):
                try:
                    if not input_element.is_displayed() or not input_element.is_enabled():
                        continue
                    
                    self.logger.info(f"Trying input element {i+1}")
                    
                    # Safety check
                    if SAFETY_CONFIG['require_confirmation']:
                        response = input("Send test message? (y/n): ")
                        if response.lower() != 'y':
                            self.logger.info("Message sending cancelled by user")
                            return False
                    
                    if SAFETY_CONFIG['dry_run']:
                        self.logger.info(f"DRY RUN: Would send message: {message}")
                        return True
                    
                    # Clear and type message
                    input_element.clear()
                    input_element.send_keys(message)
                    
                    self.take_screenshot("message_typed")
                    
                    # Try to send
                    if 'send_button' in chat_elements:
                        # Use send button
                        send_button = chat_elements['send_button']['elements'][0]
                        send_button.click()
                        self.logger.info("Message sent using send button")
                    else:
                        # Use Enter key
                        input_element.send_keys(Keys.ENTER)
                        self.logger.info("Message sent using Enter key")
                    
                    time.sleep(2)
                    self.take_screenshot("message_sent")
                    
                    return True
                    
                except Exception as e:
                    self.logger.warning(f"Failed to send with input element {i+1}: {e}")
                    continue
            
            self.logger.error("Failed to send message with any input element")
            return False
            
        except Exception as e:
            self.logger.error(f"Error sending test message: {e}")
            return False
    
    def run_test_session(self):
        """Run a complete test session"""
        try:
            self.logger.info("Starting test session...")
            
            # Initialize browser
            if not self.initialize_browser():
                return False
            
            # Login to AmoCRM
            if not self.login_to_amocrm():
                return False
            
            # Find Anastasia chat
            if not self.find_anastasia_chat():
                self.logger.warning("Could not find Anastasia chat, but continuing...")
            
            # Analyze chat structure
            self.analyze_chat_structure()
            
            # Send test message
            if SAFETY_CONFIG['test_mode']:
                self.logger.info("Test mode enabled - analyzing only")
                return True
            else:
                return self.send_test_message()
            
        except Exception as e:
            self.logger.error(f"Test session failed: {e}")
            return False
        
        finally:
            if self.driver:
                self.logger.info("Keeping browser open for manual inspection...")
                input("Press Enter to close browser...")
                self.driver.quit()
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()

def main():
    """Main test function"""
    print("🧪 AmoCRM Real Environment Test")
    print("=" * 50)
    print(f"Target contact: {AMOCRM_CONFIG['target_contact']}")
    print(f"Login: {AMOCRM_CONFIG['login']}")
    print(f"Test mode: {SAFETY_CONFIG['test_mode']}")
    print(f"Dry run: {SAFETY_CONFIG['dry_run']}")
    print()
    
    tester = TestAmoCRMAutomation()
    
    try:
        success = tester.run_test_session()
        
        if success:
            print("✅ Test completed successfully!")
        else:
            print("❌ Test failed - check logs for details")
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()

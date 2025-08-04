import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
try:
    import undetected_chromedriver as uc
    UNDETECTED_AVAILABLE = True
except ImportError:
    print("Warning: undetected-chromedriver not available, falling back to regular Chrome")
    UNDETECTED_AVAILABLE = False

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    print("Warning: cloudscraper not available, falling back to requests")
    CLOUDSCRAPER_AVAILABLE = False

import json
import os


class AntiDetectionScraper:
    """Enhanced scraper with anti-detection and captcha handling capabilities"""
    
    def __init__(self):
        self.session = requests.Session()
        if CLOUDSCRAPER_AVAILABLE:
            self.scraper = cloudscraper.create_scraper()
        else:
            self.scraper = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        ]
        
    def get_random_user_agent(self):
        """Get a random user agent"""
        return random.choice(self.user_agents)
    
    def setup_stealth_chrome_options(self):
        """Setup Chrome options for stealth browsing"""
        options = Options()
        
        # Basic stealth options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_argument("--disable-javascript")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Window and viewport settings
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        
        # User agent
        options.add_argument(f"--user-agent={self.get_random_user_agent()}")
        
        # Experimental options to avoid detection
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 2
        })
        
        return options
    
    def setup_undetected_chrome(self):
        """Setup undetected Chrome driver"""
        if not UNDETECTED_AVAILABLE:
            print("Undetected Chrome not available")
            return None
            
        try:
            options = uc.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument(f"--user-agent={self.get_random_user_agent()}")
            
            driver = uc.Chrome(options=options)
            return driver
        except Exception as e:
            print(f"Failed to setup undetected Chrome: {e}")
            return None
    
    def handle_captcha(self, driver):
        """Handle captcha challenges"""
        try:
            # Check for common captcha elements
            captcha_selectors = [
                "iframe[src*='captcha']",
                "iframe[src*='recaptcha']",
                "iframe[src*='hcaptcha']",
                ".captcha",
                ".recaptcha",
                "#captcha",
                "#recaptcha"
            ]
            
            for selector in captcha_selectors:
                captcha_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if captcha_elements:
                    print(f"Captcha detected with selector: {selector}")
                    return self.solve_captcha(driver, captcha_elements[0])
            
            # Check for text-based captcha
            captcha_text = driver.find_elements(By.XPATH, "//*[contains(text(), 'captcha') or contains(text(), 'verify')]")
            if captcha_text:
                print("Text-based captcha detected")
                return self.handle_text_captcha(driver)
                
            return False
            
        except Exception as e:
            print(f"Error handling captcha: {e}")
            return False
    
    def solve_captcha(self, driver, captcha_element):
        """Attempt to solve captcha"""
        try:
            # Try to switch to captcha iframe
            driver.switch_to.frame(captcha_element)
            
            # Look for common captcha solving elements
            checkbox = driver.find_elements(By.CSS_SELECTOR, ".recaptcha-checkbox, .h-captcha")
            if checkbox:
                print("Found captcha checkbox, attempting to click...")
                checkbox[0].click()
                time.sleep(3)
            
            # Switch back to main content
            driver.switch_to.default_content()
            
            # Wait for captcha to be solved
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"Error solving captcha: {e}")
            driver.switch_to.default_content()
            return False
    
    def handle_text_captcha(self, driver):
        """Handle text-based captcha challenges"""
        try:
            # Look for input fields that might be captcha
            captcha_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[name*='captcha']")
            
            if captcha_inputs:
                print("Text captcha detected, manual intervention required")
                # For now, we'll just wait and let user handle manually
                input("Please solve the captcha manually and press Enter to continue...")
                return True
                
            return False
            
        except Exception as e:
            print(f"Error handling text captcha: {e}")
            return False
    
    def add_human_behavior(self, driver):
        """Add human-like behavior to avoid detection"""
        try:
            # Random mouse movements
            actions = ActionChains(driver)
            for _ in range(random.randint(2, 5)):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                actions.move_by_offset(x, y)
                actions.perform()
                time.sleep(random.uniform(0.1, 0.3))
            
            # Random scrolling
            driver.execute_script(f"window.scrollTo(0, {random.randint(100, 500)});")
            time.sleep(random.uniform(0.5, 1.5))
            
            # Random page interactions
            if random.random() < 0.3:
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(random.uniform(0.5, 1.0))
                
        except Exception as e:
            print(f"Error adding human behavior: {e}")
    
    def check_for_blocking(self, driver):
        """Check if the page is blocking access"""
        try:
            page_source = driver.page_source.lower()
            blocking_indicators = [
                "blocked", "captcha", "verify", "robot", "automation",
                "access denied", "forbidden", "rate limit", "too many requests"
            ]
            
            for indicator in blocking_indicators:
                if indicator in page_source:
                    print(f"Blocking detected: {indicator}")
                    return True
                    
            return False
            
        except Exception as e:
            print(f"Error checking for blocking: {e}")
            return False
    
    def scrape_with_retry(self, keyword: str, max_results: int = 10, max_retries: int = 3):
        """Scrape with retry logic and multiple methods"""
        
        for attempt in range(max_retries):
            print(f"Attempt {attempt + 1}/{max_retries}")
            
            # Try undetected Chrome first
            driver = self.setup_undetected_chrome()
            if driver:
                try:
                    results = self.scrape_with_driver(driver, keyword, max_results)
                    if results and len(results) > 1:  # More than just error message
                        return results
                except Exception as e:
                    print(f"Undetected Chrome failed: {e}")
                finally:
                    driver.quit()
            
            # Try regular Chrome with stealth options
            driver = None
            try:
                options = self.setup_stealth_chrome_options()
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                
                # Remove webdriver property
                driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )
                
                results = self.scrape_with_driver(driver, keyword, max_results)
                if results and len(results) > 1:
                    return results
                    
            except Exception as e:
                print(f"Regular Chrome failed: {e}")
            finally:
                if driver:
                    driver.quit()
            
            # Try cloudscraper as fallback
            try:
                results = self.scrape_with_cloudscraper(keyword, max_results)
                if results and len(results) > 1:
                    return results
            except Exception as e:
                print(f"Cloudscraper failed: {e}")
            
            # Wait before retry
            if attempt < max_retries - 1:
                wait_time = random.uniform(5, 15)
                print(f"Waiting {wait_time:.1f} seconds before retry...")
                time.sleep(wait_time)
        
        # If all methods fail, return error result
        return [{
            "Item Description": f"All scraping methods failed for '{keyword}' - website may be blocking automated access",
            "Current price": "N/A",
            "Auction end date": "N/A",
            "Auction image / thumbnail URL (extra credit)": "",
        }]
    
    def scrape_with_driver(self, driver, keyword: str, max_results: int = 10):
        """Scrape using Selenium driver"""
        base_url = "https://shopgoodwill.com"
        search_url = f"{base_url}/search?keywords={keyword.replace(' ', '+')}&sort=Closing"
        results = []
        
        try:
            print(f"Navigating to: {search_url}")
            driver.get(search_url)
            
            # Add human behavior
            self.add_human_behavior(driver)
            
            # Wait for page load
            wait = WebDriverWait(driver, 20)
            time.sleep(random.uniform(3, 5))
            
            # Check for blocking
            if self.check_for_blocking(driver):
                # Try to handle captcha
                if self.handle_captcha(driver):
                    time.sleep(5)
                    if self.check_for_blocking(driver):
                        raise Exception("Still blocked after captcha handling")
                else:
                    raise Exception("Blocked and captcha handling failed")
            
            # Wait for content
            try:
                main_content = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "main, .container, .content, [class*='main']")
                    )
                )
                print("Found main content area")
            except:
                print("Main content area not found, proceeding anyway")
            
            time.sleep(random.uniform(2, 4))
            
            # Get page source and parse
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            
            # Extract results (using existing logic)
            results = self.extract_results_from_soup(soup, keyword, max_results)
            
            return results
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            return [{
                "Item Description": f"Error scraping results for '{keyword}': {str(e)}",
                "Current price": "N/A",
                "Auction end date": "N/A",
                "Auction image / thumbnail URL (extra credit)": "",
            }]
    
    def scrape_with_cloudscraper(self, keyword: str, max_results: int = 10):
        """Scrape using cloudscraper as fallback"""
        base_url = "https://shopgoodwill.com"
        search_url = f"{base_url}/search?keywords={keyword.replace(' ', '+')}&sort=Closing"
        
        try:
            headers = {
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = self.scraper.get(search_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            return self.extract_results_from_soup(soup, keyword, max_results)
            
        except Exception as e:
            print(f"Cloudscraper error: {e}")
            return [{
                "Item Description": f"Cloudscraper failed for '{keyword}': {str(e)}",
                "Current price": "N/A",
                "Auction end date": "N/A",
                "Auction image / thumbnail URL (extra credit)": "",
            }]
    
    def extract_results_from_soup(self, soup, keyword: str, max_results: int = 10):
        """Extract results from BeautifulSoup object"""
        results = []
        
        # Try to find product elements with various selectors
        product_elements = []
        
        selectors_to_try = [
            ".p-datatable-tbody tr",
            "div[class*='product']",
            "div[class*='item']:not([class*='nav']):not([class*='header']):not([class*='footer'])",
            "div[class*='card']:not([class*='nav']):not([class*='header']):not([class*='footer'])",
            "div[class*='auction']",
            "[class*='ng-star-inserted']:not([class*='nav']):not([class*='header']):not([class*='footer'])",
            "div[class*='col']:not([class*='nav']):not([class*='header']):not([class*='footer'])",
            "div[class*='row'] > div:not([class*='nav']):not([class*='header']):not([class*='footer'])",
            "a[href*='/item/']",
            "div:has(a[href*='/item/'])",
        ]
        
        for selector in selectors_to_try:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} elements with selector: {selector}")
                filtered_elements = []
                for elem in elements:
                    elem_text = elem.get_text().lower()
                    elem_classes = " ".join(elem.get("class", [])).lower()
                    if any(
                        skip_word in elem_text or skip_word in elem_classes
                        for skip_word in [
                            "sign in", "login", "register", "cart", "search", "menu", "nav", "header", "footer",
                        ]
                    ):
                        continue
                    filtered_elements.append(elem)
                
                if filtered_elements:
                    product_elements = filtered_elements
                    print(f"After filtering, found {len(product_elements)} potential product elements")
                    break
        
        # Process found elements
        for i, item in enumerate(product_elements[:max_results]):
            try:
                item_data = {}
                
                # Extract description
                description_elem = (
                    item.find("a", href=lambda x: x and "/item/" in x)
                    or item.find("a")
                    or item.find("h3")
                    or item.find("h4")
                    or item.find("div", class_=lambda x: x and any(word in str(x).lower() for word in ["title", "name", "desc"]))
                )
                item_data["Item Description"] = (
                    description_elem.get_text(strip=True) if description_elem else f"Item {i+1}"
                )
                
                # Extract price
                price_elem = (
                    item.find("span", class_=lambda x: x and "price" in str(x).lower())
                    or item.find("div", class_=lambda x: x and "price" in str(x).lower())
                    or item.find("span", string=lambda x: x and "$" in x)
                    or item.find("div", string=lambda x: x and "$" in x)
                )
                item_data["Current price"] = (
                    price_elem.get_text(strip=True) if price_elem else "Price not available"
                )
                
                # Extract date
                date_elem = (
                    item.find("div", class_=lambda x: x and any(word in str(x).lower() for word in ["date", "time", "end", "timer"]))
                    or item.find("span", class_=lambda x: x and any(word in str(x).lower() for word in ["date", "time", "end", "timer"]))
                    or item.find("div", string=lambda x: x and any(word in x.lower() for word in ["end", "closing", "time", "date"]))
                    or item.find("span", string=lambda x: x and any(word in x.lower() for word in ["end", "closing", "time", "date"]))
                )
                item_data["Auction end date"] = (
                    date_elem.get_text(strip=True) if date_elem else "Date not available"
                )
                
                # Extract image
                img_elem = item.find("img")
                item_data["Auction image / thumbnail URL (extra credit)"] = (
                    img_elem.get("src", "") if img_elem else ""
                )
                
                if item_data["Item Description"] and item_data["Item Description"] != f"Item {i+1}":
                    results.append(item_data)
                    
            except Exception as e:
                print(f"Error processing item {i+1}: {e}")
                continue
        
        if not results:
            results.append({
                "Item Description": f"No results found for '{keyword}' - website may be blocking automated access",
                "Current price": "N/A",
                "Auction end date": "N/A",
                "Auction image / thumbnail URL (extra credit)": "",
            })
        
        return results


# Global scraper instance
_scraper_instance = None


def get_scraper():
    """Get the global scraper instance"""
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = AntiDetectionScraper()
    return _scraper_instance


def scrape_auction_results(keyword: str, max_results: int = 10) -> list:
    """
    Enhanced scrape auction results with anti-detection and captcha handling.
    Returns a list of dictionaries with the required fields.
    """
    scraper = get_scraper()
    return scraper.scrape_with_retry(keyword, max_results)

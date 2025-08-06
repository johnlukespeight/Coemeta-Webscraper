"""Enhanced web scraper with anti-detection capabilities for shopgoodwill.com.

This module provides a robust web scraping solution with multiple fallback methods,
anti-bot detection avoidance, and comprehensive error handling. It implements
various techniques to avoid detection by anti-bot systems, including:

- Multiple scraping methods with fallback mechanisms
- Human behavior simulation
- Browser fingerprint manipulation
- Captcha detection and handling
- Enhanced headers and cookies
- Random user agent rotation
- Request throttling and delays

The module uses a combination of Selenium WebDriver, undetected-chromedriver,
cloudscraper, and BeautifulSoup to provide reliable scraping capabilities.

Example:
    >>> from scraper import scrape_auction_results
    >>> results = scrape_auction_results("vintage watch", max_results=5)
    >>> for result in results:
    ...     print(result["Item Description"], result["Current price"])
"""

import time
import random
import requests
from typing import List, Dict, Optional, Any
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

    # Test if it actually works
    uc.ChromeOptions()
    UNDETECTED_AVAILABLE = False  # Temporarily disable due to reuse issues
except Exception as e:
    print(
        f"Warning: undetected-chromedriver not available ({e}), falling back to regular Chrome"
    )
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
    """Enhanced scraper with anti-detection and captcha handling capabilities.

    This class provides multiple scraping methods with fallback mechanisms,
    human behavior simulation, and comprehensive error handling to avoid
    detection by anti-bot systems. It implements a variety of techniques
    to bypass anti-bot measures and captcha challenges.

    The class uses a multi-layered approach to web scraping:
    1. First attempt: undetected-chromedriver (if available)
    2. Second attempt: Selenium with stealth options
    3. Fallback: cloudscraper or requests

    Each method includes enhanced anti-detection measures such as:
    - Browser fingerprint manipulation
    - Human behavior simulation (natural scrolling, reading pauses)
    - Enhanced headers and cookies
    - Random user agent rotation
    - Captcha detection and handling

    Attributes:
        session (requests.Session): Standard requests session
        scraper (Union[requests.Session, cloudscraper.CloudScraper]): 
            Enhanced session with cloudscraper if available
        user_agents (List[str]): List of realistic user agent strings
    """

    def __init__(self) -> None:
        """Initialize the AntiDetectionScraper with session and user agents."""
        self.session = requests.Session()
        if CLOUDSCRAPER_AVAILABLE:
            self.scraper = cloudscraper.create_scraper()
        else:
            self.scraper = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        ]

    def get_random_user_agent(self) -> str:
        """Get a random user agent from the predefined list.
        
        Randomly selects a user agent string from the predefined list
        to help avoid detection by varying the browser fingerprint.

        Returns:
            str: A randomly selected user agent string representing
                a modern browser.
        """
        return random.choice(self.user_agents)

    def setup_enhanced_session(self) -> requests.Session:
        """Setup enhanced session with better headers and cookies.

        Creates a requests session with headers that mimic a real browser
        and adds common cookies to avoid detection. This method configures
        a session with realistic browser headers and cookies to make the
        requests appear as if they are coming from a legitimate browser.
        
        The headers include:
        - User-Agent: A randomly selected browser user agent
        - Accept: Common MIME types accepted by browsers
        - Accept-Language: Language preferences
        - DNT: Do Not Track preference
        - Various Sec-Fetch headers to mimic browser security features

        Returns:
            requests.Session: Configured session with enhanced headers
                and cookies for improved anti-detection.
        """
        session = requests.Session()

        # Enhanced headers to look more like a real browser
        session.headers.update(
            {
                "User-Agent": self.get_random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Cache-Control": "max-age=0",
            }
        )

        # Add some common cookies that real browsers have
        session.cookies.update(
            {
                "session_id": f"session_{random.randint(1000000, 9999999)}",
                "user_pref": "en_US",
            }
        )

        return session

    def setup_stealth_chrome_options(self) -> Options:
        """Setup Chrome options for stealth browsing.

        Configures Chrome options to avoid detection by anti-bot systems
        including disabling automation indicators and setting realistic preferences.
        This method implements multiple techniques to make the Chrome browser
        appear as a regular user browser rather than an automated one:
        
        1. Disables automation-related flags and properties
        2. Configures realistic window size and viewport
        3. Sets a random user agent
        4. Disables features that might reveal automation
        5. Configures browser preferences to match typical user settings
        
        These settings help bypass anti-bot systems that look for
        browser fingerprints and automation indicators.

        Returns:
            Options: Configured Chrome options for stealth browsing with
                enhanced anti-detection capabilities.
        """
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
        options.add_experimental_option(
            "prefs",
            {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2,
            },
        )

        return options

    def setup_undetected_chrome(self) -> Optional[webdriver.Chrome]:
        """Setup undetected Chrome driver with enhanced anti-detection.

        Attempts to create an undetected Chrome driver with stealth options.
        Falls back to regular Chrome if undetected-chromedriver is not available.
        
        This method uses the undetected-chromedriver library which provides
        advanced anti-detection capabilities by patching the ChromeDriver to
        avoid detection by anti-bot systems. It implements multiple techniques:
        
        1. Uses undetected-chromedriver if available
        2. Configures stealth options to avoid detection
        3. Executes JavaScript to modify browser properties
        4. Sets realistic window size and viewport
        5. Configures browser preferences to match typical user settings
        
        The method includes error handling and fallback mechanisms in case
        the undetected-chromedriver fails or is not available.

        Returns:
            Optional[webdriver.Chrome]: Configured Chrome driver with enhanced
                anti-detection capabilities, or None if setup failed.
        """
        if not UNDETECTED_AVAILABLE:
            print("Undetected Chrome not available")
            return None

        try:
            # Create fresh options for each attempt
            options = uc.ChromeOptions()

            # Basic stealth options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")

            # Window and viewport settings
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")

            # User agent
            options.add_argument(f"--user-agent={self.get_random_user_agent()}")

            # Experimental options to avoid detection
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            options.add_experimental_option(
                "prefs",
                {
                    "profile.default_content_setting_values.notifications": 2,
                    "profile.default_content_settings.popups": 0,
                    "profile.managed_default_content_settings.images": 2,
                    "profile.default_content_setting_values.media_stream": 2,
                    "profile.default_content_setting_values.geolocation": 2,
                    "profile.default_content_setting_values.mixed_script": 1,
                },
            )

            # Create driver with version_main parameter for better compatibility
            try:
                driver = uc.Chrome(options=options, version_main=None)
            except Exception:
                # Fallback without version_main
                driver = uc.Chrome(options=options)

            # Execute stealth scripts
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            driver.execute_script(
                "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})"
            )
            driver.execute_script(
                "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})"
            )

            return driver
        except Exception as e:
            print(f"Failed to setup undetected Chrome: {e}")
            return None

    def handle_captcha(self, driver: webdriver.Chrome) -> bool:
        """Handle captcha challenges on the page.

        Detects various types of captcha challenges and attempts to solve them
        or provide manual intervention options. This method implements a
        comprehensive approach to captcha detection and handling:
        
        1. Detects various types of captchas (reCAPTCHA, hCaptcha, etc.)
        2. Identifies captcha challenges using multiple selectors
        3. Attempts to solve simple captchas automatically
        4. Provides options for manual intervention when needed
        
        The method searches for common captcha elements using CSS selectors
        and XPath expressions, and delegates to specialized methods for
        solving different types of captchas.

        Args:
            driver: The Chrome webdriver instance with the loaded page.

        Returns:
            bool: True if captcha was detected and handled (either solved
                automatically or manual intervention was provided),
                False if no captcha was detected.
        """
        try:
            # Check for common captcha elements
            captcha_selectors = [
                "iframe[src*='captcha']",
                "iframe[src*='recaptcha']",
                "iframe[src*='hcaptcha']",
                ".captcha",
                ".recaptcha",
                "#captcha",
                "#recaptcha",
            ]

            for selector in captcha_selectors:
                captcha_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if captcha_elements:
                    print(f"Captcha detected with selector: {selector}")
                    return self.solve_captcha(driver, captcha_elements[0])

            # Check for text-based captcha
            captcha_text = driver.find_elements(
                By.XPATH,
                "//*[contains(text(), 'captcha') or contains(text(), 'verify')]",
            )
            if captcha_text:
                print("Text-based captcha detected")
                return self.handle_text_captcha(driver)

            return False

        except Exception as e:
            print(f"Error handling captcha: {e}")
            return False

    def solve_captcha(self, driver: webdriver.Chrome, captcha_element: Any) -> bool:
        """Attempt to solve captcha automatically.

        Tries to interact with captcha elements to solve them automatically.
        Falls back to manual intervention if automatic solving fails. This
        method implements techniques to solve common captcha challenges:
        
        1. Switches to the captcha iframe if present
        2. Looks for and clicks on captcha checkboxes
        3. Waits for the captcha to be solved
        4. Switches back to the main content
        
        The method is primarily designed to handle simple checkbox-based
        captchas. More complex captchas may require manual intervention.

        Args:
            driver: The Chrome webdriver instance with the loaded page.
            captcha_element: The captcha element (typically an iframe)
                to interact with.

        Returns:
            bool: True if captcha interaction was attempted (regardless
                of whether it was successfully solved), False if an error
                occurred during the interaction.
        """
        try:
            # Try to switch to captcha iframe
            driver.switch_to.frame(captcha_element)

            # Look for common captcha solving elements
            checkbox = driver.find_elements(
                By.CSS_SELECTOR, ".recaptcha-checkbox, .h-captcha"
            )
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

    def handle_text_captcha(self, driver: webdriver.Chrome) -> bool:
        """Handle text-based captcha challenges.

        Detects text-based captcha challenges and provides manual intervention
        options for the user to solve them. This method is designed to handle
        text-based captchas that require human input:
        
        1. Looks for input fields that might be part of a captcha
        2. Prompts the user to manually solve the captcha when detected
        3. Waits for the user to complete the captcha challenge
        
        This method is used when automatic captcha solving is not possible
        and human intervention is required.

        Args:
            driver: The Chrome webdriver instance with the loaded page.

        Returns:
            bool: True if a text-based captcha was detected and the user
                was prompted to solve it, False if no text-based captcha
                was detected or an error occurred.
        """
        try:
            # Look for input fields that might be captcha
            captcha_inputs = driver.find_elements(
                By.CSS_SELECTOR, "input[type='text'], input[name*='captcha']"
            )

            if captcha_inputs:
                print("Text captcha detected, manual intervention required")
                # For now, we'll just wait and let user handle manually
                input(
                    "Please solve the captcha manually and press Enter to continue..."
                )
                return True

            return False

        except Exception as e:
            print(f"Error handling text captcha: {e}")
            return False

    def add_human_behavior(self, driver: webdriver.Chrome) -> None:
        """Add enhanced human-like behavior to avoid detection.

        Simulates natural human browsing behavior including scrolling
        patterns and reading pauses to avoid bot detection. This method
        implements realistic human-like interactions with the page:
        
        1. Calculates page dimensions to determine scroll positions
        2. Implements natural scrolling patterns with varying speeds
        3. Adds random pauses to simulate reading behavior
        4. Uses randomization to make behavior less predictable
        
        These behaviors help avoid detection by systems that look for
        patterns typical of automated browsing.

        Args:
            driver: The Chrome webdriver instance with the loaded page.
            
        Returns:
            None
            
        Note:
            This method catches and handles exceptions that may occur
            during the simulation of human behavior to ensure the
            scraping process can continue even if behavior simulation fails.
        """
        try:
            # Get page dimensions
            page_height = driver.execute_script("return document.body.scrollHeight")
            viewport_height = driver.execute_script("return window.innerHeight")

            # Simulate natural scrolling patterns (less aggressive)
            scroll_positions = [100, 300, 500]
            for pos in scroll_positions:
                if pos < page_height:
                    driver.execute_script(f"window.scrollTo(0, {pos});")
                    time.sleep(random.uniform(1.0, 2.5))

            # Simulate reading behavior
            if random.random() < 0.7:
                # Pause as if reading content
                time.sleep(random.uniform(2.0, 4.0))

        except Exception as e:
            print(f"Error adding human behavior: {e}")

    def check_for_blocking(self, driver: webdriver.Chrome) -> bool:
        """Check if the page is blocking access.

        Analyzes the page source for common blocking indicators
        like captcha, robot detection, or access denied messages.
        This method examines the page content for signs that the
        website is blocking automated access:
        
        1. Searches for common blocking keywords in the page source
        2. Detects various types of blocking messages and indicators
        3. Identifies access denied, rate limiting, and robot detection
        
        The detection is based on a list of common blocking indicators
        that are frequently used by websites to block automated access.

        Args:
            driver: The Chrome webdriver instance with the loaded page.

        Returns:
            bool: True if blocking is detected (the page contains
                indicators of blocking automated access), False if
                no blocking indicators are found or an error occurs.
        """
        try:
            page_source = driver.page_source.lower()
            blocking_indicators = [
                "blocked",
                "captcha",
                "verify",
                "robot",
                "automation",
                "access denied",
                "forbidden",
                "rate limit",
                "too many requests",
            ]

            for indicator in blocking_indicators:
                if indicator in page_source:
                    print(f"Blocking detected: {indicator}")
                    return True

            return False

        except Exception as e:
            print(f"Error checking for blocking: {e}")
            return False

    def scrape_with_retry(
        self, keyword: str, max_results: Optional[int] = None, max_retries: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """Scrape with retry logic and multiple methods.

        Attempts to scrape auction results using multiple methods with
        fallback mechanisms and retry logic. This method implements a
        comprehensive approach to web scraping with multiple fallback
        mechanisms:
        
        1. First tries undetected-chromedriver (if available)
        2. Falls back to regular Chrome with stealth options
        3. Finally attempts cloudscraper as a last resort
        
        Between retry attempts, the method implements random delays
        to avoid detection by rate-limiting systems.

        Args:
            keyword: The search keyword to scrape for.
            max_results: Maximum number of results to return.
                Default is 10 results.
            max_retries: Number of retry attempts for each method.
                Default is 3 retry attempts.

        Returns:
            List[Dict[str, str]]: List of auction result dictionaries.
            Each dictionary contains the following keys:
                - "Item Description": Description of the auction item
                - "Current price": Current price of the item
                - "Auction end date": End date of the auction
                - "Auction image / thumbnail URL (extra credit)": Image URL
                
        Note:
            If all scraping methods fail, the method returns a list with
            a single dictionary containing error information.
        """

        # Get configuration if not provided
        from config import get_config
        
        if max_results is None:
            max_results = get_config().MAX_RESULTS
            
        if max_retries is None:
            max_retries = get_config().SCRAPER_MAX_RETRIES
            
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
                    from error_handling import handle_error, ScrapingError
                    handle_error(
                        error=e,
                        context="Undetected Chrome scraping failed",
                        reraise=False,
                        error_type=ScrapingError
                    )
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
                from error_handling import handle_error, ScrapingError
                handle_error(
                    error=e,
                    context="Regular Chrome scraping failed",
                    reraise=False,
                    error_type=ScrapingError
                )
            finally:
                if driver:
                    driver.quit()

            # Try cloudscraper as fallback
            try:
                results = self.scrape_with_cloudscraper(keyword, max_results)
                if results and len(results) > 1:
                    return results
            except Exception as e:
                from error_handling import handle_error, NetworkError
                handle_error(
                    error=e,
                    context="Cloudscraper fallback failed",
                    reraise=False,
                    error_type=NetworkError
                )

            # Wait before retry
            if attempt < max_retries - 1:
                wait_time = random.uniform(5, 15)
                print(f"Waiting {wait_time:.1f} seconds before retry...")
                time.sleep(wait_time)

        # If all methods fail, return error result
        return [
            {
                "Item Description": f"All scraping methods failed for '{keyword}' - website may be blocking automated access",
                "Current price": "N/A",
                "Auction end date": "N/A",
                "Auction image / thumbnail URL (extra credit)": "",
            }
        ]

    def scrape_with_driver(
        self, driver: webdriver.Chrome, keyword: str, max_results: int = 10
    ) -> List[Dict[str, str]]:
        """Scrape using Selenium driver.

        Performs web scraping using Selenium WebDriver with enhanced
        anti-detection measures and human behavior simulation. This method
        implements a comprehensive approach to web scraping with Selenium,
        including:
        
        1. Multiple search URL formats to handle different encoding methods
        2. Human behavior simulation (scrolling, pauses)
        3. Captcha detection and handling
        4. Content waiting and extraction
        
        The method tries different URL formats to find the one that works
        best for the current website structure and implements various
        anti-detection measures to avoid being blocked.

        Args:
            driver: The Chrome webdriver instance.
            keyword: The search keyword to scrape for.
            max_results: Maximum number of results to return.
                Default is 10 results.

        Returns:
            List[Dict[str, str]]: List of auction result dictionaries.
            Each dictionary contains the following keys:
                - "Item Description": Description of the auction item
                - "Current price": Current price of the item
                - "Auction end date": End date of the auction
                - "Auction image / thumbnail URL (extra credit)": Image URL
                
        Note:
            If an error occurs during scraping, the method returns a list
            with a single dictionary containing error information.
        """
        base_url = "https://shopgoodwill.com"

        # Try different search URL formats
        search_urls = [
            f"{base_url}/search?keywords={keyword.replace(' ', '+')}&sort=Closing",
            f"{base_url}/search?keywords={keyword.replace(' ', '%20')}&sort=Closing",
            f"{base_url}/search?keywords={keyword}&sort=Closing",
            f"{base_url}/search?keywords={keyword.replace(' ', '-')}&sort=Closing",
        ]

        results = []

        try:
            # Try multiple search URL formats
            current_url = None
            for i, search_url in enumerate(search_urls):
                print(f"Trying search URL {i+1}: {search_url}")
                driver.get(search_url)

                # Wait a moment for any redirects
                time.sleep(2)
                current_url = driver.current_url
                print(f"Current URL after navigation: {current_url}")

                # Check if we're on a search page
                if (
                    "search" in current_url
                    or "results" in current_url
                    or "auction" in current_url
                ):
                    print(
                        f"Successfully navigated to search page with URL format {i+1}"
                    )
                    break
                elif i < len(search_urls) - 1:  # Not the last URL to try
                    print(
                        f"URL format {i+1} redirected to homepage, trying next format..."
                    )
                else:
                    print(
                        "All URL formats redirected to homepage, proceeding anyway..."
                    )

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
            from error_handling import handle_error, ScrapingError
            
            # Log the error but don't reraise to allow returning an error result
            handle_error(
                error=e,
                context=f"Error during scraping for '{keyword}'",
                reraise=False,
                error_type=ScrapingError
            )
            
            # Return error result
            return [
                {
                    "Item Description": f"Error scraping results for '{keyword}': {str(e)}",
                    "Current price": "N/A",
                    "Auction end date": "N/A",
                    "Auction image / thumbnail URL (extra credit)": "",
                }
            ]

    def scrape_with_cloudscraper(
        self, keyword: str, max_results: int = 10
    ) -> List[Dict[str, str]]:
        """Scrape using enhanced cloudscraper as fallback.

        Uses cloudscraper library to bypass anti-bot measures and
        extract auction results from the website. This method is used
        as a fallback when Selenium-based approaches fail and implements
        several techniques to avoid detection:
        
        1. Enhanced session with realistic headers and cookies
        2. Multiple search URL formats to handle different encoding methods
        3. Random delays between requests
        4. User agent rotation
        
        The method tries different URL formats sequentially until it finds
        one that returns valid results.

        Args:
            keyword: The search keyword to scrape for.
            max_results: Maximum number of results to return.
                Default is 10 results.

        Returns:
            List[Dict[str, str]]: List of auction result dictionaries.
            Each dictionary contains the following keys:
                - "Item Description": Description of the auction item
                - "Current price": Current price of the item
                - "Auction end date": End date of the auction
                - "Auction image / thumbnail URL (extra credit)": Image URL
                
        Note:
            If all URL formats fail or an error occurs, the method returns
            a list with a single dictionary containing error information.
        """
        base_url = "https://shopgoodwill.com"

        # Try different search URL formats
        search_urls = [
            f"{base_url}/search?keywords={keyword.replace(' ', '+')}&sort=Closing",
            f"{base_url}/search?keywords={keyword.replace(' ', '%20')}&sort=Closing",
            f"{base_url}/search?keywords={keyword}&sort=Closing",
            f"{base_url}/search?keywords={keyword.replace(' ', '-')}&sort=Closing",
        ]

        try:
            # Use enhanced session
            session = self.setup_enhanced_session()

            # Enhanced headers
            headers = {
                "User-Agent": self.get_random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Cache-Control": "max-age=0",
                "DNT": "1",
            }

            # Try multiple search URL formats
            for search_url in search_urls:
                print(f"Trying cloudscraper with URL: {search_url}")
                try:
                    # Add delay between requests
                    time.sleep(random.uniform(2, 5))

                    response = self.scraper.get(search_url, headers=headers, timeout=30)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.text, "html.parser")
                    results = self.extract_results_from_soup(soup, keyword, max_results)

                    if (
                        results
                        and len(results) > 0
                        and not any("Error" in str(r) for r in results)
                    ):
                        print(f"Successfully scraped with URL: {search_url}")
                        return results
                    else:
                        print(
                            f"No results found with URL: {search_url}, trying next..."
                        )
                except Exception as e:
                    print(f"Failed with URL {search_url}: {e}")
                    continue

            # If all URLs failed, return error result
            return [
                {
                    "Item Description": f"All search URL formats failed for '{keyword}'",
                    "Current price": "N/A",
                    "Auction end date": "N/A",
                    "Auction image / thumbnail URL (extra credit)": "",
                }
            ]

        except Exception as e:
            from error_handling import handle_error, NetworkError
            
            # Log the error but don't reraise to allow returning an error result
            handle_error(
                error=e,
                context=f"Cloudscraper error for '{keyword}'",
                reraise=False,
                error_type=NetworkError
            )
            
            # Return error result
            return [
                {
                    "Item Description": f"Cloudscraper failed for '{keyword}': {str(e)}",
                    "Current price": "N/A",
                    "Auction end date": "N/A",
                    "Auction image / thumbnail URL (extra credit)": "",
                }
            ]

    def extract_results_from_soup(
        self, soup: BeautifulSoup, keyword: str, max_results: int = 10
    ) -> List[Dict[str, str]]:
        """Extract results from BeautifulSoup object.

        Parses the HTML content to extract auction item information
        including descriptions, prices, dates, and image URLs. This method
        implements a robust parsing strategy that tries multiple CSS selectors
        to find product elements, even when the website structure changes.
        
        The method uses a series of increasingly general selectors and
        filtering techniques to identify auction items while avoiding
        navigation elements, headers, footers, etc.

        Args:
            soup: BeautifulSoup object containing the page HTML.
            keyword: The search keyword used for scraping.
            max_results: Maximum number of results to extract.
                Default is 10 results.

        Returns:
            List[Dict[str, str]]: List of auction result dictionaries.
            Each dictionary contains the following keys:
                - "Item Description": Description of the auction item
                - "Current price": Current price of the item
                - "Auction end date": End date of the auction
                - "Auction image / thumbnail URL (extra credit)": Image URL
                
        Note:
            If no product elements are found or parsing fails, the method
            returns a list with a single dictionary containing error information.
        """
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
                            "sign in",
                            "login",
                            "register",
                            "cart",
                            "search",
                            "menu",
                            "nav",
                            "header",
                            "footer",
                        ]
                    ):
                        continue
                    filtered_elements.append(elem)

                if filtered_elements:
                    product_elements = filtered_elements
                    print(
                        f"After filtering, found {len(product_elements)} potential product elements"
                    )
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
                    or item.find(
                        "div",
                        class_=lambda x: x
                        and any(
                            word in str(x).lower() for word in ["title", "name", "desc"]
                        ),
                    )
                )
                item_data["Item Description"] = (
                    description_elem.get_text(strip=True)
                    if description_elem
                    else f"Item {i+1}"
                )

                # Extract price
                price_elem = (
                    item.find("span", class_=lambda x: x and "price" in str(x).lower())
                    or item.find(
                        "div", class_=lambda x: x and "price" in str(x).lower()
                    )
                    or item.find("span", string=lambda x: x and "$" in x)
                    or item.find("div", string=lambda x: x and "$" in x)
                )
                item_data["Current price"] = (
                    price_elem.get_text(strip=True)
                    if price_elem
                    else "Price not available"
                )

                # Extract date
                date_elem = (
                    item.find(
                        "div",
                        class_=lambda x: x
                        and any(
                            word in str(x).lower()
                            for word in ["date", "time", "end", "timer"]
                        ),
                    )
                    or item.find(
                        "span",
                        class_=lambda x: x
                        and any(
                            word in str(x).lower()
                            for word in ["date", "time", "end", "timer"]
                        ),
                    )
                    or item.find(
                        "div",
                        string=lambda x: x
                        and any(
                            word in x.lower()
                            for word in ["end", "closing", "time", "date"]
                        ),
                    )
                    or item.find(
                        "span",
                        string=lambda x: x
                        and any(
                            word in x.lower()
                            for word in ["end", "closing", "time", "date"]
                        ),
                    )
                )
                item_data["Auction end date"] = (
                    date_elem.get_text(strip=True)
                    if date_elem
                    else "Date not available"
                )

                # Extract image with enhanced logic
                img_elem = (
                    item.find("img", src=True)
                    or item.find("img", {"data-src": True})
                    or item.find("img", {"data-lazy": True})
                    or item.find("img", {"data-original": True})
                )

                image_url = ""
                if img_elem:
                    # Try different image source attributes
                    image_url = (
                        img_elem.get("src", "")
                        or img_elem.get("data-src", "")
                        or img_elem.get("data-lazy", "")
                        or img_elem.get("data-original", "")
                    )

                    # Make sure URL is absolute
                    if image_url and image_url.startswith("//"):
                        image_url = "https:" + image_url
                    elif image_url and image_url.startswith("/"):
                        image_url = "https://shopgoodwill.com" + image_url

                item_data["Auction image / thumbnail URL (extra credit)"] = image_url

                if (
                    item_data["Item Description"]
                    and item_data["Item Description"] != f"Item {i+1}"
                ):
                    results.append(item_data)

            except Exception as e:
                print(f"Error processing item {i+1}: {e}")
                continue

        if not results:
            results.append(
                {
                    "Item Description": f"No results found for '{keyword}' - website may be blocking automated access",
                    "Current price": "N/A",
                    "Auction end date": "N/A",
                    "Auction image / thumbnail URL (extra credit)": "",
                }
            )

        return results


# Global scraper instance
_scraper_instance: Optional[AntiDetectionScraper] = None


def get_scraper() -> AntiDetectionScraper:
    """Get the global scraper instance.

    Creates a singleton instance of AntiDetectionScraper if it doesn't exist
    and returns it for reuse across the application. This function implements
    the singleton pattern to ensure that only one scraper instance is created
    and reused throughout the application.
    
    Using a singleton instance helps:
    1. Reduce resource usage by reusing the same session
    2. Maintain consistent behavior across multiple scraping operations
    3. Avoid creating multiple browser instances unnecessarily

    Returns:
        AntiDetectionScraper: The global scraper instance that can be
            used for scraping operations.
    """
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = AntiDetectionScraper()
    return _scraper_instance


def scrape_auction_results(keyword: str, max_results: Optional[int] = None) -> List[Dict[str, str]]:
    """Enhanced scrape auction results with anti-detection and captcha handling.

    Main function to scrape auction results from shopgoodwill.com with
    comprehensive anti-detection measures and fallback mechanisms. This
    function serves as the primary entry point for scraping operations
    and provides a simple interface to the complex scraping functionality.
    
    The function:
    1. Gets or creates a singleton scraper instance
    2. Delegates to the scraper's retry mechanism
    3. Returns the scraped auction results
    
    This approach encapsulates the complexity of the scraping process
    while providing a simple interface for external code.

    Args:
        keyword: The search keyword to scrape for.
        max_results: Maximum number of results to return.
            If None, uses the configured MAX_RESULTS from config.

    Returns:
        List[Dict[str, str]]: List of dictionaries with auction result data.
        Each dictionary contains the following keys:
            - "Item Description": Description of the auction item
            - "Current price": Current price of the item
            - "Auction end date": End date of the auction
            - "Auction image / thumbnail URL (extra credit)": Image URL
    """
    from config import get_config
    
    # Use configured max_results if not specified
    if max_results is None:
        max_results = get_config().MAX_RESULTS
        
    # Use configured max_retries
    max_retries = get_config().SCRAPER_MAX_RETRIES
    
    scraper = get_scraper()
    return scraper.scrape_with_retry(keyword, max_results, max_retries)

import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


def scrape_auction_results(keyword: str, max_results: int = 10) -> list:
    """
    Scrape auction results from shopgoodwill.com for a given keyword using Selenium.
    Returns a list of dictionaries with the required fields.
    """
    base_url = "https://shopgoodwill.com"
    search_url = f"{base_url}/search?keywords={keyword.replace(' ', '+')}&sort=Closing"
    results = []

    # Setup Chrome options to avoid detection
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    driver = None
    try:
        # Initialize the driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Execute script to remove webdriver property
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        # Navigate to the search page
        print(f"Navigating to: {search_url}")
        driver.get(search_url)

        # Wait for the page to load and content to appear
        wait = WebDriverWait(driver, 20)

        # Wait for any dynamic content to load
        time.sleep(random.uniform(3, 5))

        # Try to find the main content area
        try:
            # Wait for the main content container
            main_content = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "main, .container, .content, [class*='main']")
                )
            )
            print("Found main content area")
        except:
            print("Main content area not found, proceeding anyway")

        # Wait a bit more for dynamic content
        time.sleep(random.uniform(5, 8))

        # Get the page source after JavaScript has rendered
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Check if we got blocked or redirected
        if "blocked" in page_source.lower() or "captcha" in page_source.lower():
            print("Warning: Page might be blocked or showing CAPTCHA")
            # Create a meaningful fallback result
            results.append(
                {
                    "Item Description": f"Search for '{keyword}' was blocked by website security measures",
                    "Current price": "N/A",
                    "Auction end date": "N/A",
                    "Auction image / thumbnail URL (extra credit)": "",
                }
            )
            return results

        # Try to find product elements with various selectors
        product_elements = []

        # Try multiple selectors to find products, focusing on actual product listings
        selectors_to_try = [
            ".p-datatable-tbody tr",  # Angular PrimeNG table rows
            "div[class*='product']",
            "div[class*='item']:not([class*='nav']):not([class*='header']):not([class*='footer'])",
            "div[class*='card']:not([class*='nav']):not([class*='header']):not([class*='footer'])",
            "div[class*='auction']",
            "[class*='ng-star-inserted']:not([class*='nav']):not([class*='header']):not([class*='footer'])",
            "div[class*='col']:not([class*='nav']):not([class*='header']):not([class*='footer'])",
            "div[class*='row'] > div:not([class*='nav']):not([class*='header']):not([class*='footer'])",
            "a[href*='/item/']",  # Direct links to items
            "div:has(a[href*='/item/'])",  # Containers with item links
        ]

        for selector in selectors_to_try:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} elements with selector: {selector}")
                # Filter out navigation and header elements
                filtered_elements = []
                for elem in elements:
                    elem_text = elem.get_text().lower()
                    elem_classes = " ".join(elem.get("class", [])).lower()
                    # Skip navigation, header, footer elements
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

        # If still no products, try to find any clickable elements that might be products
        if not product_elements:
            print("Trying to find any clickable elements...")
            links = soup.find_all("a", href=True)
            product_links = [link for link in links if "/item/" in link.get("href", "")]
            print(f"Found {len(product_links)} product links")

            # Get the parent containers of these links
            for link in product_links:
                parent = link.parent
                if parent and parent not in product_elements:
                    product_elements.append(parent)

        # If still no products, try a different approach - look for any content that might be products
        if not product_elements:
            print("Trying alternative approach - looking for any content containers...")
            # Look for any divs that might contain product information
            all_divs = soup.find_all("div")
            potential_products = []
            for div in all_divs:
                div_text = div.get_text().strip()
                # Look for divs that might contain product info (have some text but not too much)
                if len(div_text) > 10 and len(div_text) < 500:
                    # Check if it contains any product-like content
                    if any(
                        word in div_text.lower()
                        for word in ["$", "price", "bid", "auction", "item", "lot"]
                    ):
                        potential_products.append(div)

            if potential_products:
                product_elements = potential_products[:max_results]
                print(f"Found {len(product_elements)} potential product containers")

        # Process found elements
        for i, item in enumerate(product_elements[:max_results]):
            try:
                # Extract data from the element
                item_data = {}

                # Try to find description - look for links first, then other text elements
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

                # Try to find price - look for elements with price-related classes or text
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

                # Try to find end date - look for elements with date/time related classes or text
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

                # Try to find image
                img_elem = item.find("img")
                item_data["Auction image / thumbnail URL (extra credit)"] = (
                    img_elem.get("src", "") if img_elem else ""
                )

                # Only add if it has meaningful content
                if (
                    item_data["Item Description"]
                    and item_data["Item Description"] != f"Item {i+1}"
                ):
                    results.append(item_data)

            except Exception as e:
                print(f"Error processing item {i+1}: {e}")
                continue

        print(f"Successfully processed {len(results)} items")

        # If no results found, create a fallback result to indicate the search was attempted
        if not results:
            print("No results found - creating fallback entry")
            results.append(
                {
                    "Item Description": f"No results found for '{keyword}' - website may be blocking automated access",
                    "Current price": "N/A",
                    "Auction end date": "N/A",
                    "Auction image / thumbnail URL (extra credit)": "",
                }
            )

    except Exception as e:
        print(f"Error during scraping: {e}")
        # Create a fallback result
        results.append(
            {
                "Item Description": f"Error scraping results for '{keyword}': {str(e)}",
                "Current price": "N/A",
                "Auction end date": "N/A",
                "Auction image / thumbnail URL (extra credit)": "",
            }
        )

    finally:
        try:
            if driver:
                driver.quit()
        except:
            pass

    return results

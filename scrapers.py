# This is the full code for: scrapers.py

import re
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Croma Bot Class (Fixed with Human Typing) ---

class CromaScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--window-position=-3000,0")  # Hide window
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            print(f"Croma: Failed to start browser: {e}")
            raise
    
    def human_type(self, element, text):
        """Type like a human with random delays"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # Random delays
    
    def handle_all_popups(self):
        """Comprehensive popup handler for all websites"""
        try:
            # Try multiple close button selectors
            close_selectors = [
                ".close", ".popup-close", "[data-role='close']", 
                ".modal-close", "button[aria-label*='close']", 
                ".btn-close", ".close-button", ".x-close",
                "#close", ".close-btn", "[class*='close']"
            ]
            
            for selector in close_selectors:
                try:
                    close_btn = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    close_btn.click()
                    print(f"Croma: Closed popup with selector: {selector}")
                    time.sleep(1)
                except:
                    continue
            
            # Try Escape key as fallback
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ESCAPE)
                time.sleep(1)
            except:
                pass
                
        except Exception as e:
            print(f"Croma: Popup handling failed: {e}")
    
    def search_product(self, product_name):
        try:
            self.driver.get("https://www.croma.com")
            time.sleep(2)
            
            # Handle popups
            self.handle_all_popups()
            
            search_box = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#searchV2"))
            )
            
            search_box.clear()
            # FIXED: Added human-like typing
            self.human_type(search_box, product_name)
            time.sleep(1)
            search_box.send_keys(Keys.ENTER)
            time.sleep(4)
            
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.product-item, div.cp-product, [data-product]"))
            )
            
            product_data = self.extract_product_data()
            return product_data
            
        except Exception as e:
            print(f"Croma: Search failed: {e}")
            return None
    
    def extract_product_data(self):
        try:
            product = {}
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            product_container = soup.select_one('li.product-item, div.cp-product, [data-product]')
            
            if not product_container:
                return None
            
            product['brand'] = self.extract_brand(product_container)
            product['price'] = self.extract_price(product_container)
            product['discount_percentage'] = self.extract_discount(product_container)
            
            rating_data = self.extract_croma_rating_perfect(product_container)
            product['rating'] = rating_data['rating']
            product['review_count'] = rating_data['review_count']
            
            return product
            
        except Exception as e:
            print(f"Croma: Extraction failed: {e}")
            return None
    
    def extract_croma_rating_perfect(self, container):
        rating_data = {'rating': '0', 'review_count': '0'}
        try:
            # Try multiple rating container selectors
            rating_selectors = [
                '.cp-rating.plp-ratings',
                '.cp-rating',
                '.plp-ratings',
                '.ratings-plp',
                '[class*="rating"]'
            ]
            
            rating_container = None
            for selector in rating_selectors:
                rating_container = container.select_one(selector)
                if rating_container:
                    break
            
            if rating_container:
                # Try to find rating text in multiple ways
                rating_text_selectors = ['.rating-text', '.rating', 'span']
                for selector in rating_text_selectors:
                    rating_text_span = rating_container.select_one(selector)
                    if rating_text_span:
                        rating_text = rating_text_span.get_text(strip=True)
                        # Look for decimal numbers in rating
                        decimal_match = re.search(r'(\d+\.\d+)', rating_text)
                        if decimal_match:
                            rating_data['rating'] = decimal_match.group(1)
                            break
                
                # Try to find review count in multiple ways
                review_selectors = [
                    'span[style*="color: rgb(255, 255, 255)"]',
                    'span[class*="review"]',
                    'span[class*="count"]',
                    '.review-count'
                ]
                
                for selector in review_selectors:
                    review_elem = rating_container.select_one(selector)
                    if review_elem:
                        review_text = review_elem.get_text(strip=True)
                        review_match = re.search(r'\(?(\d+)\)?', review_text)
                        if review_match:
                            rating_data['review_count'] = review_match.group(1)
                            break
                
                # If no review count found, try parent container
                if rating_data['review_count'] == '0':
                    parent_text = rating_container.get_text()
                    review_match = re.search(r'\((\d+)\)', parent_text)
                    if review_match:
                        rating_data['review_count'] = review_match.group(1)
                        
            return rating_data
        except Exception as e:
            print(f"Croma rating extraction error: {e}")
            return rating_data
    
    def extract_brand(self, container):
        try:
            title_elem = container.select_one('h3.product-title, .product-title, h3 a, .product-name')
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                
                # Enhanced brand detection with better iPhone handling
                brands = {
                    'Apple': ['iphone', 'ipad', 'macbook', 'apple', 'mac', 'watch'],
                    'Samsung': ['samsung', 'galaxy'],
                    'OnePlus': ['oneplus'],
                    'Xiaomi': ['xiaomi', 'mi ', 'redmi', 'poco'],
                    'Realme': ['realme'],
                    'Oppo': ['oppo'],
                    'Vivo': ['vivo'],
                    'Lenovo': ['lenovo'],
                    'HP': ['hp ', 'hp[^a-z]'],
                    'Dell': ['dell'],
                    'Asus': ['asus'],
                    'Acer': ['acer'],
                    'MSI': ['msi'],
                    'JBL': ['jbl'],
                    'Boat': ['boat'],
                    'Sony': ['sony'],
                    'LG': ['lg'],
                    'Google': ['google', 'pixel']
                }
                
                title_lower = title_text.lower()
                
                for brand, keywords in brands.items():
                    for keyword in keywords:
                        if keyword in title_lower:
                            return brand
                
                # If no brand found, try first word
                first_word = title_text.split()[0]
                if first_word and len(first_word) > 2:
                    return first_word.title()
                    
            return "unknown"
        except:
            return "unknown"
    
    def extract_price(self, container):
        try:
            price_selectors = ['.amount', '.current-price', '.new-price', '.price', '[class*="price"]']
            for selector in price_selectors:
                price_elem = container.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    numbers = re.findall(r'[\d,]+', price_text)
                    if numbers:
                        price_clean = numbers[0].replace(',', '')
                        # Validate price is reasonable
                        if float(price_clean) > 1000:
                            return price_clean
            return "0"
        except:
            return "0"
    
    def extract_discount(self, container):
        try:
            discount_elem = container.select_one('.discount, .off, .save, [class*="discount"]')
            if discount_elem:
                discount_text = discount_elem.get_text(strip=True)
                numbers = re.findall(r'(\d+)%', discount_text)
                if numbers:
                    return numbers[0]
            
            original_elem = container.select_one('.old-price, .original-price, .was-price')
            current_elem = container.select_one('.amount, .current-price, .new-price')
            if original_elem and current_elem:
                original_text = original_elem.get_text(strip=True)
                current_text = current_elem.get_text(strip=True)
                original_price = re.findall(r'[\d,]+', original_text)
                current_price = re.findall(r'[\d,]+', current_text)
                if original_price and current_price:
                    original = float(original_price[0].replace(',', ''))
                    current = float(current_price[0].replace(',', ''))
                    if original > 0:
                        discount = ((original - current) / original) * 100
                        return f"{discount:.0f}"
            return "0"
        except:
            return "0"
    
    def close(self):
        if self.driver:
            self.driver.quit()

# --- Reliance Digital Bot Class (Fixed with Human Typing) ---

class RelianceDigitalScraper:
    def __init__(self):
        self.driver = None
        self.current_search_query = ""
        self.setup_driver()
    
    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--window-position=-3000,0")  # Hide window
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            print(f"Reliance: Failed to start browser: {e}")
            raise
    
    def human_type(self, element, text):
        """Type like a human with random delays"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # Random delays
    
    def handle_all_popups(self):
        """Comprehensive popup handler for all websites"""
        try:
            # Try multiple close button selectors
            close_selectors = [
                ".close", ".popup-close", "[data-role='close']", 
                ".modal-close", "button[aria-label*='close']", 
                ".btn-close", ".close-button", ".x-close",
                "#close", ".close-btn", "[class*='close']"
            ]
            
            for selector in close_selectors:
                try:
                    close_btn = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    close_btn.click()
                    print(f"Reliance: Closed popup with selector: {selector}")
                    time.sleep(1)
                except:
                    continue
            
            # Try Escape key as fallback
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ESCAPE)
                time.sleep(1)
            except:
                pass
                
        except Exception as e:
            print(f"Reliance: Popup handling failed: {e}")
    
    def search_product(self, product_name):
        try:
            self.current_search_query = product_name.lower()
            self.driver.get("https://www.reliancedigital.in")
            time.sleep(3)
            
            self.handle_all_popups()
            
            search_box = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 
                    "input[placeholder*='Search'], input[type='search'], #suggestionBox, .search__input"))
            )
            
            search_box.clear()
            self.human_type(search_box, product_name)
            time.sleep(1)
            search_box.send_keys(Keys.ENTER)
            time.sleep(5)
            
            # Wait for results with multiple possible selectors
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                    ".product-card, [data-v-4a642320], .sp__grid, .pl-grid, .search-result, [class*='product']"))
            )
            
            # Additional wait for content to load
            time.sleep(3)
            
            product_data = self.extract_product_data_enhanced()
            return product_data
            
        except Exception as e:
            print(f"Reliance: Search failed: {e}")
            return None
    
    def extract_product_data_enhanced(self):
        """Enhanced product data extraction for Reliance Digital"""
        try:
            product = {}
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            print("Reliance: Searching for product containers...")
            
            # Enhanced product selectors for Reliance Digital
            product_selectors = [
                '[data-v-4a642320]',  # Main product container
                '.product-card', 
                '.sp__grid', 
                '.pl-grid',
                '[class*="product-item"]',
                '[class*="product-card"]',
                '.slider-item'
            ]
            
            product_containers = []
            for selector in product_selectors:
                containers = soup.select(selector)
                product_containers.extend(containers)
            
            product_container = None
            
            for container in product_containers:
                container_text = container.get_text(strip=True)
                # Enhanced filtering - look for product keywords
                if len(container_text) > 50:
                    # Check if this looks like a real product (has price and reasonable content)
                    has_price = any(char in container_text for char in ['¥', '₹', 'Rs', 'INR', ','])
                    has_product_terms = any(term in container_text.lower() for term in ['gb', 'ram', 'storage', 'mobile', 'phone', 'laptop', 'earphone', 'headphone'])
                    
                    if has_price and has_product_terms:
                        print(f"Reliance: Potential product found: {container_text[:150]}...")
                        product_container = container
                        break
            
            if not product_container:
                print("Reliance: No valid product container found")
                # Try to get the first product-like container as fallback
                for container in product_containers[:5]:  # Check first 5 containers
                    container_text = container.get_text(strip=True)
                    if len(container_text) > 100:  # Reasonable length for a product
                        product_container = container
                        print(f"Reliance: Using fallback container: {container_text[:100]}...")
                        break
            
            if not product_container:
                return None
            
            # Enhanced brand extraction
            product['brand'] = self.extract_brand_enhanced(product_container)
            product['price'] = self.extract_price_enhanced(product_container)
            product['discount_percentage'] = self.extract_discount_enhanced(product_container)
            
            rating_data = self.extract_rating_enhanced(product_container)
            product['rating'] = rating_data['rating']
            product['review_count'] = rating_data['review_count']
            
            print(f"Reliance: Final extracted data - Brand: {product['brand']}, Price: {product['price']}, Discount: {product['discount_percentage']}%")
            return product
            
        except Exception as e:
            print(f"Reliance: Extraction failed: {e}")
            return None

    def extract_brand_enhanced(self, container):
        """Enhanced brand extraction specifically for Google Pixel"""
        try:
            # First, try to find the product title
            title_selectors = [
                '.product-card-title',
                '[class*="title"]',
                '[class*="name"]',
                'div[data-v-4a642320]',
                'h3', 'h2', 'h1'
            ]
            
            title_text = ""
            for selector in title_selectors:
                title_elem = container.select_one(selector)
                if title_elem:
                    title_text = title_elem.get_text(strip=True)
                    if title_text:
                        break
            
            if not title_text:
                # Fallback: get all text from container
                title_text = container.get_text(strip=True)
            
            print(f"Reliance: Title text found: {title_text}")
            
            # Enhanced brand detection with Google/Pixel specific handling
            title_lower = title_text.lower()
            
            # Google/Pixel specific detection
            if 'pixel' in title_lower or 'google' in title_lower:
                return 'Google'
            
            # Other brands
            brands = {
                'Apple': ['iphone', 'ipad', 'macbook', 'apple', 'mac'],
                'Samsung': ['samsung', 'galaxy'],
                'OnePlus': ['oneplus'],
                'Xiaomi': ['xiaomi', 'mi ', 'redmi', 'poco'],
                'Realme': ['realme'],
                'Oppo': ['oppo'],
                'Vivo': ['vivo'],
                'Google': ['google', 'pixel'],
                'Nothing': ['nothing'],
                'Motorola': ['motorola', 'moto'],
                'Lenovo': ['lenovo'],
                'HP': ['hp ', 'hp[^a-z]'],
                'Dell': ['dell'],
                'Asus': ['asus'],
                'Acer': ['acer'],
                'MSI': ['msi'],
                'JBL': ['jbl'],
                'Boat': ['boat'],
                'Sony': ['sony']
            }
            
            for brand, keywords in brands.items():
                for keyword in keywords:
                    if keyword in title_lower:
                        return brand
            
            return "unknown"
            
        except Exception as e:
            print(f"Reliance: Brand extraction error: {e}")
            return "unknown"

    def extract_price_enhanced(self, container):
        """Enhanced price extraction for Reliance Digital - handles promotional text"""
        try:
            container_text = container.get_text()
            print(f"Reliance: Container text: {container_text[:200]}...")
            
            # Remove promotional text that contains numbers but aren't prices
            # Remove lines like "4K Disc", "6M NCEMI", etc.
            cleaned_text = re.sub(r'\b\d+[KMG]?\s*(?:Disc|NCEMI|HDFC|CC|\+|\*)\b', '', container_text, flags=re.IGNORECASE)
            
            # Enhanced price patterns - handle both ¥ and ₹ symbols, and various formats
            price_patterns = [
                r'[¥₹]\s*([\d,]+\.?\d*)',  # Symbol followed by numbers
                r'Rs\.\s*([\d,]+\.?\d*)',   # Rs. format
                r'INR\s*([\d,]+\.?\d*)',    # INR format
                r'([\d,]+\.?\d*)\s*[¥₹]',   # Numbers followed by symbol
            ]
            
            all_prices = []
            for pattern in price_patterns:
                prices = re.findall(pattern, cleaned_text)
                for price in prices:
                    price_clean = price.replace(',', '')
                    try:
                        price_num = float(price_clean)
                        # Validate it's a reasonable price (not from "4K", "6M", etc.)
                        if 1000 <= price_num <= 500000:  # Reasonable range for smartphones
                            all_prices.append(price_num)
                            print(f"Reliance: Found valid price: {price_num}")
                    except ValueError:
                        continue
            
            if all_prices:
                # Return the smallest price (usually the current price, not MRP)
                return str(min(all_prices))
            
            print("Reliance: No valid price found after filtering promotional text")
            return "0"
            
        except Exception as e:
            print(f"Reliance: Price extraction error: {e}")
            return "0"

    def extract_discount_enhanced(self, container):
        """Enhanced discount extraction"""
        try:
            # Try discount selectors
            discount_selectors = [
                '.discount',
                '[class*="discount"]',
                '.off',
                '.save',
                '[class*="off"]'
            ]
        
            for selector in discount_selectors:
                discount_elem = container.select_one(selector)
                if discount_elem:
                    discount_text = discount_elem.get_text(strip=True)
                    numbers = re.findall(r'(\d+)%', discount_text)
                    if numbers:
                        return numbers[0]
            
            # Look for discount in container text
            container_text = container.get_text()
            discount_match = re.search(r'(\d+)%\s*OFF', container_text, re.IGNORECASE)
            if discount_match:
                return discount_match.group(1)
            
            return "0"
            
        except Exception as e:
            print(f"Reliance: Discount extraction error: {e}")
            return "0"

    def extract_rating_enhanced(self, container):
        """Enhanced rating extraction"""
        rating_data = {'rating': '0', 'review_count': '0'}
        try:
            # Try multiple rating selectors
            rating_selectors = [
                '.rating-star-list',
                '[class*="rating"]',
                '[class*="star"]',
                '.ratings'
            ]
            
            for selector in rating_selectors:
                rating_elem = container.select_one(selector)
                if rating_elem:
                    rating_text = rating_elem.get_text(strip=True)
                    # Look for decimal rating
                    decimal_match = re.search(r'(\d+\.\d+)', rating_text)
                    if decimal_match:
                        rating_data['rating'] = decimal_match.group(1)
                        break
            
            # Try to find review count
            review_selectors = [
                '[class*="review"]',
                '[class*="rating"] span',
                '.review-count'
            ]
            
            for selector in review_selectors:
                review_elem = container.select_one(selector)
                if review_elem:
                    review_text = review_elem.get_text(strip=True)
                    numbers = re.findall(r'\(?(\d+)\)?', review_text)
                    if numbers:
                        rating_data['review_count'] = numbers[0]
                        break
            
            return rating_data
            
        except Exception as e:
            print(f"Reliance: Rating extraction error: {e}")
            return rating_data

    def close(self):
        if self.driver:
            self.driver.quit()

# --- Amazon Bot Class (Enhanced with Robust Popup Handling) ---

class AmazonScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--window-position=-3000,0")  # Hide window
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            print(f"Amazon: Failed to start browser: {e}")
            raise
    
    def human_type(self, element, text):
        """Type like a human with random delays"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # Random delays
    
    def handle_amazon_popups(self):
        """Handle various Amazon popups including location selection"""
        try:
            # Try multiple popup close selectors
            popup_selectors = [
                ".a-button-close", 
                ".a-icon-close",
                "#glow-ingress-block .a-button-primary",
                ".a-button[aria-label='Close']",
                "#nav-main .a-button-close",
                "#a-autoid-0-announce",  # Location continue button
                ".a-popover-footer .a-button-primary",  # Location footer button
            ]
            
            for selector in popup_selectors:
                try:
                    close_btn = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    close_btn.click()
                    print(f"Amazon: Closed popup with selector: {selector}")
                    time.sleep(1)
                    break
                except:
                    continue
            
            # Special handling for location selection popup
            try:
                # Look for location-related elements
                location_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    "[data-action-type='SELECT_LOCATION'], .a-button[href*='location']")
                if location_buttons:
                    location_buttons[0].click()
                    print("Amazon: Clicked location selection")
                    time.sleep(2)
            except:
                pass
                
            # Handle the "Deliver to" location popup
            try:
                location_continue = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 
                        "#a-autoid-0-announce, [data-action-type='DISMISS']"))
                )
                location_continue.click()
                print("Amazon: Handled location continue button")
                time.sleep(1)
            except:
                pass
                
            # Try using Escape key as fallback
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ESCAPE)
                time.sleep(1)
                body.send_keys(Keys.ESCAPE)  # Press twice for safety
                print("Amazon: Pressed ESC to close popups")
            except:
                pass
                
        except Exception as e:
            print(f"Amazon: Popup handling failed: {e}")
    
    def search_product(self, product_name):
        try:
            # Use direct search URL to avoid popups
            search_url = f"https://www.amazon.in/s?k={product_name.replace(' ', '+')}"
            self.driver.get(search_url)
            time.sleep(5)
            
            # Handle any popups that might still appear
            self.handle_amazon_popups()
            
            # Wait for results
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 
                    "[data-component-type='s-search-result'], .s-result-item"))
            )
            
            # Additional wait for content to load
            time.sleep(3)
            
            product_data = self.extract_product_data()
            return product_data
            
        except Exception as e:
            print(f"Amazon: Search failed: {e}")
            # Take screenshot for debugging
            try:
                self.driver.save_screenshot("amazon_error.png")
                print("Screenshot saved as amazon_error.png")
            except:
                pass
            return None
    
    def extract_product_data(self):
        try:
            product = {}
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Try multiple selectors for product container
            product_container = None
            selectors = [
                '[data-component-type="s-search-result"]',
                '.s-result-item[data-component-type="s-search-result"]',
                '.s-main-slot [data-component-type="s-search-result"]'
            ]
            
            for selector in selectors:
                containers = soup.select(selector)
                for container in containers:
                    # Skip sponsored ads and non-product items
                    container_text = container.get_text()
                    if len(container_text) > 100 and 'sponsored' not in container_text.lower():
                        product_container = container
                        break
                if product_container:
                    break
            
            if not product_container:
                print("Amazon: No valid product container found")
                return None
            
            # Extract product name and brand
            title_elem = product_container.select_one('h2 a span')
            if title_elem:
                product['product_name'] = title_elem.get_text(strip=True)
                if product['product_name']:
                    # Enhanced brand extraction
                    title_lower = product['product_name'].lower()
                    brands = {
                        'Apple': ['iphone', 'ipad', 'macbook', 'apple', 'mac', 'watch'],
                        'Samsung': ['samsung', 'galaxy'],
                        'OnePlus': ['oneplus'],
                        'Xiaomi': ['xiaomi', 'mi ', 'redmi', 'poco'],
                        'Realme': ['realme'],
                        'Oppo': ['oppo'],
                        'Vivo': ['vivo'],
                        'HP': ['hp ', 'hp[^a-z]', 'victus', 'pavilion'],
                        'Dell': ['dell', 'inspiron', 'xps'],
                        'Lenovo': ['lenovo', 'thinkpad', 'ideapad'],
                        'Asus': ['asus', 'rog', 'tuf'],
                        'Acer': ['acer', 'aspire', 'predator'],
                        'MSI': ['msi'],
                        'Google': ['google', 'pixel']
                    }
                    
                    brand_found = False
                    for brand, keywords in brands.items():
                        for keyword in keywords:
                            if keyword in title_lower:
                                product['brand'] = brand
                                brand_found = True
                                break
                        if brand_found:
                            break
                    
                    if not brand_found:
                        first_word = product['product_name'].split()[0]
                        product['brand'] = first_word if first_word and len(first_word) > 2 else "unknown"
            
            # Extract current price - try multiple selectors
            price_selectors = [
                '.a-price-whole',
                '.a-price .a-offscreen',
                '.a-price[data-a-size="xl"] .a-offscreen',
                '.a-text-price .a-offscreen'
            ]
            
            for selector in price_selectors:
                price_elem = product_container.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    numbers = re.findall(r'[\d,]+', price_text)
                    if numbers:
                        product['price'] = numbers[0].replace(',', '')
                        break
            
            # Extract original price for discount calculation
            original_selectors = [
                '.a-price.a-text-price .a-offscreen',
                '.a-text-price[data-a-strike="true"] .a-offscreen'
            ]
            
            for selector in original_selectors:
                original_elem = product_container.select_one(selector)
                if original_elem:
                    original_text = original_elem.get_text(strip=True)
                    numbers = re.findall(r'[\d,]+', original_text)
                    if numbers:
                        product['original_price'] = numbers[0].replace(',', '')
                        break
            
            # Calculate discount if we have both prices
            if 'original_price' in product and 'price' in product:
                try:
                    original = float(product['original_price'])
                    current = float(product['price'])
                    if original > current:
                        discount = ((original - current) / original) * 100
                        product['discount_percentage'] = f"{discount:.0f}"
                    else:
                        product['discount_percentage'] = "0"
                except:
                    product['discount_percentage'] = "0"
            else:
                product['discount_percentage'] = "0"
            
            # Extract rating with better selectors
            rating_selectors = [
                '.a-icon-alt',
                '.a-row.a-size-small .a-icon-alt',
                '[aria-label*="out of 5 stars"]'
            ]
            
            for selector in rating_selectors:
                rating_elem = product_container.select_one(selector)
                if rating_elem:
                    rating_text = rating_elem.get_text(strip=True)
                    rating_match = re.search(r'(\d\.\d)', rating_text)
                    if rating_match:
                        product['rating'] = rating_match.group(1)
                        break
                else:
                    product['rating'] = "0"
            
            # Extract review count with better selectors
            review_selectors = [
                '.a-size-base.s-underline-text',
                '.a-row.a-size-small .a-size-base',
                '[aria-label*="ratings"]',
                '.a-link-normal .a-size-base'
            ]
            
            for selector in review_selectors:
                review_elem = product_container.select_one(selector)
                if review_elem:
                    review_text = review_elem.get_text(strip=True)
                    numbers = re.findall(r'[\d,]+', review_text)
                    if numbers:
                        product['review_count'] = numbers[0].replace(',', '')
                        break
                else:
                    product['review_count'] = "0"
            
            # If we don't have essential data, return None
            if 'price' not in product or product.get('price', '0') == '0':
                print("Amazon: No valid price found")
                return None
                
            return product
            
        except Exception as e:
            print(f"Amazon: Extraction failed: {e}")
            return None
    
    def close(self):
        if self.driver:
            self.driver.quit()

# ===================================================================
# --- MAIN FUNCTIONS (Updated with Amazon) ---
# ===================================================================

def _clean_data(data_dict, source):
    """
    Takes a scraped data dictionary and cleans it into the
    final format required by the AI model.
    """
    try:
        # 1. Clean Price
        price_str = str(data_dict.get('price', '0')).replace(',', '')
        price = float(re.sub(r'[^\d.]', '', price_str))
        if price == 0: return None  # Useless if no price

        # 2. Clean Discount
        discount_str = str(data_dict.get('discount_percentage', '0')).replace('%', '')
        discount = float(re.sub(r'[^\d.]', '', discount_str))

        # 3. Clean Rating
        rating_str = str(data_dict.get('rating', '0'))
        rating = float(re.sub(r'[^\d.]', '', rating_str))

        # 4. Clean Review Count
        review_str = str(data_dict.get('review_count', '0')).replace(',', '')
        review_count = int(re.sub(r'[^\d]', '', review_str))
        
        # 5. Get Brand
        brand = str(data_dict.get('brand', 'unknown'))

        return {
            "source": source,
            "brand": brand,
            "price": price,
            "discount_percentage": discount,
            "rating": rating,
            "review_count": review_count
        }
    except Exception as e:
        print(f"Failed to clean data from {source}: {e}")
        return None

def scrape_croma_data(product_name):
    """
    High-level function to scrape and clean Croma data.
    """
    scraper = None
    try:
        print(f"Starting Croma scrape for: {product_name}")
        scraper = CromaScraper()
        raw_data = scraper.search_product(product_name)
        scraper.close()
        
        if not raw_data:
            print("Croma: No raw data found.")
            return None
        
        print("Croma: Raw data found, cleaning...")
        clean_data = _clean_data(raw_data, "Croma")
        return clean_data
        
    except Exception as e:
        print(f"Croma: Main function failed: {e}")
        if scraper:
            scraper.close()
        return None

def scrape_reliance_data(product_name):
    """
    High-level function to scrape and clean Reliance data.
    """
    scraper = None
    try:
        print(f"Starting Reliance scrape for: {product_name}")
        scraper = RelianceDigitalScraper()
        raw_data = scraper.search_product(product_name)
        scraper.close()
        
        if not raw_data:
            print("Reliance: No raw data found.")
            return None
            
        print("Reliance: Raw data found, cleaning...")
        clean_data = _clean_data(raw_data, "Reliance")
        
        # Additional validation
        if clean_data and clean_data.get('price', 0) < 1000:
            print(f"Reliance: Suspicious price {clean_data['price']}, likely wrong product")
            return None
            
        return clean_data
        
    except Exception as e:
        print(f"Reliance: Main function failed: {e}")
        if scraper:
            scraper.close()
        return None

def scrape_amazon_data(product_name):
    """
    High-level function to scrape and clean Amazon data.
    """
    scraper = None
    try:
        print(f"Starting Amazon scrape for: {product_name}")
        scraper = AmazonScraper()
        raw_data = scraper.search_product(product_name)
        scraper.close()
        
        if not raw_data:
            print("Amazon: No raw data found.")
            return None
            
        print("Amazon: Raw data found, cleaning...")
        clean_data = _clean_data(raw_data, "Amazon")
        return clean_data
        
    except Exception as e:
        print(f"Amazon: Main function failed: {e}")
        if scraper:
            scraper.close()
        return None


# ===================================================================
# --- TEST SCRIPT ---
# ===================================================================

def test_amazon():
    """Quick test script for Amazon scraper"""
    scraper = AmazonScraper()
    try:
        result = scraper.search_product("samsung s25 ultra")
        print("Amazon result:", result)
    except Exception as e:
        print("Error:", e)
    finally:
        scraper.close()

if __name__ == "__main__":
    test_amazon()
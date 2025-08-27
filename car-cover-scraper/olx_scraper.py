import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import logging
import random
import os
from config import *

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OLXScraper:
    def __init__(self):
        self.base_url = "https://www.olx.in/items/q-car-cover"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def fetch_page(self, url):
        """Fetch webpage with error handling and retries"""
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"Fetching: {url} (Attempt {attempt + 1})")
                
                # Add random delay to mimic human behavior
                time.sleep(random.uniform(2, 5))
                
                response = self.session.get(url, timeout=TIMEOUT)
                response.raise_for_status()
                
                logger.info(f"Successfully fetched page. Status: {response.status_code}")
                return response
                
            except requests.exceptions.Timeout:
                logger.error(f"Timeout error on attempt {attempt + 1}")
            except requests.exceptions.ConnectionError:
                logger.error(f"Connection error on attempt {attempt + 1}")
            except requests.RequestException as e:
                logger.error(f"Error fetching page: {e}")
                
            if attempt < MAX_RETRIES - 1:
                wait_time = REQUEST_DELAY * (2 ** attempt)
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        return None

    def parse_products(self, soup):
        """Parse product information from the soup object"""
        products = []
        
        # Try different selectors for OLX product listings
        product_selectors = [
            '[data-aut-id="itemBox"]',
            '.EIR5N',
            '._1DNjI',
            '._2Gr10'
        ]
        
        product_elements = []
        for selector in product_selectors:
            product_elements = soup.select(selector)
            if product_elements:
                logger.info(f"Found {len(product_elements)} products using selector: {selector}")
                break
        
        if not product_elements:
            logger.warning("No products found with any selector")
            return products
        
        for element in product_elements:
            try:
                product = self.extract_product_info(element)
                if product:
                    products.append(product)
            except Exception as e:
                logger.error(f"Error parsing product: {e}")
                continue
        
        return products

    def extract_product_info(self, element):
        """Extract individual product information"""
        product = {}
        
        try:
            # Title
            title_selectors = ['[data-aut-id="itemTitle"]', '.H8i_3', '._2tW1I']
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    product['title'] = title_elem.get_text(strip=True)
                    break
            
            # Price
            price_selectors = ['[data-aut-id="itemPrice"]', '._2Ks63', '.notranslate']
            for selector in price_selectors:
                price_elem = element.select_one(selector)
                if price_elem:
                    product['price'] = price_elem.get_text(strip=True)
                    break
            
            # Location
            location_selectors = ['[data-aut-id="item-location"]', '.tjgMm', '._1oajQ']
            for selector in location_selectors:
                location_elem = element.select_one(selector)
                if location_elem:
                    product['location'] = location_elem.get_text(strip=True)
                    break
            
            # Image URL
            img_elem = element.select_one('img')
            if img_elem:
                product['image_url'] = img_elem.get('src', '')
            
            # Product URL
            link_elem = element.select_one('a')
            if link_elem:
                href = link_elem.get('href', '')
                if href.startswith('/'):
                    product['url'] = f"https://www.olx.in{href}"
                else:
                    product['url'] = href
            
            # Only return product if it has at least title
            if 'title' in product:
                return product
            
        except Exception as e:
            logger.error(f"Error extracting product info: {e}")
            
        return None

    def scrape(self):
        """Main scraping function"""
        try:
            logger.info("Starting OLX car cover scraping...")
            
            response = self.fetch_page(self.base_url)
            if not response:
                raise Exception("Failed to fetch the main page")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = self.parse_products(soup)
            
            if not products:
                logger.warning("No products were scraped")
                return []
            
            logger.info(f"Successfully scraped {len(products)} products")
            
            # Save results
            self.save_results(products)
            
            return products
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise

    def save_results(self, products):
        """Save results to JSON file"""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
            
            # Prepare data with metadata
            data = {
                'timestamp': datetime.now().isoformat(),
                'total_products': len(products),
                'source': 'OLX India',
                'search_query': 'car cover',
                'products': products
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            raise

def main():
    try:
        scraper = OLXScraper()
        products = scraper.scrape()
        
        if products:
            print(f"✅ Successfully scraped {len(products)} car cover listings!")
            print(f"Results saved to {os.path.join(OUTPUT_DIR, OUTPUT_FILE)}")
        else:
            print("⚠️ No products found. OLX might be blocking requests.")
            
    except Exception as e:
        print(f"✗ Scraping failed. Check logs for details.")
        logger.error(f"Main execution failed: {e}")

if __name__ == "__main__":
    main()
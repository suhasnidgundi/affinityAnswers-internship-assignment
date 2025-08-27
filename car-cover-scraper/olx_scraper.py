import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import logging
from config import *

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OLXScraper:
    def __init__(self):
        self.base_url = "https://www.olx.in/items/q-car-cover"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def fetch_page(self, url):
        """Fetch webpage with error handling and retries"""
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"Fetching: {url} (Attempt {attempt + 1})")
                response = self.session.get(url, timeout=TIMEOUT)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logger.error(f"Error fetching page: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(REQUEST_DELAY * (attempt + 1))
                else:
                    raise
        return None

    def parse_product_details(self, soup):
        """Extract product information from OLX page"""
        products = []
        
        try:
            # Find product containers (this selector may need adjustment based on OLX's current structure)
            product_elements = soup.find_all('div', {'data-aut-id': 'itemBox'}) or soup.find_all('div', class_='_1ONnP')
            
            for element in product_elements:
                try:
                    # Extract title
                    title_elem = element.find('span', {'data-aut-id': 'itemTitle'}) or element.find('h2')
                    title = title_elem.get_text(strip=True) if title_elem else "N/A"
                    
                    # Extract price
                    price_elem = element.find('span', {'data-aut-id': 'itemPrice'}) or element.find('span', class_='_89yzn')
                    price = price_elem.get_text(strip=True) if price_elem else "N/A"
                    
                    # Extract location
                    location_elem = element.find('span', {'data-aut-id': 'item-location'})
                    location = location_elem.get_text(strip=True) if location_elem else "N/A"
                    
                    # Extract URL
                    link_elem = element.find('a', href=True)
                    url = "https://www.olx.in" + link_elem['href'] if link_elem else "N/A"
                    
                    # Extract image URL
                    img_elem = element.find('img')
                    image_url = img_elem.get('src') or img_elem.get('data-src') if img_elem else "N/A"
                    
                    # Extract posted date
                    date_elem = element.find('span', string=lambda text: text and ('day' in text.lower() or 'hour' in text.lower() or 'today' in text.lower()))
                    posted_date = date_elem.get_text(strip=True) if date_elem else "N/A"
                    
                    if title != "N/A":  # Only add if we have at least a title
                        products.append({
                            'title': title,
                            'price': price,
                            'location': location,
                            'url': url,
                            'image_url': image_url,
                            'posted_date': posted_date
                        })
                        
                except Exception as e:
                    logger.warning(f"Error parsing individual product: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing products: {e}")
            
        return products

    def scrape_car_covers(self):
        """Main scraping function"""
        logger.info("Starting OLX car cover scraping...")
        
        try:
            response = self.fetch_page(self.base_url)
            if not response:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            products = self.parse_product_details(soup)
            
            # Prepare final results
            results = {
                'search_query': 'car cover',
                'timestamp': datetime.now().isoformat(),
                'source_url': self.base_url,
                'total_results': len(products),
                'products': products
            }
            
            logger.info(f"Successfully scraped {len(products)} products")
            return results
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return None

    def save_results(self, results, filename='results/car_covers_results.json'):
        """Save results to JSON file"""
        try:
            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")

def main():
    scraper = OLXScraper()
    results = scraper.scrape_car_covers()
    
    if results:
        scraper.save_results(results)
        print(f"✅ Scraping completed! Found {results['total_results']} car cover listings")
        print("📄 Results saved to: results/car_covers_results.json")
    else:
        print("❌ Scraping failed. Check logs for details.")

if __name__ == "__main__":
    main()
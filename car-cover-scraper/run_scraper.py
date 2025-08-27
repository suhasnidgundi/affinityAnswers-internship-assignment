import logging
from olx_scraper import OLXScraper
import importlib.util

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def try_requests_first():
    """Try the requests-based scraper first"""
    try:
        logger.info("Attempting scraping with requests...")
        scraper = OLXScraper()
        products = scraper.scrape()
        
        if products and len(products) > 0:
            logger.info(f"✅ Requests scraper successful! Found {len(products)} products")
            return products, True
        else:
            logger.warning("Requests scraper returned no products")
            return [], False
            
    except Exception as e:
        logger.error(f"Requests scraper failed: {e}")
        return [], False

def try_selenium_fallback():
    """Fallback to Selenium if requests fails"""
    try:
        # Check if selenium is available
        selenium_spec = importlib.util.find_spec("selenium")
        if selenium_spec is None:
            logger.error("Selenium not installed. Install with: pip install selenium")
            return [], False
            
        logger.info("Attempting scraping with Selenium...")
        from selenium_scraper import SeleniumOLXScraper
        
        scraper = SeleniumOLXScraper()
        products = scraper.scrape()
        
        if products and len(products) > 0:
            logger.info(f"✅ Selenium scraper successful! Found {len(products)} products")
            return products, True
        else:
            logger.warning("Selenium scraper returned no products")
            return [], False
            
    except Exception as e:
        logger.error(f"Selenium scraper failed: {e}")
        return [], False

def main():
    # Try requests-based scraper first
    products, success = try_requests_first()
    
    if not success:
        logger.info("Falling back to Selenium scraper...")
        products, success = try_selenium_fallback()
    
    if success:
        print(f"🎉 Scraping completed successfully! Found {len(products)} products")
    else:
        print("❌ Both scraping methods failed. OLX might have strong anti-bot protection.")
        print("\nTroubleshooting suggestions:")
        print("1. Try using a VPN")
        print("2. Run the script from a different network")
        print("3. Check if OLX is accessible manually in your browser")

if __name__ == "__main__":
    main()
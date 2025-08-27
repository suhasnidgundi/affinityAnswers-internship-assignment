# Configuration file for OLX scraper

# Request settings
REQUEST_DELAY = 2  # seconds between requests
MAX_RETRIES = 3
TIMEOUT = 30

# Output settings
OUTPUT_DIR = "results"
OUTPUT_FILE = "car_covers_results.json"

# Scraping settings
MAX_PAGES = 3  # Maximum pages to scrape
PRODUCTS_PER_PAGE = 40
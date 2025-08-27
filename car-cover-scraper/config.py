# Configuration file for OLX scraper

# Request settings
REQUEST_DELAY = 5  # Increased delay between requests
MAX_RETRIES = 5    # More retries
TIMEOUT = 60       # Increased timeout

# Output settings
OUTPUT_DIR = "results"
OUTPUT_FILE = "car_covers_results.json"

# Scraping settings
MAX_PAGES = 1      # Start with just 1 page
PRODUCTS_PER_PAGE = 20
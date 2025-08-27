from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

def scrape_with_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Remove headless for debugging: chrome_options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("https://www.olx.in/items/q-car-cover")
        time.sleep(5)  # Wait for page to load
        
        # Extract data here
        products = driver.find_elements(By.CSS_SELECTOR, "[data-aut-id='itemBox']")
        print(f"Found {len(products)} products")
        
    finally:
        driver.quit()
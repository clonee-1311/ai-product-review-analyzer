from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re

# Optional: For BrightData (commented out by default)
# from selenium.webdriver import Remote, ChromeOptions as RemoteChromeOptions
# from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
# from dotenv import load_dotenv
# import os
# load_dotenv()
# SBR_WEBDRIVER = os.getenv("SBR_WEBDRIVER")


def scrape_website(website):
    """
    Main function to scrape a website and return its HTML content
    """
    print(f"Connecting to scrape: {website}")
    
    # Configure Chrome options for better scraping
    options = Options()
    
    # Run in headless mode (no GUI window)
    options.add_argument("--headless=new")
    
    # Anti-detection measures
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Additional arguments for stability
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # Set a realistic user agent
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = None
    try:
        # Initialize the Chrome driver
        driver = webdriver.Chrome(options=options)
        
        # Navigate to the website
        print(f"Navigating to {website}...")
        driver.get(website)
        
        # Wait for page to load
        time.sleep(3)
        
        # Scroll to load dynamic content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(1)
        
        print("Scraping page content...")
        html = driver.page_source
        
        return html
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        return ""
        
    finally:
        if driver:
            driver.quit()


def extract_body_content(html_content):
    """
    Extract the body content from HTML
    """
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""


def clean_body_content(body_content):
    """
    Clean the body content by removing scripts, styles, and extra whitespace
    """
    if not body_content:
        return ""
    
    soup = BeautifulSoup(body_content, "html.parser")

    # Remove script and style elements
    for script_or_style in soup(["script", "style", "meta", "link", "noscript"]):
        script_or_style.extract()

    # Get text with proper line breaks
    cleaned_content = soup.get_text(separator="\n")
    
    # Remove extra whitespace and empty lines
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() 
        if line.strip() and not line.strip().isspace()
    )

    return cleaned_content


def split_dom_content(dom_content, max_length=6000):
    """
    Split DOM content into chunks of specified maximum length
    """
    if not dom_content:
        return []
    
    return [
        dom_content[i : i + max_length] 
        for i in range(0, len(dom_content), max_length)
    ]


def extract_reviews_from_dom(dom_content):
    """
    Extract reviews with metadata from DOM content
    """
    if not dom_content:
        return []
    
    reviews = []
    lines = dom_content.split('\n')
    
    # Patterns for review extraction
    rating_patterns = [
        r'(\d+\.?\d*)\s*out of\s*5',
        r'(\d+\.?\d*)\s*stars?',
        r'rating[:\s]*(\d+\.?\d*)',
    ]
    
    date_patterns = [
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}',
        r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
        r'\d{4}-\d{2}-\d{2}',
    ]
    
    current_review = {}
    review_text_lines = []
    collecting_review = False
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Skip empty lines
        if not line_lower:
            if collecting_review and review_text_lines:
                # Empty line might indicate end of review
                if len(' '.join(review_text_lines)) > 30:
                    current_review['text'] = ' '.join(review_text_lines)
                    reviews.append(current_review.copy())
                current_review = {}
                review_text_lines = []
                collecting_review = False
            continue
        
        # Check for review markers
        review_markers = ['verified purchase', 'helpful', 'report', 'review', 'comment']
        if any(marker in line_lower for marker in review_markers):
            collecting_review = True
            
        # Extract rating
        if not current_review.get('rating'):
            for pattern in rating_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    try:
                        rating = float(match.group(1))
                        current_review['rating'] = f"{rating}/5"
                        break
                    except:
                        pass
        
        # Extract date
        if not current_review.get('date'):
            for pattern in date_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    current_review['date'] = match.group(0)
                    break
        
        # Extract author (simple heuristic)
        if not current_review.get('author'):
            if 'by ' in line_lower and len(line) < 100:
                parts = line.split('by ')
                if len(parts) > 1:
                    current_review['author'] = parts[-1].strip()
        
        # Collect review text
        if collecting_review:
            # Skip lines that are likely UI elements
            skip_patterns = ['cookie', 'javascript', 'browser', 'subscribe', 'newsletter']
            if not any(pattern in line_lower for pattern in skip_patterns):
                if len(line) > 15:
                    review_text_lines.append(line.strip())
    
    # Add any remaining review
    if review_text_lines and len(' '.join(review_text_lines)) > 30:
        current_review['text'] = ' '.join(review_text_lines)
        if not current_review.get('rating'):
            current_review['rating'] = 'N/A'
        if not current_review.get('date'):
            from datetime import datetime
            current_review['date'] = datetime.now().strftime('%B %d, %Y')
        if not current_review.get('author'):
            current_review['author'] = 'Anonymous'
        reviews.append(current_review)
    
    # If no reviews found with pattern matching, use fallback method
    if not reviews:
        print("No structured reviews found. Using fallback extraction...")
        paragraphs = [line.strip() for line in lines if len(line.strip()) > 100]
        
        for i, para in enumerate(paragraphs[:20]):  # Limit to 20
            reviews.append({
                'text': para,
                'rating': 'N/A',
                'date': 'N/A',
                'author': 'Anonymous',
            })
    
    print(f"Extracted {len(reviews)} reviews")
    return reviews


# Optional: BrightData version (uncomment if needed)
"""
def scrape_website_brightdata(website):
    '''
    Alternative scraping function using BrightData
    '''
    print("Connecting to Scraping Browser...")
    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, "goog", "chrome")
    with Remote(sbr_connection, options=RemoteChromeOptions()) as driver:
        driver.get(website)
        print("Waiting captcha to solve...")
        solve_res = driver.execute(
            "executeCdpCommand",
            {
                "cmd": "Captcha.waitForSolve",
                "params": {"detectTimeout": 10000},
            },
        )
        print("Captcha solve status:", solve_res["value"]["status"])
        print("Navigated! Scraping page content...")
        html = driver.page_source
        return html
"""
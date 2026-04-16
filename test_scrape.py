# test_scrape.py
from scrape import scrape_website, extract_body_content, clean_body_content, split_dom_content

# Test the import
print("✅ All functions imported successfully!")

# Test with a simple URL
url = "https://example.com"
html = scrape_website(url)
if html:
    print(f"✅ Scraping works! Got {len(html)} characters")
else:
    print("❌ Scraping failed")
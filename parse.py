from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import re
import json
from datetime import datetime
import time

# Template for review analysis
template = """
You are a product review analyzer. Analyze the following review text and provide the requested output.

Review Text: {dom_content}

Task: {parse_description}

Important Instructions:
1. Be concise and accurate
2. For sentiment analysis: Return ONLY "POSITIVE", "NEGATIVE", or "NEUTRAL"
3. For summarization: Return a single sentence summary
4. Do not include any explanations or additional text
5. If the review is unclear, return "NEUTRAL" for sentiment or "Unable to summarize" for summary

Your Response:
"""

model = OllamaLLM(model="llama3", temperature=0.3, max_tokens=150)

def parse_with_ollama(dom_chunks, parse_description):
    """Generic parse function for any content"""
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    
    parsed_results = []
    
    for i, chunk in enumerate(dom_chunks, start=1):
        try:
            response = chain.invoke(
                {"dom_content": chunk, "parse_description": parse_description}
            )
            print(f"Parsed batch: {i} of {len(dom_chunks)}")
            parsed_results.append(response)
            time.sleep(0.1)  # Rate limiting
        except Exception as e:
            print(f"Error parsing batch {i}: {str(e)}")
            parsed_results.append("Error processing")
    
    return "\n".join(parsed_results)

def parse_reviews_with_ollama(review_chunks, task_description):
    """Specific function for review analysis with better error handling"""
    try:
        return parse_with_ollama(review_chunks, task_description)
    except Exception as e:
        print(f"Error in review parsing: {str(e)}")
        return "Error: Analysis failed"

def extract_reviews_from_dom(dom_content):
    """
    Extract reviews, ratings, dates, and authors from DOM content
    """
    reviews = []
    
    # Split content into lines
    lines = dom_content.split('\n')
    
    # Patterns for Amazon-like review structure
    rating_pattern = r'(\d+\.?\d*)\s*out of\s*5\s*stars'
    date_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}'
    
    current_review = {}
    review_text = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Try to identify rating
        rating_match = re.search(rating_pattern, line)
        if rating_match and not current_review.get('rating'):
            current_review['rating'] = f"{rating_match.group(1)}/5"
            
        # Try to identify date
        date_match = re.search(date_pattern, line)
        if date_match and not current_review.get('date'):
            current_review['date'] = date_match.group(0)
            
        # Look for "Verified Purchase" or similar markers
        if 'Verified Purchase' in line:
            # This often precedes the review text
            continue
            
        # Collect review text
        if len(line) > 50 and not any(marker in line.lower() for marker in ['stars', 'reviews', 'answered']):
            review_text.append(line)
            
        # Check if we've reached the end of a review
        if ('people found this helpful' in line.lower() or 
            'helpful' in line.lower() or 
            'report' in line.lower() or
            len(' '.join(review_text)) > 500):  # Max review length
            
            if review_text:
                current_review['text'] = ' '.join(review_text)
                current_review['author'] = current_review.get('author', 'Anonymous')
                
                # Only add if we have actual review text
                if len(current_review.get('text', '')) > 20:
                    reviews.append(current_review.copy())
                
                # Reset for next review
                current_review = {}
                review_text = []
    
    # Add any remaining review
    if review_text and len(' '.join(review_text)) > 20:
        current_review['text'] = ' '.join(review_text)
        current_review['author'] = current_review.get('author', 'Anonymous')
        reviews.append(current_review)
    
    # If no reviews found with the pattern matching, try a simpler approach
    if not reviews:
        # Just split by common separators and look for substantial text blocks
        potential_reviews = []
        for line in lines:
            if len(line) > 100 and not any(x in line.lower() for x in ['cookie', 'javascript', 'browser']):
                potential_reviews.append({
                    'text': line,
                    'rating': 'N/A',
                    'date': datetime.now().strftime('%B %d, %Y'),
                    'author': 'Anonymous'
                })
        reviews = potential_reviews[:20]  # Limit to 20 reviews
    
    return reviews
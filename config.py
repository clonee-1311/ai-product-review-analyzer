# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# API Settings
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "150"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))

# Scraping Settings
MAX_REVIEWS = int(os.getenv("MAX_REVIEWS", "50"))
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.5"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# File Export Settings
EXPORT_FORMAT = os.getenv("EXPORT_FORMAT", "csv")  # csv, json, excel
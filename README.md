# 🤖 AI Product Review Analyzer

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B.svg)](https://streamlit.io/)
[![Ollama](https://img.shields.io/badge/Ollama-Llama3-000000.svg)](https://ollama.ai/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A powerful web scraping and AI-powered analysis tool that extracts product reviews from e-commerce websites and performs intelligent sentiment analysis and summarization using local Large Language Models (LLMs).

<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/c44656b8-7639-4f54-8865-117c30988e18" />
<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/834ef7ec-5391-4e59-a68f-5fd7bec135cc" />
<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/07e5f356-cc19-476a-9fa9-169f4798d062" />
<img width="1500" height="1000" alt="image" src="https://github.com/user-attachments/assets/42c406b5-8378-49f7-893f-cb802c99f2cd" />





### Main Interface
![Main Interface](screenshots/main.png)

### Analysis Results
![Analysis Results](screenshots/results.png)

## ✨ Features

- **🌐 Intelligent Web Scraping**: Extracts product reviews from Amazon, Best Buy, and similar e-commerce platforms
- **🤖 AI-Powered Analysis**: Uses Ollama (Llama 3) for:
  - Sentiment Analysis (Positive/Negative/Neutral)
  - Review Summarization
  - Combined analysis (Both sentiment + summary)
- **📊 Structured Data Export**: Download results in CSV or JSON formats
- **🛡️ Anti-Detection Measures**: Built-in browser fingerprinting evasion
- **⚡ Real-time Processing**: Progress tracking and live status updates
- **📈 Statistical Overview**: Visual metrics for rating averages and sentiment distribution
- **🔍 Raw Data Inspection**: View scraped DOM content for debugging

## 🛠️ Tech Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| **Frontend** | Streamlit | Interactive web interface |
| **Web Scraping** | Selenium WebDriver | Dynamic content extraction |
| | BeautifulSoup4 | HTML parsing and cleaning |
| **AI/ML** | Ollama | Local LLM inference |
| | LangChain | LLM orchestration framework |
| | Llama 3 (8B) | Text analysis model |
| **Data Processing** | Pandas | Data manipulation and analysis |
| | NumPy | Numerical computations |
| **Utilities** | python-dotenv | Environment configuration |
| | Requests | HTTP client |

## 📋 Prerequisites

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Google Chrome Browser** ([Download](https://www.google.com/chrome/))
- **Ollama** ([Download](https://ollama.ai/download))
- **8GB+ RAM** (16GB recommended for Llama 3)
- **10GB+ Free Disk Space** (for model storage)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-product-review-analyzer.git
cd ai-product-review-analyzer```
create virtual enviornment
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

install dependency
pip install -r requirements.txt

install configure ollama
# Download and install Ollama from https://ollama.ai/download

# Pull the Llama 3 model (3.8GB download)
ollama pull llama3

# Verify installation
ollama list
📁 Project Structure
ai-product-review-analyzer/
├── main.py                 # Streamlit web application
├── scrape.py               # Web scraping logic with Selenium
├── parse.py                # AI analysis using Ollama/LangChain
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── README.md               # Project documentation
└── screenshots/            # Application screenshots
    ├── main.png
    └── results.png

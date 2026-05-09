import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# App settings
APP_NAME = "stock_market_analyser"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Stock settings
DEFAULT_CURRENCY = "INR"
DEFAULT_MARKET = "NSE"
POPULAR_INDIAN_STOCKS = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "WIPRO.NS",
    "ADANIENT.NS",
    "BAJFINANCE.NS",
    "SBIN.NS",
]

# Data settings
DEFAULT_PERIOD = "1mo"   # how much historical data to fetch by default
DEFAULT_INTERVAL = "1d"  # daily data


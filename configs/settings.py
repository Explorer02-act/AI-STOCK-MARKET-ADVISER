import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# News API
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

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

# Advanced environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://stock_user:stock_password@localhost:5432/stock_market",
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))

# Streaming settings
STREAM_INTERVAL_SECONDS = int(os.getenv("STREAM_INTERVAL_SECONDS", "15"))

# Monitoring and cost controls
RATE_LIMIT_WARNING_THRESHOLD = int(os.getenv("RATE_LIMIT_WARNING_THRESHOLD", "90"))
DAILY_COST_LIMIT_USD = float(os.getenv("DAILY_COST_LIMIT_USD", "5.00"))
GROQ_INPUT_COST_PER_1K = float(os.getenv("GROQ_INPUT_COST_PER_1K", "0.00005"))
GROQ_OUTPUT_COST_PER_1K = float(os.getenv("GROQ_OUTPUT_COST_PER_1K", "0.00008"))


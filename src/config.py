"""
Configuration settings for IPO Base Breakout Strategy
Using free data sources: Yahoo Finance and Alpha Vantage
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Data Source Configuration
    DATA_SOURCE = "yfinance"  # Options: "yfinance", "alphavantage"
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")  # Optional
    
    # Strategy Parameters
    MIN_BASE_DAYS = 5           # Minimum days for base formation
    MAX_BASE_DAYS = 60          # Maximum days for base formation
    VOLUME_DRY_THRESHOLD = 0.5  # Volume should be 50% below average during base
    BREAKOUT_VOLUME_MULTIPLIER = 1.5  # Breakout volume should be 1.5x average
    
    # Stop Loss and Targets
    TRAILING_STOP_PERCENT = 8   # 8% trailing stop loss
    INITIAL_STOP_PERCENT = 10   # 10% initial stop loss
    TARGET_1_PERCENT = 15       # First target at 15%
    TARGET_2_PERCENT = 25       # Second target at 25%
    BREAKEVEN_AFTER_T1 = True   # Move stop to breakeven after hitting Target 1
    
    # Data Parameters
    LOOKBACK_DAYS = 500         # Days to look back for data
    MIN_LISTING_DAYS = 10       # Minimum days after listing
    
    # Backtest Parameters
    START_DATE = "2014-01-01"
    END_DATE = None  # None for current date
    
    # Scanner Parameters
    SCAN_DAYS = 100             # Days to scan for recent IPOs
    MIN_MARKET_CAP = 100        # Minimum market cap in crores (₹100 Cr)
    
    # Database Files
    DATA_DIR = "data"
    RESULTS_DIR = "results"
    IPO_LIST_FILE = "data/ipo_list.csv"
    
    # Notification Settings (Optional)
    ENABLE_TELEGRAM = False
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # Rate Limiting
    RATE_LIMIT_DELAY = 2  # Seconds between API calls
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories"""
        Path(cls.DATA_DIR).mkdir(exist_ok=True)
        Path(cls.RESULTS_DIR).mkdir(exist_ok=True)

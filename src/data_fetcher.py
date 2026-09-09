"""
Data fetching module using free data sources
Primary: Yahoo Finance (yfinance)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

class DataFetcher:
    def __init__(self, config):
        self.config = config
        self.rate_limit_delay = config.RATE_LIMIT_DELAY if hasattr(config, 'RATE_LIMIT_DELAY') else 2
        
    def fetch_stock_data(self, symbol, start_date=None, end_date=None):
        """
        Fetch historical data for a stock using Yahoo Finance
        """
        try:
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=self.config.LOOKBACK_DAYS)).strftime('%Y-%m-%d')
            
            # Fetch from Yahoo Finance
            df = self._fetch_from_yfinance(symbol, start_date, end_date)
            
            if df is not None and not df.empty:
                df['Symbol'] = symbol
                return df
                
            return None
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def _fetch_from_yfinance(self, symbol, start_date, end_date):
        """Fetch data from Yahoo Finance"""
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(start=start_date, end=end_date)
            
            if df.empty:
                return None
                
            df = df.reset_index()
            
            # Standardize column names
            if 'Date' not in df.columns:
                df = df.rename(columns={'index': 'Date'})
            
            # Ensure required columns exist
            required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            for col in required_columns:
                if col not in df.columns:
                    if col == 'Date':
                        df[col] = pd.to_datetime(df.index)
                    else:
                        df[col] = 0
            
            return df[required_columns]
            
        except Exception as e:
            print(f"Yahoo Finance error for {symbol}: {e}")
            return None
    
    def fetch_multiple_stocks(self, symbols, start_date=None, end_date=None):
        """Fetch data for multiple stocks with rate limiting"""
        all_data = {}
        
        for symbol in symbols:
            df = self.fetch_stock_data(symbol, start_date, end_date)
            
            if df is not None:
                all_data[symbol] = df
                print(f"✓ Fetched data for {symbol}")
            else:
                print(f"✗ Failed to fetch data for {symbol}")
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
        
        return all_data

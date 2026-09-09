"""
Data fetching module using free data sources
Primary: Yahoo Finance (yfinance)
Secondary: Alpha Vantage (optional)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import requests
import warnings
warnings.filterwarnings('ignore')

class DataFetcher:
    def __init__(self, config):
        self.config = config
        self.rate_limit_delay = config.RATE_LIMIT_DELAY
        
    def fetch_stock_data(self, symbol, start_date=None, end_date=None):
        """
        Fetch historical data for a stock using Yahoo Finance
        """
        try:
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=self.config.LOOKBACK_DAYS)).strftime('%Y-%m-%d')
            
            # Try Yahoo Finance first
            df = self._fetch_from_yfinance(symbol, start_date, end_date)
            
            # If Yahoo Finance fails and Alpha Vantage key is available, try it
            if df is None and self.config.ALPHA_VANTAGE_API_KEY:
                df = self._fetch_from_alphavantage(symbol, start_date, end_date)
            
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
            df = df.rename(columns={'Date': 'Date', 'Open': 'Open', 'High': 'High', 
                                   'Low': 'Low', 'Close': 'Close', 'Volume': 'Volume'})
            return df
            
        except Exception as e:
            print(f"Yahoo Finance error for {symbol}: {e}")
            return None
    
    def _fetch_from_alphavantage(self, symbol, start_date, end_date):
        """Fetch data from Alpha Vantage (requires API key)"""
        try:
            # Convert symbol format (remove .NS for Alpha Vantage)
            av_symbol = symbol.replace('.NS', '.BSE')
            
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': av_symbol,
                'outputsize': 'full',
                'apikey': self.config.ALPHA_VANTAGE_API_KEY
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'Time Series (Daily)' not in data:
                return None
                
            time_series = data['Time Series (Daily)']
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Rename columns
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            df = df.astype(float)
            df = df.reset_index()
            df = df.rename(columns={'index': 'Date'})
            
            # Filter date range
            df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
            
            return df
            
        except Exception as e:
            print(f"Alpha Vantage error for {symbol}: {e}")
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
    
    def get_stock_info(self, symbol):
        """Get basic stock information"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            return {
                'Symbol': symbol,
                'Company': info.get('longName', symbol),
                'Market_Cap': info.get('marketCap', 0),
                'Sector': info.get('sector', 'Unknown'),
                'Industry': info.get('industry', 'Unknown'),
                'Current_Price': info.get('currentPrice', 0),
                '52_Week_High': info.get('fiftyTwoWeekHigh', 0),
                '52_Week_Low': info.get('fiftyTwoWeekLow', 0),
                'Average_Volume': info.get('averageVolume', 0)
            }
        except:
            return {
                'Symbol': symbol,
                'Company': symbol,
                'Market_Cap': 0,
                'Sector': 'Unknown',
                'Industry': 'Unknown',
                'Current_Price': 0,
                '52_Week_High': 0,
                '52_Week_Low': 0,
                'Average_Volume': 0
            }

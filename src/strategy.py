"""
IPO Base Breakout Strategy Implementation
Enhanced with better base detection and volume analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class IPOBaseBreakoutStrategy:
    def __init__(self, config):
        self.config = config
        
    def calculate_indicators(self, df):
        """
        Calculate technical indicators for the strategy
        """
        if df is None or len(df) < 20:
            return None
            
        df = df.copy()
        
        # Moving averages
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA10'] = df['Close'].rolling(window=10).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()
        
        # Volume indicators
        df['Volume_MA5'] = df['Volume'].rolling(window=5).mean()
        df['Volume_MA10'] = df['Volume'].rolling(window=10).mean()
        df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
        df['Volume_MA50'] = df['Volume'].rolling(window=50).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA20']
        
        # Price indicators
        df['High_20'] = df['High'].rolling(window=20).max()
        df['Low_20'] = df['Low'].rolling(window=20).min()
        df['High_50'] = df['High'].rolling(window=50).max()
        
        # Volatility (ATR)
        df['TR'] = np.maximum(
            df['High'] - df['Low'],
            np.maximum(
                abs(df['High'] - df['Close'].shift(1)),
                abs(df['Low'] - df['Close'].shift(1))
            )
        )
        df['ATR'] = df['TR'].rolling(window=14).mean()
        df['ATR_Pct'] = (df['ATR'] / df['Close']) * 100
        
        # IPO Day High (first trading day high)
        df['IPO_Day_High'] = df['High'].iloc[0] if len(df) > 0 else 0
        
        # Price position relative to IPO high
        df['Pct_From_IPO_High'] = ((df['Close'] - df['IPO_Day_High']) / df['IPO_Day_High']) * 100
        
        return df
    
    def identify_base_formation(self, df):
        """
        Identify base formation pattern
        """
        if df is None or len(df) < self.config.MIN_BASE_DAYS:
            return []
        
        bases = []
        
        for i in range(self.config.MIN_LISTING_DAYS, len(df)):
            # Check for potential base formation
            if i + self.config.MIN_BASE_DAYS > len(df):
                break
                
            # Look for consolidation pattern
            base_candidates = self._check_base_pattern(df, i)
            
            if base_candidates:
                bases.extend(base_candidates)
        
        return bases
    
    def _check_base_pattern(self, df, end_idx):
        """
        Check if there's a valid base formation ending at end_idx
        """
        bases = []
        
        for base_days in range(self.config.MIN_BASE_DAYS, self.config.MAX_BASE_DAYS + 1):
            start_idx = end_idx - base_days
            
            if start_idx < self.config.MIN_LISTING_DAYS:
                continue
                
            # Get base period data
            base_highs = df['High'].iloc[start_idx:end_idx]
            base_lows = df['Low'].iloc[start_idx:end_idx]
            base_volumes = df['Volume'].iloc[start_idx:end_idx]
            base_closes = df['Close'].iloc[start_idx:end_idx]
            
            # Calculate base metrics
            base_high = base_highs.max()
            base_low = base_lows.min()
            base_range = base_high - base_low
            base_range_pct = (base_range / base_high) * 100 if base_high > 0 else 0
            
            # Check if base is tight (less than 20% range)
            if base_range_pct > 20:
                continue
                
            # Check volume drying during base
            avg_volume = df['Volume'].iloc[:start_idx].mean()
            base_avg_volume = base_volumes.mean()
            volume_dry_ratio = base_avg_volume / avg_volume if avg_volume > 0 else 1
            
            if volume_dry_ratio > self.config.VOLUME_DRY_THRESHOLD:
                continue
                
            # Check if base high is above IPO day high
            if base_high < df['IPO_Day_High'].iloc[end_idx]:
                continue
                
            # Check for breakout at end_idx
            if df['High'].iloc[end_idx] > base_high:
                # Volume on breakout should be high
                volume_ma20 = df['Volume_MA20'].iloc[end_idx]
                volume_breakout_ratio = df['Volume'].iloc[end_idx] / volume_ma20 if volume_ma20 > 0 else 0
                
                if volume_breakout_ratio >= self.config.BREAKOUT_VOLUME_MULTIPLIER:
                    bases.append({
                        'start_idx': start_idx,
                        'end_idx': end_idx,
                        'start_date': df['Date'].iloc[start_idx],
                        'end_date': df['Date'].iloc[end_idx],
                        'breakout_date': df['Date'].iloc[end_idx],
                        'base_high': base_high,
                        'base_low': base_low,
                        'breakout_price': df['High'].iloc[end_idx],
                        'base_days': base_days,
                        'base_range_pct': base_range_pct,
                        'volume_dry_ratio': volume_dry_ratio,
                        'volume_breakout_ratio': volume_breakout_ratio,
                        'avg_volume': volume_ma20,
                        'volume_on_breakout': df['Volume'].iloc[end_idx]
                    })
                    break  # Only take the most recent valid base
                    
        return bases
    
    def generate_signals(self, df):
        """
        Generate trading signals
        """
        if df is None or len(df) < 20:
            return pd.DataFrame()
        
        df = self.calculate_indicators(df)
        
        if df is None:
            return pd.DataFrame()
            
        bases = self.identify_base_formation(df)
        
        signals = []
        
        for base in bases:
            # Calculate entry, stop, and targets
            entry_price = base['breakout_price']
            stop_loss = entry_price * (1 - self.config.INITIAL_STOP_PERCENT / 100)
            target_1 = entry_price * (1 + self.config.TARGET_1_PERCENT / 100)
            target_2 = entry_price * (1 + self.config.TARGET_2_PERCENT / 100)
            
            # Risk-Reward calculation
            risk = entry_price - stop_loss
            reward_1 = target_1 - entry_price
            reward_2 = target_2 - entry_price
            
            rr_ratio_1 = reward_1 / risk if risk > 0 else 0
            rr_ratio_2 = reward_2 / risk if risk > 0 else 0
            
            # Only take trades with good risk-reward (minimum 1.5:1)
            if rr_ratio_1 < 1.5:
                continue
                
            signal = {
                'Symbol': df['Symbol'].iloc[0] if 'Symbol' in df.columns else 'Unknown',
                'Entry_Price': entry_price,
                'Initial_Stop': stop_loss,
                'Target_1': target_1,
                'Target_2': target_2,
                'RR_Ratio_1': rr_ratio_1,
                'RR_Ratio_2': rr_ratio_2,
                'Base_Days': base['base_days'],
                'Base_Range_Pct': base['base_range_pct'],
                'Volume_Dry_Ratio': base['volume_dry_ratio'],
                'Volume_Breakout_Ratio': base['volume_breakout_ratio'],
                'Breakout_Date': base['breakout_date'],
                'Base_High': base['base_high'],
                'Base_Low': base['base_low']
            }
            
            signals.append(signal)
        
        return pd.DataFrame(signals)

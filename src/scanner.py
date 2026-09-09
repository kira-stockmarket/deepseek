"""
Enhanced daily scanner for IPO base breakout opportunities
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

class IPOBaseBreakoutScanner:
    def __init__(self, config, strategy, data_fetcher, ipo_database):
        self.config = config
        self.strategy = strategy
        self.data_fetcher = data_fetcher
        self.ipo_database = ipo_database
        
    def scan_for_opportunities(self):
        """
        Scan for current IPO base breakout opportunities
        """
        print("\n🔍 Scanning for IPO Base Breakout Opportunities...")
        print("="*70)
        
        # Get recent IPO stocks (last 2 years for scanning)
        recent_ipos = self.ipo_database.get_recent_ipos(days=730)
        
        if recent_ipos.empty:
            print("✗ No recent IPOs found in database")
            return []
        
        opportunities = []
        watchlist = []
        
        for idx, row in recent_ipos.iterrows():
            symbol = row['Symbol']
            company = row['Company']
            
            print(f"\n[{idx+1}/{len(recent_ipos)}] Analyzing {symbol} - {company}")
            
            # Fetch recent data
            df = self.data_fetcher.fetch_stock_data(symbol)
            
            if df is None or len(df) < self.config.MIN_BASE_DAYS:
                print(f"  ✗ Insufficient data")
                continue
            
            # Calculate indicators
            df = self.strategy.calculate_indicators(df)
            
            # Check for base formation
            current_price = df['Close'].iloc[-1]
            current_high = df['High'].iloc[-1]
            current_volume = df['Volume'].iloc[-1]
            volume_ma20 = df['Volume_MA20'].iloc[-1]
            
            # Find recent high points (potential base highs)
            recent_high = df['High'].iloc[-20:].max()
            recent_high_idx = df['High'].iloc[-20:].idxmax()
            
            # Check if stock is near its IPO day high
            ipo_high = df['IPO_Day_High'].iloc[-1]
            distance_from_ipo_high = ((ipo_high - current_price) / current_price) * 100
            
            # Check volume pattern
            recent_volume_avg = df['Volume'].iloc[-10:].mean()
            older_volume_avg = df['Volume'].iloc[-30:-10].mean()
            volume_drying = recent_volume_avg < older_volume_avg * self.config.VOLUME_DRY_THRESHOLD
            
            # Check for potential breakout setup
            distance_to_breakout = ((recent_high - current_price) / current_price) * 100
            
            info = {
                'Symbol': symbol,
                'Company': company,
                'Current_Price': round(current_price, 2),
                'IPO_Day_High': round(ipo_high, 2),
                'Recent_High': round(recent_high, 2),
                'Distance_To_Breakout_Pct': round(distance_to_breakout, 2),
                'Distance_From_IPO_High_Pct': round(distance_from_ipo_high, 2),
                'Volume_Today': current_volume,
                'Avg_Volume_20': round(volume_ma20, 2),
                'Volume_Ratio': round(current_volume / volume_ma20, 2) if volume_ma20 > 0 else 0,
                'Volume_Drying': volume_drying,
                'Recent_Volume_Avg': round(recent_volume_avg, 2),
                'Older_Volume_Avg': round(older_volume_avg, 2),
                'Scan_Date': datetime.now().strftime('%Y-%m-%d')
            }
            
            # Check if this is a breakout opportunity
            if (0 < distance_to_breakout < 5 and  # Within 5% of breakout
                volume_drying and  # Volume is drying
                current_price > ipo_high * 0.8):  # Above 80% of IPO high
                
                opportunities.append(info)
                print(f"  🎯 BREAKOUT OPPORTUNITY DETECTED!")
                print(f"     Price: ₹{current_price:.2f}")
                print(f"     Breakout Level: ₹{recent_high:.2f}")
                print(f"     Distance: {distance_to_breakout:.2f}%")
                
            elif volume_drying and distance_from_ipo_high < 20:
                # Add to watchlist
                watchlist.append(info)
                print(f"  👀 Watchlist (Volume drying)")
                
            else:
                print(f"  ✗ No setup found")
        
        # Save results
        results = {
            'opportunities': opportunities,
            'watchlist': watchlist,
            'scan_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if opportunities or watchlist:
            self.save_scan_results(results)
        
        return results
    
    def save_scan_results(self, results):
        """Save scan results to files"""
        import os
        os.makedirs(self.config.RESULTS_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # Save opportunities
        if results['opportunities']:
            df_opp = pd.DataFrame(results['opportunities'])
            opp_file = os.path.join(self.config.RESULTS_DIR, f'opportunities_{timestamp}.csv')
            df_opp.to_csv(opp_file, index=False)
            print(f"\n✓ Opportunities saved to {opp_file}")
        
        # Save watchlist
        if results['watchlist']:
            df_watch = pd.DataFrame(results['watchlist'])
            watch_file = os.path.join(self.config.RESULTS_DIR, f'watchlist_{timestamp}.csv')
            df_watch.to_csv(watch_file, index=False)
            print(f"✓ Watchlist saved to {watch_file}")
        
        # Save complete results as JSON
        json_file = os.path.join(self.config.RESULTS_DIR, f'scan_results_{timestamp}.json')
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📊 Scan Summary:")
        print(f"   Opportunities: {len(results['opportunities'])}")
        print(f"   Watchlist: {len(results['watchlist'])}")

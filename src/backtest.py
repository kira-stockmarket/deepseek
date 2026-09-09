"""
Backtesting engine for IPO Base Breakout Strategy
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class BacktestEngine:
    def __init__(self, config, strategy, data_fetcher, ipo_database):
        self.config = config
        self.strategy = strategy
        self.data_fetcher = data_fetcher
        self.ipo_database = ipo_database
        self.results = []
        
    def run_backtest(self):
        """Run backtest from 2014 to present"""
        ipo_stocks = self.ipo_database.get_all_ipos()
        all_trades = []
        
        print(f"Starting backtest with {len(ipo_stocks)} IPO stocks...")
        
        for idx, row in ipo_stocks.iterrows():
            symbol = row['Symbol']
            company = row.get('Company', symbol)
            
            print(f"\n[{idx+1}/{len(ipo_stocks)}] Backtesting {symbol} - {company}")
            
            try:
                # Fetch data
                df = self.data_fetcher.fetch_stock_data(
                    symbol, 
                    start_date=self.config.START_DATE,
                    end_date=self.config.END_DATE
                )
                
                if df is None or len(df) < 30:
                    print(f"  ✗ Insufficient data")
                    continue
                
                # Generate signals
                signals = self.strategy.generate_signals(df)
                
                if not signals.empty:
                    # Simulate trades
                    trades = self.simulate_trades(df, signals)
                    all_trades.extend(trades)
                    print(f"  ✓ Found {len(trades)} trades")
                else:
                    print(f"  ✗ No signals found")
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue
        
        # Create results dataframe
        if all_trades:
            results_df = pd.DataFrame(all_trades)
            self.calculate_performance_metrics(results_df)
            self.save_results(results_df)
            return results_df
        else:
            print("\n✗ No trades generated during backtest period")
            return pd.DataFrame()
    
    def simulate_trades(self, df, signals):
        """Simulate trades with trailing stop loss and targets"""
        trades = []
        
        for _, signal in signals.iterrows():
            entry_date = signal.get('Breakout_Date', signal.get('breakout_date'))
            entry_price = signal['Entry_Price']
            stop_loss = signal['Initial_Stop']
            target_1 = signal['Target_1']
            target_2 = signal['Target_2']
            
            # Find entry index
            entry_idx = df[df['Date'] == entry_date].index
            if len(entry_idx) == 0:
                continue
            entry_idx = entry_idx[0]
            
            # Simulate trade
            exit_price = None
            exit_date = None
            exit_reason = None
            max_price = entry_price
            hit_target_1 = False
            
            for i in range(entry_idx + 1, min(entry_idx + 90, len(df))):
                current_high = df['High'].iloc[i]
                current_low = df['Low'].iloc[i]
                current_date = df['Date'].iloc[i]
                
                # Update max price and trailing stop
                if current_high > max_price:
                    max_price = current_high
                    trailing_stop = max_price * (1 - self.config.TRAILING_STOP_PERCENT / 100)
                    stop_loss = max(stop_loss, trailing_stop)
                
                # Check stop loss
                if current_low <= stop_loss:
                    exit_price = stop_loss
                    exit_date = current_date
                    exit_reason = "Stop Loss" if not hit_target_1 else "Trailing Stop"
                    break
                
                # Check targets
                if current_high >= target_2:
                    exit_price = target_2
                    exit_date = current_date
                    exit_reason = "Target 2"
                    break
                elif current_high >= target_1 and not hit_target_1:
                    hit_target_1 = True
                    if self.config.BREAKEVEN_AFTER_T1:
                        stop_loss = max(stop_loss, entry_price)
            
            if exit_price is None:
                exit_idx = min(entry_idx + 90, len(df)-1)
                exit_price = df['Close'].iloc[exit_idx]
                exit_date = df['Date'].iloc[exit_idx]
                exit_reason = "Time Exit"
            
            # Calculate trade metrics
            pnl_pct = (exit_price - entry_price) / entry_price * 100
            holding_days = (pd.to_datetime(exit_date) - pd.to_datetime(entry_date)).days
            
            trades.append({
                'Symbol': signal.get('Symbol', 'Unknown'),
                'Entry_Date': entry_date,
                'Exit_Date': exit_date,
                'Entry_Price': round(entry_price, 2),
                'Exit_Price': round(exit_price, 2),
                'PnL_Pct': round(pnl_pct, 2),
                'Holding_Days': holding_days,
                'Exit_Reason': exit_reason,
                'Base_Days': signal.get('Base_Days', 0),
                'Volume_Breakout': round(signal.get('Volume_Breakout_Ratio', 0), 2)
            })
        
        return trades
    
    def calculate_performance_metrics(self, results_df):
        """Calculate performance metrics"""
        total_trades = len(results_df)
        winning_trades = len(results_df[results_df['PnL_Pct'] > 0])
        losing_trades = len(results_df[results_df['PnL_Pct'] <= 0])
        win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0
        
        avg_win = results_df[results_df['PnL_Pct'] > 0]['PnL_Pct'].mean() if winning_trades > 0 else 0
        avg_loss = results_df[results_df['PnL_Pct'] <= 0]['PnL_Pct'].mean() if losing_trades > 0 else 0
        
        total_profit = results_df[results_df['PnL_Pct'] > 0]['PnL_Pct'].sum()
        total_loss = abs(results_df[results_df['PnL_Pct'] <= 0]['PnL_Pct'].sum())
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        print("\n" + "="*70)
        print("📊 BACKTEST RESULTS SUMMARY")
        print("="*70)
        print(f"Total Trades: {total_trades}")
        print(f"Winning Trades: {winning_trades}")
        print(f"Losing Trades: {losing_trades}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Average Win: {avg_win:.2f}%")
        print(f"Average Loss: {avg_loss:.2f}%")
        print(f"Profit Factor: {profit_factor:.2f}")
        print("="*70)
        
        self.metrics = {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_return': results_df['PnL_Pct'].sum(),
            'avg_holding_days': results_df['Holding_Days'].mean()
        }
    
    def save_results(self, results_df):
        """Save backtest results to CSV"""
        os.makedirs(self.config.RESULTS_DIR, exist_ok=True)
        
        filepath = os.path.join(self.config.RESULTS_DIR, 'backtest_results.csv')
        results_df.to_csv(filepath, index=False)
        print(f"\n✓ Results saved to {filepath}")

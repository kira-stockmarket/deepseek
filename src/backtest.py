"""
Enhanced Backtesting engine with better performance metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import os

class BacktestEngine:
    def __init__(self, config, strategy, data_fetcher, ipo_database):
        self.config = config
        self.strategy = strategy
        self.data_fetcher = data_fetcher
        self.ipo_database = ipo_database
        self.results = []
        
    def run_backtest(self):
        """
        Run backtest from 2014 to present
        """
        ipo_stocks = self.ipo_database.get_all_ipos()
        all_trades = []
        
        print(f"Starting backtest with {len(ipo_stocks)} IPO stocks...")
        
        for idx, row in ipo_stocks.iterrows():
            symbol = row['Symbol']
            company = row['Company']
            ipo_date = row['IPO_Date']
            
            print(f"\n[{idx+1}/{len(ipo_stocks)}] Backtesting {symbol} - {company}")
            
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
        
        # Create results dataframe
        if all_trades:
            results_df = pd.DataFrame(all_trades)
            self.calculate_performance_metrics(results_df)
            self.save_results(results_df)
            self.plot_results(results_df)
            return results_df
        else:
            print("\n✗ No trades generated during backtest period")
            return pd.DataFrame()
    
    def simulate_trades(self, df, signals):
        """
        Simulate trades with trailing stop loss and targets
        """
        trades = []
        
        for _, signal in signals.iterrows():
            entry_date = signal['Breakout_Date']
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
            trailing_stop = stop_loss
            hit_target_1 = False
            
            for i in range(entry_idx + 1, min(entry_idx + 90, len(df))):
                current_high = df['High'].iloc[i]
                current_low = df['Low'].iloc[i]
                current_close = df['Close'].iloc[i]
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
                    # Move stop to breakeven
                    if self.config.BREAKEVEN_AFTER_T1:
                        stop_loss = max(stop_loss, entry_price)
            
            if exit_price is None:
                # Exit at last available price
                exit_price = df['Close'].iloc[min(entry_idx + 90, len(df)-1)]
                exit_date = df['Date'].iloc[min(entry_idx + 90, len(df)-1)]
                exit_reason = "Time Exit"
            
            # Calculate trade metrics
            pnl_pct = (exit_price - entry_price) / entry_price * 100
            holding_days = (pd.to_datetime(exit_date) - pd.to_datetime(entry_date)).days
            
            trades.append({
                'Symbol': signal['Symbol'],
                'Entry_Date': entry_date,
                'Exit_Date': exit_date,
                'Entry_Price': round(entry_price, 2),
                'Exit_Price': round(exit_price, 2),
                'PnL_Pct': round(pnl_pct, 2),
                'Holding_Days': holding_days,
                'Exit_Reason': exit_reason,
                'Base_Days': signal['Base_Days'],
                'RR_Ratio': round(signal['RR_Ratio_1'], 2),
                'Volume_Breakout': round(signal['Volume_Breakout_Ratio'], 2)
            })
        
        return trades
    
    def calculate_performance_metrics(self, results_df):
        """
        Calculate comprehensive performance metrics
        """
        total_trades = len(results_df)
        winning_trades = len(results_df[results_df['PnL_Pct'] > 0])
        losing_trades = len(results_df[results_df['PnL_Pct'] <= 0])
        win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0
        
        avg_win = results_df[results_df['PnL_Pct'] > 0]['PnL_Pct'].mean() if winning_trades > 0 else 0
        avg_loss = results_df[results_df['PnL_Pct'] <= 0]['PnL_Pct'].mean() if losing_trades > 0 else 0
        
        total_profit = results_df[results_df['PnL_Pct'] > 0]['PnL_Pct'].sum()
        total_loss = abs(results_df[results_df['PnL_Pct'] <= 0]['PnL_Pct'].sum())
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        avg_holding_days = results_df['Holding_Days'].mean()
        total_return = results_df['PnL_Pct'].sum()
        
        # Calculate drawdown
        cumulative = results_df['PnL_Pct'].cumsum()
        running_max = cumulative.expanding().max()
        drawdown = cumulative - running_max
        max_drawdown = drawdown.min()
        
        print("\n" + "="*70)
        print("📊 BACKTEST RESULTS SUMMARY (2014 - Present)")
        print("="*70)
        print(f"Total Trades: {total_trades}")
        print(f"Winning Trades: {winning_trades}")
        print(f"Losing Trades: {losing_trades}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Average Win: {avg_win:.2f}%")
        print(f"Average Loss: {avg_loss:.2f}%")
        print(f"Profit Factor: {profit_factor:.2f}")
        print(f"Average Holding Days: {avg_holding_days:.1f}")
        print(f"Total Return: {total_return:.2f}%")
        print(f"Max Drawdown: {max_drawdown:.2f}%")
        print("="*70)
        
        # Store metrics
        self.metrics = {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'avg_holding_days': avg_holding_days
        }
    
    def save_results(self, results_df):
        """Save backtest results to CSV"""
        os.makedirs(self.config.RESULTS_DIR, exist_ok=True)
        
        # Save detailed results
        filepath = os.path.join(self.config.RESULTS_DIR, 'backtest_results.csv')
        results_df.to_csv(filepath, index=False)
        
        # Save summary
        summary_filepath = os.path.join(self.config.RESULTS_DIR, 'backtest_summary.csv')
        if hasattr(self, 'metrics'):
            summary_df = pd.DataFrame([self.metrics])
            summary_df.to_csv(summary_filepath, index=False)
        
        print(f"\n✓ Results saved to {self.config.RESULTS_DIR}")
    
    def plot_results(self, results_df):
        """Generate comprehensive visualization"""
        os.makedirs(self.config.RESULTS_DIR, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        
        fig = plt.figure(figsize=(20, 12))
        
        # Equity curve
        ax1 = plt.subplot(3, 3, 1)
        results_df['Cumulative_Return'] = results_df['PnL_Pct'].cumsum()
        ax1.plot(pd.to_datetime(results_df['Entry_Date']), results_df['Cumulative_Return'], linewidth=2)
        ax1.set_title('Equity Curve', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Cumulative Return (%)')
        ax1.grid(True, alpha=0.3)
        
        # PnL Distribution
        ax2 = plt.subplot(3, 3, 2)
        ax2.hist(results_df['PnL_Pct'], bins=20, edgecolor='black', alpha=0.7)
        ax2.axvline(x=0, color='red', linestyle='--', linewidth=2)
        ax2.set_title('PnL Distribution', fontsize=12, fontweight='bold')
        ax2.set_xlabel('PnL (%)')
        ax2.set_ylabel('Frequency')
        
        # Exit Reasons Pie Chart
        ax3 = plt.subplot(3, 3, 3)
        exit_counts = results_df['Exit_Reason'].value_counts()
        colors = ['#2ecc71', '#e74c3c', '#f39c12', '#3498db']
        ax3.pie(exit_counts.values, labels=exit_counts.index, autopct='%1.1f%%', 
                colors=colors, startangle=90)
        ax3.set_title('Exit Reasons', fontsize=12, fontweight='bold')
        
        # Monthly Returns
        ax4 = plt.subplot(3, 3, 4)
        results_df['Month'] = pd.to_datetime(results_df['Entry_Date']).dt.to_period('M')
        monthly_returns = results_df.groupby('Month')['PnL_Pct'].sum()
        ax4.bar(range(len(monthly_returns)), monthly_returns.values, color='skyblue')
        ax4.set_title('Monthly Returns', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Month')
        ax4.set_ylabel('Return (%)')
        
        # Holding Period Distribution
        ax5 = plt.subplot(3, 3, 5)
        ax5.hist(results_df['Holding_Days'], bins=30, edgecolor='black', alpha=0.7, color='orange')
        ax5.set_title('Holding Period Distribution', fontsize=12, fontweight='bold')
        ax5.set_xlabel('Days')
        ax5.set_ylabel('Frequency')
        
        # Win/Loss by Year
        ax6 = plt.subplot(3, 3, 6)
        results_df['Year'] = pd.to_datetime(results_df['Entry_Date']).dt.year
        yearly_stats = results_df.groupby('Year').agg({
            'PnL_Pct': ['count', 'sum', 'mean']
        }).round(2)
        yearly_stats.columns = ['Trades', 'Total_Return', 'Avg_Return']
        ax6.plot(yearly_stats.index, yearly_stats['Total_Return'], marker='o', linewidth=2)
        ax6.set_title('Yearly Returns', fontsize=12, fontweight='bold')
        ax6.set_xlabel('Year')
        ax6.set_ylabel('Return (%)')
        ax6.grid(True, alpha=0.3)
        
        # Volume Breakout vs PnL
        ax7 = plt.subplot(3, 3, 7)
        ax7.scatter(results_df['Volume_Breakout'], results_df['PnL_Pct'], alpha=0.6)
        ax7.set_title('Volume Breakout vs PnL', fontsize=12, fontweight='bold')
        ax7.set_xlabel('Volume Ratio')
        ax7.set_ylabel('PnL (%)')
        
        # Risk-Reward vs PnL
        ax8 = plt.subplot(3, 3, 8)
        ax8.scatter(results_df['RR_Ratio'], results_df['PnL_Pct'], alpha=0.6, color='green')
        ax8.set_title('Risk-Reward vs PnL', fontsize=12, fontweight='bold')
        ax8.set_xlabel('R:R Ratio')
        ax8.set_ylabel('PnL (%)')
        
        # Cumulative PnL by Symbol
        ax9 = plt.subplot(3, 3, 9)
        symbol_pnl = results_df.groupby('Symbol')['PnL_Pct'].sum().sort_values(ascending=True)[-15:]
        ax9.barh(range(len(symbol_pnl)), symbol_pnl.values, color=['green' if x > 0 else 'red' for x in symbol_pnl.values])
        ax9.set_yticks(range(len(symbol_pnl)))
        ax9.set_yticklabels(symbol_pnl.index)
        ax9.set_title('Top 15 Symbols by PnL', fontsize=12, fontweight='bold')
        ax9.set_xlabel('Total PnL (%)')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.config.RESULTS_DIR, 'backtest_analysis.png'), dpi=150)
        plt.show()
        
        print(f"✓ Analysis chart saved to {self.config.RESULTS_DIR}/backtest_analysis.png")

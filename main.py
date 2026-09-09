"""
Main application for IPO Base Breakout Strategy
"""

import argparse
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config import Config
from data_fetcher import DataFetcher
from ipo_database import IPODatabase
from strategy import IPOBaseBreakoutStrategy
from backtest import BacktestEngine
from scanner import IPOBaseBreakoutScanner
from notifier import Notifier

def print_banner():
    """Print application banner"""
    print("\n" + "="*70)
    print("📈 IPO BASE BREAKOUT STRATEGY - INDIA")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

def main():
    parser = argparse.ArgumentParser(description='IPO Base Breakout Strategy')
    parser.add_argument('--mode', type=str, default='scan', 
                       choices=['scan', 'backtest', 'both', 'setup'],
                       help='Operation mode: scan, backtest, both, or setup')
    parser.add_argument('--symbols', type=str, nargs='+',
                       help='Specific symbols to scan (optional)')
    parser.add_argument('--years', type=int, default=10,
                       help='Number of years for backtest (default: 10)')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Initialize components
    config = Config()
    config.ensure_directories()
    
    ipo_database = IPODatabase(config)
    data_fetcher = DataFetcher(config)
    strategy = IPOBaseBreakoutStrategy(config)
    scanner = IPOBaseBreakoutScanner(config, strategy, data_fetcher, ipo_database)
    notifier = Notifier(config)
    
    if args.mode == 'setup':
        # Run setup mode
        print("\n🔧 Running setup...")
        print(f"✓ Data directory created: {config.DATA_DIR}")
        print(f"✓ Results directory created: {config.RESULTS_DIR}")
        print(f"✓ IPO database loaded: {len(ipo_database.get_all_ipos())} stocks")
        print(f"✓ Data source: {config.DATA_SOURCE}")
        print("\n✅ Setup complete!")
        return
    
    if args.mode in ['scan', 'both']:
        print("\n📊 Running Daily Scanner...")
        
        if args.symbols:
            # Scan specific symbols
            print(f"Scanning specific symbols: {args.symbols}")
            # Implementation for specific symbols
        else:
            results = scanner.scan_for_opportunities()
            
            # Send notification if enabled
            if config.ENABLE_TELEGRAM:
                opportunities = results.get('opportunities', [])
                message = notifier.format_opportunity_message(opportunities)
                notifier.send_telegram_notification(message)
            
            # Display summary
            if results:
                print("\n" + "="*70)
                print("📊 SCAN RESULTS SUMMARY")
                print("="*70)
                
                if results['opportunities']:
                    print(f"\n🎯 BREAKOUT OPPORTUNITIES ({len(results['opportunities'])}):")
                    for opp in results['opportunities']:
                        print(f"\n📈 {opp['Symbol']} - {opp['Company']}")
                        print(f"   Entry: Above ₹{opp['Recent_High']}")
                        print(f"   Current: ₹{opp['Current_Price']}")
                        print(f"   Stop Loss: ₹{opp['Recent_High'] * 0.9:.2f}")
                        print(f"   Target 1: ₹{opp['Recent_High'] * 1.15:.2f}")
                        print(f"   Target 2: ₹{opp['Recent_High'] * 1.25:.2f}")
                
                if results['watchlist']:
                    print(f"\n👀 WATCHLIST ({len(results['watchlist'])}):")
                    for item in results['watchlist'][:10]:
                        print(f"   • {item['Symbol']} - ₹{item['Current_Price']}")
    
    if args.mode in ['backtest', 'both']:
        print("\n📈 Running Backtest...")
        
        # Adjust start date based on years parameter
        from datetime import timedelta
        start_date = (datetime.now() - timedelta(days=365 * args.years)).strftime('%Y-%m-%d')
        config.START_DATE = start_date
        
        backtest = BacktestEngine(config, strategy, data_fetcher, ipo_database)
        results = backtest.run_backtest()
        
        if results is not None and not results.empty:
            print("\n✅ Backtest completed successfully!")
            print(f"Total trades executed: {len(results)}")
            print(f"Results saved in: {config.RESULTS_DIR}")
    
    print("\n✅ Process completed!")

if __name__ == "__main__":
    main()

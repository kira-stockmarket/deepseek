"""
Main application for IPO Base Breakout Strategy
With enhanced error handling for automation
"""

import argparse
from datetime import datetime
import sys
import os
import traceback
import logging

# Add src to path properly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now import from src package
try:
    from config import Config
    from data_fetcher import DataFetcher
    from ipo_database import IPODatabase
    from strategy import IPOBaseBreakoutStrategy
    from backtest import BacktestEngine
    from scanner import IPOBaseBreakoutScanner
    from notifier import Notifier
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying alternative import...")
    try:
        from src.config import Config
        from src.data_fetcher import DataFetcher
        from src.ipo_database import IPODatabase
        from src.strategy import IPOBaseBreakoutStrategy
        from src.backtest import BacktestEngine
        from src.scanner import IPOBaseBreakoutScanner
        from src.notifier import Notifier
    except ImportError as e2:
        print(f"Alternative import also failed: {e2}")
        print("Current directory:", os.getcwd())
        print("Files in current directory:", os.listdir('.'))
        if os.path.exists('src'):
            print("Files in src directory:", os.listdir('src'))
        sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scanner.log')
    ]
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║         📈 IPO BASE BREAKOUT STRATEGY - INDIA 📈            ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)
    logger.info(f"Starting scanner at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def ensure_directories(config):
    """Ensure all required directories exist"""
    dirs_to_create = [
        config.DATA_DIR,
        config.RESULTS_DIR
    ]
    
    for dir_path in dirs_to_create:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")

def main():
    parser = argparse.ArgumentParser(description='IPO Base Breakout Strategy')
    parser.add_argument('--mode', type=str, default='scan', 
                       choices=['scan', 'backtest', 'both', 'setup'],
                       help='Operation mode: scan, backtest, both, or setup')
    parser.add_argument('--symbols', type=str, nargs='+',
                       help='Specific symbols to scan (optional)')
    parser.add_argument('--years', type=int, default=10,
                       help='Number of years for backtest (default: 10)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        print_banner()
        
        # Initialize components
        config = Config()
        ensure_directories(config)
        
        logger.info(f"Data source: {config.DATA_SOURCE}")
        logger.info(f"Mode: {args.mode}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        ipo_database = IPODatabase(config)
        data_fetcher = DataFetcher(config)
        strategy = IPOBaseBreakoutStrategy(config)
        notifier = Notifier(config)
        
        logger.info(f"Loaded {len(ipo_database.get_all_ipos())} IPO stocks from database")
        
        if args.mode == 'setup':
            # Run setup mode
            logger.info("Running setup...")
            print(f"\n🔧 Setup Information:")
            print(f"✓ Data directory: {config.DATA_DIR}")
            print(f"✓ Results directory: {config.RESULTS_DIR}")
            print(f"✓ IPO database loaded: {len(ipo_database.get_all_ipos())} stocks")
            print(f"✓ Data source: {config.DATA_SOURCE}")
            
            # Test data fetching
            test_symbol = "DMART.NS"
            print(f"\nTesting data fetch for {test_symbol}...")
            test_df = data_fetcher.fetch_stock_data(test_symbol)
            if test_df is not None and not test_df.empty:
                print(f"✓ Data fetching test successful ({test_symbol})")
                print(f"  Rows fetched: {len(test_df)}")
                print(f"  Date range: {test_df['Date'].min()} to {test_df['Date'].max()}")
            else:
                print(f"✗ Data fetching test failed ({test_symbol})")
                print("  This might be due to rate limiting. Try again later.")
            
            print("\n✅ Setup complete!")
            return
        
        if args.mode in ['scan', 'both']:
            logger.info("Starting daily scanner...")
            scanner = IPOBaseBreakoutScanner(config, strategy, data_fetcher, ipo_database)
            
            try:
                if args.symbols:
                    # Scan specific symbols
                    logger.info(f"Scanning specific symbols: {args.symbols}")
                    results = scanner.scan_specific_symbols(args.symbols)
                else:
                    results = scanner.scan_for_opportunities()
                
                # Send notification if enabled
                if config.ENABLE_TELEGRAM and results:
                    opportunities = results.get('opportunities', [])
                    if opportunities:
                        message = notifier.format_opportunity_message(opportunities)
                        notifier.send_telegram_notification(message)
                
                # Display summary
                if results:
                    print("\n" + "="*70)
                    print("📊 SCAN RESULTS SUMMARY")
                    print("="*70)
                    
                    if results.get('opportunities'):
                        print(f"\n🎯 BREAKOUT OPPORTUNITIES ({len(results['opportunities'])}):")
                        for opp in results['opportunities']:
                            print(f"\n📈 {opp.get('Symbol', 'Unknown')} - {opp.get('Company', 'Unknown')}")
                            print(f"   Entry: Above ₹{opp.get('Recent_High', 0):.2f}")
                            print(f"   Current: ₹{opp.get('Current_Price', 0):.2f}")
                            if opp.get('Recent_High', 0) > 0:
                                print(f"   Stop Loss: ₹{opp['Recent_High'] * 0.9:.2f}")
                                print(f"   Target 1: ₹{opp['Recent_High'] * 1.15:.2f}")
                                print(f"   Target 2: ₹{opp['Recent_High'] * 1.25:.2f}")
                    
                    if results.get('watchlist'):
                        print(f"\n👀 WATCHLIST ({len(results['watchlist'])}):")
                        for item in results['watchlist'][:10]:
                            print(f"   • {item.get('Symbol', 'Unknown')} - ₹{item.get('Current_Price', 0):.2f}")
                else:
                    print("\n📊 No results found in this scan")
                    
            except Exception as scan_error:
                logger.error(f"Error during scanning: {scan_error}")
                logger.error(traceback.format_exc())
                print(f"\n❌ Scan error: {scan_error}")
                # Continue execution - don't exit
        
        if args.mode in ['backtest', 'both']:
            logger.info("Starting backtest...")
            
            try:
                # Adjust start date based on years parameter
                from datetime import timedelta
                start_date = (datetime.now() - timedelta(days=365 * args.years)).strftime('%Y-%m-%d')
                config.START_DATE = start_date
                
                backtest = BacktestEngine(config, strategy, data_fetcher, ipo_database)
                results = backtest.run_backtest()
                
                if results is not None and not results.empty:
                    logger.info(f"Backtest completed with {len(results)} trades")
                    print("\n✅ Backtest completed successfully!")
                    print(f"Total trades executed: {len(results)}")
                    print(f"Results saved in: {config.RESULTS_DIR}")
            except Exception as bt_error:
                logger.error(f"Error during backtest: {bt_error}")
                logger.error(traceback.format_exc())
                print(f"\n❌ Backtest error: {bt_error}")
        
        logger.info("Process completed successfully")
        print("\n✅ Process completed!")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Send error notification if configured
        try:
            if 'config' in locals() and config.ENABLE_TELEGRAM:
                notifier = Notifier(config)
                error_message = f"❌ Error in IPO Scanner:\n{str(e)}"
                notifier.send_telegram_notification(error_message)
        except:
            pass
        
        print(f"\n❌ Error: {str(e)}")
        print("\nStack trace:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

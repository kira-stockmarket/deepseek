def scan_for_opportunities(self):
    """
    Scan for current IPO base breakout opportunities
    """
    import os
    
    # Ensure results directory exists
    os.makedirs(self.config.RESULTS_DIR, exist_ok=True)
    
    print("\n🔍 Scanning for IPO Base Breakout Opportunities...")
    print("="*70)
    
    # Get recent IPO stocks (last 2 years for scanning)
    recent_ipos = self.ipo_database.get_recent_ipos(days=730)
    
    if recent_ipos.empty:
        print("✗ No recent IPOs found in database")
        return {'opportunities': [], 'watchlist': [], 'scan_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    opportunities = []
    watchlist = []
    
    # ... rest of the method remains the same
    
    # At the end, always save results (even if empty)
    results = {
        'opportunities': opportunities,
        'watchlist': watchlist,
        'scan_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Always save results
    self.save_scan_results(results)
    
    return results

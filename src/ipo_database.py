"""
IPO Database - List of Indian IPOs since 2014
"""

import pandas as pd
from datetime import datetime
import os

class IPODatabase:
    def __init__(self, config):
        self.config = config
        self.ipo_list = self.load_or_create_ipo_list()
    
    def load_or_create_ipo_list(self):
        """Load IPO list from CSV or create from built-in database"""
        if os.path.exists(self.config.IPO_LIST_FILE):
            try:
                return pd.read_csv(self.config.IPO_LIST_FILE)
            except:
                pass
        return self.create_ipo_database()
    
    def create_ipo_database(self):
        """Create IPO database with major Indian IPOs"""
        
        ipo_data = [
            # Major IPOs since 2014
            {"Symbol": "DMART.NS", "Company": "Avenue Supermarts", "IPO_Date": "2017-03-21", "Sector": "Retail"},
            {"Symbol": "IRCTC.NS", "Company": "IRCTC", "IPO_Date": "2019-10-14", "Sector": "Travel"},
            {"Symbol": "ZOMATO.NS", "Company": "Zomato", "IPO_Date": "2021-07-23", "Sector": "Food Tech"},
            {"Symbol": "PAYTM.NS", "Company": "One97 Communications", "IPO_Date": "2021-11-18", "Sector": "Technology"},
            {"Symbol": "POLICYBZR.NS", "Company": "PB Fintech", "IPO_Date": "2021-11-15", "Sector": "Insurance"},
            {"Symbol": "NYKAA.NS", "Company": "FSN E-Commerce", "IPO_Date": "2021-11-11", "Sector": "E-commerce"},
            {"Symbol": "LICI.NS", "Company": "LIC India", "IPO_Date": "2022-05-17", "Sector": "Insurance"},
            {"Symbol": "DELHIVERY.NS", "Company": "Delhivery", "IPO_Date": "2022-05-24", "Sector": "Logistics"},
            {"Symbol": "AWL.NS", "Company": "Adani Wilmar", "IPO_Date": "2022-02-08", "Sector": "FMCG"},
            {"Symbol": "SBICARD.NS", "Company": "SBI Cards", "IPO_Date": "2020-03-16", "Sector": "Finance"},
            {"Symbol": "HDFCAMC.NS", "Company": "HDFC AMC", "IPO_Date": "2018-08-06", "Sector": "Finance"},
            {"Symbol": "BANDHANBNK.NS", "Company": "Bandhan Bank", "IPO_Date": "2018-03-27", "Sector": "Banking"},
            {"Symbol": "GLAND.NS", "Company": "Gland Pharma", "IPO_Date": "2020-11-20", "Sector": "Pharma"},
            {"Symbol": "CLEAN.NS", "Company": "Clean Science", "IPO_Date": "2021-07-19", "Sector": "Chemicals"},
            {"Symbol": "LODHA.NS", "Company": "Macrotech Developers", "IPO_Date": "2021-04-22", "Sector": "Real Estate"},
            {"Symbol": "POLYCAB.NS", "Company": "Polycab India", "IPO_Date": "2019-04-16", "Sector": "Electrical"},
            {"Symbol": "AFFLE.NS", "Company": "Affle India", "IPO_Date": "2019-08-08", "Sector": "Technology"},
            {"Symbol": "INDIAMART.NS", "Company": "IndiaMART", "IPO_Date": "2019-07-04", "Sector": "Technology"},
            {"Symbol": "HAPPSTMNDS.NS", "Company": "Happiest Minds", "IPO_Date": "2020-09-17", "Sector": "Technology"},
            {"Symbol": "ROUTE.NS", "Company": "Route Mobile", "IPO_Date": "2020-09-21", "Sector": "Technology"},
            {"Symbol": "BURGERKING.NS", "Company": "Burger King India", "IPO_Date": "2020-12-14", "Sector": "Food"},
            {"Symbol": "MAZDOCK.NS", "Company": "Mazagon Dock", "IPO_Date": "2020-10-12", "Sector": "Defense"},
            {"Symbol": "LXCHEM.NS", "Company": "Laxmi Organic", "IPO_Date": "2020-03-25", "Sector": "Chemicals"},
            {"Symbol": "TATVA.NS", "Company": "Tatva Chintan", "IPO_Date": "2021-07-29", "Sector": "Chemicals"},
            {"Symbol": "NUVOCO.NS", "Company": "Nuvoco Vistas", "IPO_Date": "2021-08-23", "Sector": "Cement"},
            {"Symbol": "CHEMPLASTS.NS", "Company": "Chemplast Sanmar", "IPO_Date": "2021-08-24", "Sector": "Chemicals"},
            {"Symbol": "LATENTVIEW.NS", "Company": "Latent View", "IPO_Date": "2021-11-23", "Sector": "Technology"},
            {"Symbol": "EASEMYTRIP.NS", "Company": "Easy Trip Planners", "IPO_Date": "2021-03-19", "Sector": "Travel"},
            {"Symbol": "MTARTECH.NS", "Company": "MTAR Technologies", "IPO_Date": "2021-03-15", "Sector": "Engineering"},
            {"Symbol": "BARBEQUE.NS", "Company": "Barbeque Nation", "IPO_Date": "2021-04-07", "Sector": "Food"},
        ]
        
        df = pd.DataFrame(ipo_data)
        df['IPO_Date'] = pd.to_datetime(df['IPO_Date'])
        
        # Save to CSV
        os.makedirs(self.config.DATA_DIR, exist_ok=True)
        df.to_csv(self.config.IPO_LIST_FILE, index=False)
        
        print(f"✓ Created IPO database with {len(df)} stocks")
        return df
    
    def get_recent_ipos(self, days=100):
        """Get IPOs from recent days"""
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        recent = self.ipo_list[self.ipo_list['IPO_Date'] >= cutoff_date]
        return recent
    
    def get_all_ipos(self):
        """Get all IPOs since 2014"""
        return self.ipo_list

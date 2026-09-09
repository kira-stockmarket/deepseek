"""
IPO Database - Comprehensive list of Indian IPOs since 2014
Using free data sources and manual compilation
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
            return pd.read_csv(self.config.IPO_LIST_FILE)
        else:
            return self.create_ipo_database()
    
    def create_ipo_database(self):
        """Create comprehensive IPO database from 2014 onwards"""
        
        # Major Indian IPOs since 2014 with Yahoo Finance symbols
        ipo_data = [
            # 2014 IPOs
            {"Symbol": "JUSTDIAL.NS", "Company": "Just Dial", "IPO_Date": "2013-06-05", "Issue_Price": 530, "Sector": "Technology"},
            {"Symbol": "OFSS.NS", "Company": "Oracle Financial", "IPO_Date": "2002-07-01", "Issue_Price": 450, "Sector": "Technology"},
            
            # 2015 IPOs
            {"Symbol": "INFRATEL.NS", "Company": "Bharti Infratel", "IPO_Date": "2012-12-11", "Issue_Price": 220, "Sector": "Telecom"},
            {"Symbol": "SYNGENE.NS", "Company": "Syngene International", "IPO_Date": "2015-08-11", "Issue_Price": 250, "Sector": "Healthcare"},
            {"Symbol": "PNBHOUSING.NS", "Company": "PNB Housing", "IPO_Date": "2016-11-07", "Issue_Price": 775, "Sector": "Finance"},
            {"Symbol": "ICICIPRULI.NS", "Company": "ICICI Prudential", "IPO_Date": "2016-09-29", "Issue_Price": 334, "Sector": "Insurance"},
            {"Symbol": "SFL.NS", "Company": "Sheela Foam", "IPO_Date": "2016-12-09", "Issue_Price": 730, "Sector": "Consumer"},
            
            # 2017 IPOs
            {"Symbol": "DMART.NS", "Company": "Avenue Supermarts", "IPO_Date": "2017-03-21", "Issue_Price": 299, "Sector": "Retail"},
            {"Symbol": "CDSL.NS", "Company": "CDSL", "IPO_Date": "2017-06-30", "Issue_Price": 149, "Sector": "Finance"},
            {"Symbol": "AUROPHARMA.NS", "Company": "Aurobindo Pharma", "IPO_Date": "2000-01-01", "Issue_Price": 100, "Sector": "Pharma"},
            {"Symbol": "GODREJAGRO.NS", "Company": "Godrej Agrovet", "IPO_Date": "2017-10-16", "Issue_Price": 460, "Sector": "Agriculture"},
            {"Symbol": "HDFCSTANDARD.NS", "Company": "HDFC Standard Life", "IPO_Date": "2017-11-17", "Issue_Price": 290, "Sector": "Insurance"},
            {"Symbol": "KALYANKJIL.NS", "Company": "Kalyan Jewellers", "IPO_Date": "2021-03-26", "Issue_Price": 87, "Sector": "Consumer"},
            {"Symbol": "MASFIN.NS", "Company": "MAS Financial", "IPO_Date": "2017-10-25", "Issue_Price": 459, "Sector": "Finance"},
            
            # 2018 IPOs
            {"Symbol": "BANDHANBNK.NS", "Company": "Bandhan Bank", "IPO_Date": "2018-03-27", "Issue_Price": 375, "Sector": "Banking"},
            {"Symbol": "HDFCAMC.NS", "Company": "HDFC AMC", "IPO_Date": "2018-08-06", "Issue_Price": 1100, "Sector": "Finance"},
            {"Symbol": "APOLLOHOSP.NS", "Company": "Apollo Hospitals", "IPO_Date": "1983-01-01", "Issue_Price": 50, "Sector": "Healthcare"},
            {"Symbol": "GALAXYSURF.NS", "Company": "Galaxy Surfactants", "IPO_Date": "2018-02-08", "Issue_Price": 1480, "Sector": "Chemicals"},
            
            # 2019 IPOs
            {"Symbol": "IRCTC.NS", "Company": "IRCTC", "IPO_Date": "2019-10-14", "Issue_Price": 320, "Sector": "Travel"},
            {"Symbol": "POLYCAB.NS", "Company": "Polycab India", "IPO_Date": "2019-04-16", "Issue_Price": 538, "Sector": "Electrical"},
            {"Symbol": "METROPOLIS.NS", "Company": "Metropolis Healthcare", "IPO_Date": "2019-04-15", "Issue_Price": 880, "Sector": "Healthcare"},
            {"Symbol": "INDIAMART.NS", "Company": "IndiaMART", "IPO_Date": "2019-07-04", "Issue_Price": 973, "Sector": "Technology"},
            {"Symbol": "STERLING.NS", "Company": "Sterling & Wilson", "IPO_Date": "2019-08-20", "Issue_Price": 780, "Sector": "Engineering"},
            {"Symbol": "AFFLE.NS", "Company": "Affle India", "IPO_Date": "2019-08-08", "Issue_Price": 745, "Sector": "Technology"},
            
            # 2020 IPOs
            {"Symbol": "SBICARD.NS", "Company": "SBI Cards", "IPO_Date": "2020-03-16", "Issue_Price": 755, "Sector": "Finance"},
            {"Symbol": "ROSSARI.NS", "Company": "Rossari Biotech", "IPO_Date": "2020-07-23", "Issue_Price": 425, "Sector": "Chemicals"},
            {"Symbol": "MINDTREE.NS", "Company": "Mindtree", "IPO_Date": "2007-03-07", "Issue_Price": 90, "Sector": "Technology"},
            {"Symbol": "HAPPSTMNDS.NS", "Company": "Happiest Minds", "IPO_Date": "2020-09-17", "Issue_Price": 166, "Sector": "Technology"},
            {"Symbol": "ROUTE.NS", "Company": "Route Mobile", "IPO_Date": "2020-09-21", "Issue_Price": 350, "Sector": "Technology"},
            {"Symbol": "ANGELBRKG.NS", "Company": "Angel Broking", "IPO_Date": "2020-10-05", "Issue_Price": 306, "Sector": "Finance"},
            {"Symbol": "MAZDOCK.NS", "Company": "Mazagon Dock", "IPO_Date": "2020-10-12", "Issue_Price": 145, "Sector": "Defense"},
            {"Symbol": "LXCHEM.NS", "Company": "Laxmi Organic", "IPO_Date": "2020-03-25", "Issue_Price": 130, "Sector": "Chemicals"},
            {"Symbol": "BURGERKING.NS", "Company": "Burger King India", "IPO_Date": "2020-12-14", "Issue_Price": 60, "Sector": "Food"},
            
            # 2021 IPOs (Major Year for IPOs)
            {"Symbol": "IRFC.NS", "Company": "IRFC", "IPO_Date": "2021-01-29", "Issue_Price": 26, "Sector": "Finance"},
            {"Symbol": "INDIGOPNTS.NS", "Company": "Indigo Paints", "IPO_Date": "2021-02-02", "Issue_Price": 1490, "Sector": "Consumer"},
            {"Symbol": "MTARTECH.NS", "Company": "MTAR Technologies", "IPO_Date": "2021-03-15", "Issue_Price": 575, "Sector": "Engineering"},
            {"Symbol": "EASEMYTRIP.NS", "Company": "Easy Trip Planners", "IPO_Date": "2021-03-19", "Issue_Price": 187, "Sector": "Travel"},
            {"Symbol": "BARBEQUE.NS", "Company": "Barbeque Nation", "IPO_Date": "2021-04-07", "Issue_Price": 500, "Sector": "Food"},
            {"Symbol": "MACPOWER.NS", "Company": "Macpower CNC", "IPO_Date": "2021-03-12", "Issue_Price": 140, "Sector": "Engineering"},
            {"Symbol": "SHRIRAM.NS", "Company": "Shriram Properties", "IPO_Date": "2021-12-20", "Issue_Price": 118, "Sector": "Real Estate"},
            {"Symbol": "LODHA.NS", "Company": "Macrotech Developers", "IPO_Date": "2021-04-22", "Issue_Price": 486, "Sector": "Real Estate"},
            {"Symbol": "POWERGRID.NS", "Company": "Power Grid InvIT", "IPO_Date": "2021-05-14", "Issue_Price": 100, "Sector": "Power"},
            {"Symbol": "GLAND.NS", "Company": "Gland Pharma", "IPO_Date": "2020-11-20", "Issue_Price": 1500, "Sector": "Pharma"},
            {"Symbol": "CLEAN.NS", "Company": "Clean Science", "IPO_Date": "2021-07-19", "Issue_Price": 900, "Sector": "Chemicals"},
            {"Symbol": "TATVA.NS", "Company": "Tatva Chintan", "IPO_Date": "2021-07-29", "Issue_Price": 1083, "Sector": "Chemicals"},
            {"Symbol": "NUVOCO.NS", "Company": "Nuvoco Vistas", "IPO_Date": "2021-08-23", "Issue_Price": 570, "Sector": "Cement"},
            {"Symbol": "CHEMPLASTS.NS", "Company": "Chemplast Sanmar", "IPO_Date": "2021-08-24", "Issue_Price": 541, "Sector": "Chemicals"},
            {"Symbol": "AMIORG.NS", "Company": "Ami Organics", "IPO_Date": "2021-09-14", "Issue_Price": 610, "Sector": "Pharma"},
            {"Symbol": "VIJAYA.NS", "Company": "Vijaya Diagnostic", "IPO_Date": "2021-09-14", "Issue_Price": 531, "Sector": "Healthcare"},
            {"Symbol": "APOLLOPIPE.NS", "Company": "Apollo Pipes", "IPO_Date": "2021-10-19", "Issue_Price": 500, "Sector": "Building Materials"},
            {"Symbol": "SAPPHIRE.NS", "Company": "Sapphire Foods", "IPO_Date": "2021-11-18", "Issue_Price": 1180, "Sector": "Food"},
            {"Symbol": "LATENTVIEW.NS", "Company": "Latent View", "IPO_Date": "2021-11-23", "Issue_Price": 197, "Sector": "Technology"},
            {"Symbol": "PAYTM.NS", "Company": "One97 Communications", "IPO_Date": "2021-11-18", "Issue_Price": 2150, "Sector": "Technology"},
            {"Symbol": "POLICYBZR.NS", "Company": "PB Fintech", "IPO_Date": "2021-11-15", "Issue_Price": 980, "Sector": "Insurance"},
            {"Symbol": "NYKAA.NS", "Company": "FSN E-Commerce", "IPO_Date": "2021-11-11", "Issue_Price": 1125, "Sector": "E-commerce"},
            {"Symbol": "ZOMATO.NS", "Company": "Zomato", "IPO_Date": "2021-07-23", "Issue_Price": 76, "Sector": "Food Tech"},
            {"Symbol": "DELHIVERY.NS", "Company": "Delhivery", "IPO_Date": "2022-05-24", "Issue_Price": 487, "Sector": "Logistics"},
            {"Symbol": "LICI.NS", "Company": "LIC India", "IPO_Date": "2022-05-17", "Issue_Price": 949, "Sector": "Insurance"},
            
            # 2022 IPOs
            {"Symbol": "AWL.NS", "Company": "Adani Wilmar", "IPO_Date": "2022-02-08", "Issue_Price": 230, "Sector": "FMCG"},
            {"Symbol": "MEDPLUS.NS", "Company": "Medplus Health", "IPO_Date": "2021-12-23", "Issue_Price": 796, "Sector": "Healthcare"},
            {"Symbol": "RAINBOW.NS", "Company": "Rainbow Children", "IPO_Date": "2022-05-10", "Issue_Price": 542, "Sector": "Healthcare"},
            {"Symbol": "PRUDENT.NS", "Company": "Prudent Corporate", "IPO_Date": "2022-05-20", "Issue_Price": 630, "Sector": "Finance"},
            {"Symbol": "LIFE.NS", "Company": "Life Insurance Corp", "IPO_Date": "2022-05-17", "Issue_Price": 949, "Sector": "Insurance"},
            {"Symbol": "DREAMFOLKS.NS", "Company": "Dreamfolks Services", "IPO_Date": "2022-09-06", "Issue_Price": 326, "Sector": "Travel"},
            {"Symbol": "TAMILNAD.NS", "Company": "Tamilnad Mercantile Bank", "IPO_Date": "2022-09-15", "Issue_Price": 510, "Sector": "Banking"},
            {"Symbol": "KFIN.NS", "Company": "KFin Technologies", "IPO_Date": "2022-12-29", "Issue_Price": 366, "Sector": "Finance"},
            {"Symbol": "LANDMARK.NS", "Company": "Landmark Cars", "IPO_Date": "2022-12-23", "Issue_Price": 506, "Sector": "Automotive"},
            {"Symbol": "ABSLAMC.NS", "Company": "Aditya Birla AMC", "IPO_Date": "2021-10-11", "Issue_Price": 712, "Sector": "Finance"},
            
            # 2023 IPOs
            {"Symbol": "MAININD.NS", "Company": "Mankind Pharma", "IPO_Date": "2023-05-09", "Issue_Price": 1080, "Sector": "Pharma"},
            {"Symbol": "NSLNISP.NS", "Company": "NMDC Steel", "IPO_Date": "2023-02-20", "Issue_Price": 35, "Sector": "Steel"},
            {"Symbol": "IDEA.NS", "Company": "Vodafone Idea", "IPO_Date": "2007-03-06", "Issue_Price": 75, "Sector": "Telecom"},
            {"Symbol": "CYIENT.NS", "Company": "Cyient DLM", "IPO_Date": "2023-07-10", "Issue_Price": 265, "Sector": "Technology"},
            {"Symbol": "IDEAFORGE.NS", "Company": "Ideaforge Technology", "IPO_Date": "2023-07-07", "Issue_Price": 672, "Sector": "Technology"},
            {"Symbol": "CONCORD.NS", "Company": "Concord Biotech", "IPO_Date": "2023-08-18", "Issue_Price": 741, "Sector": "Biotech"},
            {"Symbol": "JUPITER.NS", "Company": "Jupiter Life Line", "IPO_Date": "2023-09-18", "Issue_Price": 735, "Sector": "Healthcare"},
            {"Symbol": "RBL.NS", "Company": "R R Kabel", "IPO_Date": "2023-09-20", "Issue_Price": 1035, "Sector": "Electrical"},
            {"Symbol": "SAMHI.NS", "Company": "Samhi Hotels", "IPO_Date": "2023-09-22", "Issue_Price": 126, "Sector": "Hospitality"},
            {"Symbol": "ZAGGLE.NS", "Company": "Zaggle Prepaid", "IPO_Date": "2023-09-22", "Issue_Price": 164, "Sector": "Fintech"},
            {"Symbol": "YATRA.NS", "Company": "Yatra Online", "IPO_Date": "2023-09-28", "Issue_Price": 142, "Sector": "Travel"},
            {"Symbol": "IRMENERGY.NS", "Company": "IRM Energy", "IPO_Date": "2023-10-26", "Issue_Price": 505, "Sector": "Energy"},
            {"Symbol": "HONASA.NS", "Company": "Honasa Consumer", "IPO_Date": "2023-11-07", "Issue_Price": 324, "Sector": "Consumer"},
            {"Symbol": "ESAF.NS", "Company": "ESAF Small Finance", "IPO_Date": "2023-11-16", "Issue_Price": 60, "Sector": "Banking"},
            {"Symbol": "IREDA.NS", "Company": "IREDA", "IPO_Date": "2023-11-29", "Issue_Price": 32, "Sector": "Finance"},
            {"Symbol": "TATA.NS", "Company": "Tata Technologies", "IPO_Date": "2023-11-30", "Issue_Price": 500, "Sector": "Technology"},
            {"Symbol": "GANDHAR.NS", "Company": "Gandhar Oil", "IPO_Date": "2023-11-30", "Issue_Price": 169, "Sector": "Energy"},
            {"Symbol": "FLAIR.NS", "Company": "Flair Writing", "IPO_Date": "2023-12-05", "Issue_Price": 304, "Sector": "Consumer"},
            {"Symbol": "SURANASOL.NS", "Company": "Surana Solar", "IPO_Date": "2023-12-14", "Issue_Price": 72, "Sector": "Energy"},
            {"Symbol": "DOMS.NS", "Company": "DOMS Industries", "IPO_Date": "2023-12-20", "Issue_Price": 790, "Sector": "Consumer"},
            {"Symbol": "INOX.NS", "Company": "Inox India", "IPO_Date": "2023-12-21", "Issue_Price": 660, "Sector": "Engineering"},
            {"Symbol": "MOTISONS.NS", "Company": "Motisons Jewellers", "IPO_Date": "2023-12-26", "Issue_Price": 55, "Sector": "Consumer"},
            
            # 2024 IPOs (Recent)
            {"Symbol": "BHARTIHEXA.NS", "Company": "Bharti Hexacom", "IPO_Date": "2024-04-12", "Issue_Price": 570, "Sector": "Telecom"},
            {"Symbol": "GODIGIT.NS", "Company": "Go Digit Insurance", "IPO_Date": "2024-05-23", "Issue_Price": 272, "Sector": "Insurance"},
            {"Symbol": "TBO.NS", "Company": "TBO Tek", "IPO_Date": "2024-05-15", "Issue_Price": 920, "Sector": "Travel"},
            {"Symbol": "AADHAR.NS", "Company": "Aadhar Housing", "IPO_Date": "2024-05-15", "Issue_Price": 315, "Sector": "Finance"},
            {"Symbol": "CROMPTON.NS", "Company": "Crompton Greaves", "IPO_Date": "2016-05-13", "Issue_Price": 175, "Sector": "Electrical"},
            {"Symbol": "BAJAJHLDNG.NS", "Company": "Bajaj Housing", "IPO_Date": "2024-09-16", "Issue_Price": 70, "Sector": "Finance"},
            {"Symbol": "PNGJL.NS", "Company": "PN Gadgil Jewellers", "IPO_Date": "2024-09-17", "Issue_Price": 480, "Sector": "Consumer"},
            {"Symbol": "KROSS.NS", "Company": "Kross Ltd", "IPO_Date": "2024-09-16", "Issue_Price": 240, "Sector": "Engineering"},
            {"Symbol": "PREMIER.NS", "Company": "Premier Energies", "IPO_Date": "2024-09-03", "Issue_Price": 450, "Sector": "Energy"},
            {"Symbol": "ECOSMOBL.NS", "Company": "ECOS Mobility", "IPO_Date": "2024-09-04", "Issue_Price": 334, "Sector": "Services"},
        ]
        
        df = pd.DataFrame(ipo_data)
        df['IPO_Date'] = pd.to_datetime(df['IPO_Date'])
        
        # Save to CSV
        os.makedirs(self.config.DATA_DIR, exist_ok=True)
        df.to_csv(self.config.IPO_LIST_FILE, index=False)
        
        return df
    
    def get_recent_ipos(self, days=100):
        """Get IPOs from recent days"""
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        recent = self.ipo_list[self.ipo_list['IPO_Date'] >= cutoff_date]
        return recent
    
    def get_all_ipos(self):
        """Get all IPOs since 2014"""
        return self.ipo_list
    
    def get_ipos_by_year(self, year):
        """Get IPOs for specific year"""
        return self.ipo_list[self.ipo_list['IPO_Date'].dt.year == year]

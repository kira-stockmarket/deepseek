"""
Notification module for sending alerts
"""

import requests
import json
from datetime import datetime

class Notifier:
    def __init__(self, config):
        self.config = config
        
    def send_telegram_notification(self, message):
        """Send notification via Telegram"""
        if not self.config.ENABLE_TELEGRAM:
            return
        
        try:
            url = f"https://api.telegram.org/bot{self.config.TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                'chat_id': self.config.TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                print("✓ Telegram notification sent")
            else:
                print(f"✗ Failed to send Telegram notification: {response.text}")
                
        except Exception as e:
            print(f"✗ Error sending Telegram notification: {e}")
    
    def format_opportunity_message(self, opportunities):
        """Format opportunity message for notification"""
        if not opportunities:
            return "No breakout opportunities found today"
        
        message = f"<b>🎯 IPO Base Breakout Opportunities</b>\n"
        message += f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        for opp in opportunities[:5]:  # Top 5 opportunities
            message += f"<b>📈 {opp['Symbol']} - {opp['Company']}</b>\n"
            message += f"   Current Price: ₹{opp['Current_Price']}\n"
            message += f"   Breakout Level: ₹{opp['Recent_High']}\n"
            message += f"   Distance: {opp['Distance_To_Breakout_Pct']}%\n"
            message += f"   Volume Ratio: {opp['Volume_Ratio']}x\n\n"
        
        return message

import json
import os
from typing import Dict, List, Optional
from config import Config
from datetime import datetime  # Added missing import

class DatabaseManager:
    def __init__(self):
        self.ensure_directories()
        self.ensure_files()
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            Config.DATA_DIR,
            Config.BANNERS_DIR,
            Config.USER_DROPS_DIR,
            Config.REMINDERS_DIR
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def ensure_files(self):
        """Create necessary files if they don't exist"""
        if not os.path.exists(Config.ALLDROPS_FILE):
            self.create_sample_airdrops()
    
    def create_sample_airdrops(self):
        """Create sample airdrops data"""
        sample_data = {
            "airdrops": [
                {
                    "id": "airdrop_001",
                    "title": "MetaMask Airdrop",
                    "description": "Complete tasks to earn META tokens. Connect wallet and perform swaps.",
                    "category": "DeFi",
                    "status": "active",
                    "end_date": "2025-07-30",
                    "reward": "Up to 1000 META",
                    "difficulty": "Easy",
                    "links": {
                        "website": "https://metamask.io",
                        "twitter": "https://twitter.com/metamask",
                        "discord": "https://discord.gg/metamask"
                    },
                    "tasks": [
                        "Connect MetaMask wallet",
                        "Perform 3 swaps",
                        "Hold 0.1 ETH for 30 days"
                    ],
                    "banner": "metamask_banner.jpg"
                },
                {
                    "id": "airdrop_002",
                    "title": "Arbitrum ARB Tokens",
                    "description": "Claim your ARB tokens if you used Arbitrum before the snapshot.",
                    "category": "Layer 2",
                    "status": "hot",
                    "end_date": "2025-08-15",
                    "reward": "500-10000 ARB",
                    "difficulty": "Medium",
                    "links": {
                        "website": "https://arbitrum.io",
                        "twitter": "https://twitter.com/arbitrum"
                    },
                    "tasks": [
                        "Check eligibility",
                        "Connect eligible wallet",
                        "Claim tokens"
                    ],
                    "banner": "arbitrum_banner.jpg"
                }
            ]
        }
        
        with open(Config.ALLDROPS_FILE, 'w') as f:
            json.dump(sample_data, f, indent=2)
    
    def load_all_airdrops(self) -> Dict:
        """Load all airdrops from JSON file"""
        try:
            with open(Config.ALLDROPS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"airdrops": []}
    
    def get_airdrop_by_id(self, airdrop_id: str) -> Optional[Dict]:
        """Get specific airdrop by ID"""
        data = self.load_all_airdrops()
        for airdrop in data.get("airdrops", []):
            if airdrop["id"] == airdrop_id:
                return airdrop
        return None
    
    def load_user_drops(self, username: str) -> List[str]:
        """Load user's saved airdrops"""
        file_path = os.path.join(Config.USER_DROPS_DIR, f"{username}.json")
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get("airdrops", [])
        except FileNotFoundError:
            return []
    
    def save_user_drop(self, username: str, airdrop_id: str):
        """Save airdrop to user's list"""
        file_path = os.path.join(Config.USER_DROPS_DIR, f"{username}.json")
        user_drops = self.load_user_drops(username)
        
        if airdrop_id not in user_drops:
            user_drops.append(airdrop_id)
            
            data = {"airdrops": user_drops}
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
    
    def remove_user_drop(self, username: str, airdrop_id: str):
        """Remove airdrop from user's list"""
        file_path = os.path.join(Config.USER_DROPS_DIR, f"{username}.json")
        user_drops = self.load_user_drops(username)
        
        if airdrop_id in user_drops:
            user_drops.remove(airdrop_id)
            
            data = {"airdrops": user_drops}
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
    
    def load_user_reminders(self, username: str) -> List[Dict]:
        """Load user's reminders"""
        file_path = os.path.join(Config.REMINDERS_DIR, f"{username}_reminders.json")
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get("reminders", [])
        except FileNotFoundError:
            return []
    
    def save_user_reminder(self, username: str, airdrop_id: str, remind_time: str, frequency: str):
        """Save user reminder"""
        file_path = os.path.join(Config.REMINDERS_DIR, f"{username}_reminders.json")
        reminders = self.load_user_reminders(username)
        
        reminder = {
            "airdrop_id": airdrop_id,
            "remind_time": remind_time,
            "frequency": frequency,
            "created_at": str(datetime.now())
        }
        
        reminders.append(reminder)
        
        data = {"reminders": reminders}
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

# Global database instance
db = DatabaseManager()

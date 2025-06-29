import os
from typing import List, Dict, Tuple
from config import Config
from utils.database import db

class PaginationHelper:
    @staticmethod
    def paginate_airdrops(airdrops: List[Dict], page: int = 1) -> Tuple[List[Dict], Dict]:
        """Paginate airdrops list and return page info"""
        total_items = len(airdrops)
        total_pages = (total_items + Config.AIRDROPS_PER_PAGE - 1) // Config.AIRDROPS_PER_PAGE
        
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages if total_pages > 0 else 1
        
        start_idx = (page - 1) * Config.AIRDROPS_PER_PAGE
        end_idx = start_idx + Config.AIRDROPS_PER_PAGE
        
        page_airdrops = airdrops[start_idx:end_idx]
        
        page_info = {
            'current_page': page,
            'total_pages': total_pages,
            'total_items': total_items,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page < total_pages else None
        }
        
        return page_airdrops, page_info

class MessageFormatter:
    @staticmethod
    def format_airdrop_summary(airdrop: Dict) -> str:
        """Format airdrop for list display"""
        status_emoji = {
            'active': '🟢',
            'hot': '🔥',
            'ending_soon': '⚠️',
            'expired': '🔴'
        }
        
        difficulty_emoji = {
            'Easy': '🟢',
            'Medium': '🟡',
            'Hard': '🔴'
        }
        
        emoji = status_emoji.get(airdrop.get('status', 'active'), '🟢')
        diff_emoji = difficulty_emoji.get(airdrop.get('difficulty', 'Easy'), '🟢')
        
        return f"{emoji} **{airdrop['title']}**\n" \
               f"💰 Reward: {airdrop.get('reward', 'TBA')}\n" \
               f"{diff_emoji} Difficulty: {airdrop.get('difficulty', 'Easy')}\n" \
               f"📅 Ends: {airdrop.get('end_date', 'TBA')}\n" \
               f"📝 {airdrop['description'][:100]}{'...' if len(airdrop['description']) > 100 else ''}"
    
    @staticmethod
    def format_airdrop_detail(airdrop: Dict) -> str:
        """Format detailed airdrop information"""
        status_emoji = {
            'active': '🟢 Active',
            'hot': '🔥 Hot',
            'ending_soon': '⚠️ Ending Soon',
            'expired': '🔴 Expired'
        }
        
        message = f"🎯 **{airdrop['title']}**\n\n"
        message += f"📊 Status: {status_emoji.get(airdrop.get('status'), '🟢 Active')}\n"
        message += f"🏷️ Category: {airdrop.get('category', 'General')}\n"
        message += f"💰 Reward: {airdrop.get('reward', 'TBA')}\n"
        message += f"⚡ Difficulty: {airdrop.get('difficulty', 'Easy')}\n"
        message += f"📅 End Date: {airdrop.get('end_date', 'TBA')}\n\n"
        message += f"📝 **Description:**\n{airdrop['description']}\n\n"
        
        if airdrop.get('tasks'):
            message += "✅ **Tasks:**\n"
            for i, task in enumerate(airdrop['tasks'], 1):
                message += f"{i}. {task}\n"
            message += "\n"
        
        if airdrop.get('links'):
            message += "🔗 **Links:**\n"
            links = airdrop['links']
            if links.get('website'):
                message += f"🌐 Website: {links['website']}\n"
            if links.get('twitter'):
                message += f"🐦 Twitter: {links['twitter']}\n"
            if links.get('discord'):
                message += f"💬 Discord: {links['discord']}\n"
        
        return message
    
    @staticmethod
    def format_page_info(page_info: Dict) -> str:
        """Format pagination information"""
        return f"📄 Page {page_info['current_page']}/{page_info['total_pages']} " \
               f"({page_info['total_items']} total airdrops)"

class FileHelper:
    @staticmethod
    def get_banner_path(banner_filename: str) -> str:
        """Get full path to banner image"""
        return os.path.join(Config.BANNERS_DIR, banner_filename)
    
    @staticmethod
    def banner_exists(banner_filename: str) -> bool:
        """Check if banner file exists"""
        if not banner_filename:
            return False
        return os.path.exists(FileHelper.get_banner_path(banner_filename))
    
    @staticmethod
    def create_sample_banner_files():
        """Create sample banner files (placeholder)"""
        sample_banners = ['metamask_banner.jpg', 'arbitrum_banner.jpg']
        for banner in sample_banners:
            banner_path = FileHelper.get_banner_path(banner)
            if not os.path.exists(banner_path):
                # Create empty file as placeholder
                with open(banner_path, 'w') as f:
                    f.write("# Placeholder banner file\n")

class ValidationHelper:
    @staticmethod
    def validate_airdrop_id(airdrop_id: str) -> bool:
        """Validate if airdrop ID exists"""
        return db.get_airdrop_by_id(airdrop_id) is not None
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate telegram username"""
        if not username:
            return False
        # Remove @ if present
        username = username.lstrip('@')
        return len(username) >= 3 and username.isalnum()
    
    @staticmethod
    def sanitize_username(username: str) -> str:
        """Sanitize username for file operations"""
        if not username:
            return "unknown"
        # Remove @ and any special characters
        username = username.lstrip('@')
        return ''.join(c for c in username if c.isalnum() or c in '_-')

# Initialize helper classes
pagination = PaginationHelper()
formatter = MessageFormatter()
file_helper = FileHelper()
validator = ValidationHelper()

# Create sample banner files on import
file_helper.create_sample_banner_files()

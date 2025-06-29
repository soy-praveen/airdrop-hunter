import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)
from telegram.constants import ParseMode
from config import Config
from utils import db, pagination, formatter, file_helper, validator

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AirdropBot:
    def __init__(self):
        self.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup all bot handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        username = validator.sanitize_username(user.username or str(user.id))
        
        welcome_message = f"🎯 **Welcome to Airdrop Hunter Bot, {user.first_name}!**\n\n" \
                         f"🚀 Discover and manage cryptocurrency airdrops easily!\n\n" \
                         f"**Available Features:**\n" \
                         f"🌟 Browse all available airdrops\n" \
                         f"💎 Save airdrops to your wishlist\n" \
                         f"⏰ Set custom reminders\n" \
                         f"🔥 Check hot trending airdrops\n\n" \
                         f"Choose an option below to get started:"
        
        keyboard = self.get_main_keyboard()
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = "🤖 **Airdrop Hunter Bot Help**\n\n" \
                   "**Commands:**\n" \
                   "/start - Start the bot\n" \
                   "/help - Show this help message\n\n" \
                   "**Features:**\n" \
                   "🌟 **All Drops** - Browse all available airdrops\n" \
                   "💎 **My Drops** - View your saved airdrops\n" \
                   "⏰ **Reminders** - Manage your airdrop reminders\n" \
                   "🔥 **Hot Drops** - Check trending airdrops\n\n" \
                   "**How to use:**\n" \
                   "1. Click 'All Drops' to browse airdrops\n" \
                   "2. Click on any airdrop for details\n" \
                   "3. Use 'Wishlist' to save interesting airdrops\n" \
                   "4. Use 'Remind' to set notifications\n\n" \
                   "Happy airdrop hunting! 🎯"
        
        keyboard = self.get_main_keyboard()
        
        await update.message.reply_text(
            help_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    
    def get_main_keyboard(self):
        """Get main menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🌟 All Drops", callback_data="all_drops_1"),
                InlineKeyboardButton("💎 My Drops", callback_data="my_drops_1")
            ],
            [
                InlineKeyboardButton("⏰ Reminders", callback_data="reminders"),
                InlineKeyboardButton("🔥 Hot Drops", callback_data="hot_drops_1")
            ],
            [
                InlineKeyboardButton("ℹ️ Help", callback_data="help"),
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all callback queries"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user = update.effective_user
        username = validator.sanitize_username(user.username or str(user.id))
        
        try:
            if data.startswith("all_drops_"):
                page = int(data.split("_")[-1])
                await self.show_all_drops(query, page)
            
            elif data.startswith("my_drops_"):
                page = int(data.split("_")[-1])
                await self.show_my_drops(query, username, page)
            
            elif data.startswith("hot_drops_"):
                page = int(data.split("_")[-1])
                await self.show_hot_drops(query, page)
            
            elif data.startswith("airdrop_"):
                airdrop_id = data.replace("airdrop_", "")
                await self.show_airdrop_detail(query, airdrop_id, username)
            
            elif data.startswith("wishlist_"):
                airdrop_id = data.replace("wishlist_", "")
                await self.add_to_wishlist(query, username, airdrop_id)
            
            elif data.startswith("remove_wishlist_"):
                airdrop_id = data.replace("remove_wishlist_", "")
                await self.remove_from_wishlist(query, username, airdrop_id)
            
            elif data.startswith("remind_"):
                airdrop_id = data.replace("remind_", "")
                await self.show_reminder_options(query, airdrop_id)
            
            elif data.startswith("set_reminder_"):
                parts = data.split("_", 3)
                airdrop_id, time_option = parts[2], parts[3]
                await self.set_reminder(query, username, airdrop_id, time_option)
            
            elif data == "reminders":
                await self.show_reminders(query, username)
            
            elif data == "help":
                await self.show_help(query)
            
            elif data == "refresh":
                await self.show_main_menu(query)
            
            elif data == "back_to_main":
                await self.show_main_menu(query)
            
            elif data.startswith("back_to_drops_"):
                page = int(data.split("_")[-1])
                await self.show_all_drops(query, page)
        
        except Exception as e:
            logger.error(f"Error handling callback {data}: {e}")
            await query.edit_message_text("❌ An error occurred. Please try again.")
    
    async def show_all_drops(self, query, page: int = 1):
        """Show all airdrops with pagination"""
        all_data = db.load_all_airdrops()
        airdrops = all_data.get("airdrops", [])
        
        if not airdrops:
            await query.edit_message_text(
                "📭 No airdrops available at the moment.\nCheck back later!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")
                ]])
            )
            return
        
        page_airdrops, page_info = pagination.paginate_airdrops(airdrops, page)
        
        message = "🌟 **All Available Airdrops**\n\n"
        message += formatter.format_page_info(page_info) + "\n\n"
        
        keyboard = []
        
        # Add airdrop buttons
        for airdrop in page_airdrops:
            keyboard.append([InlineKeyboardButton(
                f"🎯 {airdrop['title']}", 
                callback_data=f"airdrop_{airdrop['id']}"
            )])
        
        # Add navigation buttons
        nav_buttons = []
        if page_info['has_prev']:
            nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"all_drops_{page_info['prev_page']}"))
        if page_info['has_next']:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"all_drops_{page_info['next_page']}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")])
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_airdrop_detail(self, query, airdrop_id: str, username: str):
        """Show detailed airdrop information"""
        airdrop = db.get_airdrop_by_id(airdrop_id)
        
        if not airdrop:
            await query.edit_message_text("❌ Airdrop not found!")
            return
        
        message = formatter.format_airdrop_detail(airdrop)
        
        # Check if already in wishlist
        user_drops = db.load_user_drops(username)
        is_wishlisted = airdrop_id in user_drops
        
        keyboard = []
        
        # Action buttons
        action_buttons = []
        if is_wishlisted:
            action_buttons.append(InlineKeyboardButton("💔 Remove from Wishlist", callback_data=f"remove_wishlist_{airdrop_id}"))
        else:
            action_buttons.append(InlineKeyboardButton("💎 Add to Wishlist", callback_data=f"wishlist_{airdrop_id}"))
        
        action_buttons.append(InlineKeyboardButton("⏰ Set Reminder", callback_data=f"remind_{airdrop_id}"))
        keyboard.append(action_buttons)
        
        # Back button
        keyboard.append([InlineKeyboardButton("🔙 Back to All Drops", callback_data="all_drops_1")])
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_my_drops(self, query, username: str, page: int = 1):
        """Show user's saved airdrops"""
        user_drop_ids = db.load_user_drops(username)
        
        if not user_drop_ids:
            await query.edit_message_text(
                "💎 **My Drops**\n\n📭 Your wishlist is empty!\n\nBrowse 'All Drops' to add some airdrops to your collection.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🌟 Browse All Drops", callback_data="all_drops_1")],
                    [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
                ]),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get full airdrop data
        all_data = db.load_all_airdrops()
        all_airdrops = {airdrop['id']: airdrop for airdrop in all_data.get("airdrops", [])}
        
        user_airdrops = []
        for airdrop_id in user_drop_ids:
            if airdrop_id in all_airdrops:
                user_airdrops.append(all_airdrops[airdrop_id])
        
        page_airdrops, page_info = pagination.paginate_airdrops(user_airdrops, page)
        
        message = "💎 **My Saved Airdrops**\n\n"
        message += formatter.format_page_info(page_info) + "\n\n"
        
        keyboard = []
        
        # Add airdrop buttons
        for airdrop in page_airdrops:
            keyboard.append([InlineKeyboardButton(
                f"🎯 {airdrop['title']}", 
                callback_data=f"airdrop_{airdrop['id']}"
            )])
        
        # Add navigation buttons
        nav_buttons = []
        if page_info['has_prev']:
            nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"my_drops_{page_info['prev_page']}"))
        if page_info['has_next']:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"my_drops_{page_info['next_page']}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")])
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

    async def show_hot_drops(self, query, page: int = 1):
        """Show hot/trending airdrops"""
        all_data = db.load_all_airdrops()
        all_airdrops = all_data.get("airdrops", [])
        
        # Filter for hot airdrops
        hot_airdrops = [airdrop for airdrop in all_airdrops if airdrop.get('status') == 'hot']
        
        if not hot_airdrops:
            await query.edit_message_text(
                "🔥 **Hot Drops**\n\n🚫 No hot airdrops at the moment.\nCheck back later for trending opportunities!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")
                ]]),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        page_airdrops, page_info = pagination.paginate_airdrops(hot_airdrops, page)
        
        message = "🔥 **Hot Trending Airdrops**\n\n"
        message += formatter.format_page_info(page_info) + "\n\n"
        
        keyboard = []
        
        # Add airdrop buttons
        for airdrop in page_airdrops:
            keyboard.append([InlineKeyboardButton(
                f"🔥 {airdrop['title']}", 
                callback_data=f"airdrop_{airdrop['id']}"
            )])
        
        # Add navigation buttons
        nav_buttons = []
        if page_info['has_prev']:
            nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"hot_drops_{page_info['prev_page']}"))
        if page_info['has_next']:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"hot_drops_{page_info['next_page']}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")])
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

    async def add_to_wishlist(self, query, username: str, airdrop_id: str):
        """Add airdrop to user's wishlist"""
        airdrop = db.get_airdrop_by_id(airdrop_id)
        
        if not airdrop:
            await query.answer("❌ Airdrop not found!", show_alert=True)
            return
        
        db.save_user_drop(username, airdrop_id)
        await query.answer(f"💎 Added '{airdrop['title']}' to your wishlist!", show_alert=True)
        
        # Refresh the airdrop detail view
        await self.show_airdrop_detail(query, airdrop_id, username)

    async def remove_from_wishlist(self, query, username: str, airdrop_id: str):
        """Remove airdrop from user's wishlist"""
        airdrop = db.get_airdrop_by_id(airdrop_id)
        
        if not airdrop:
            await query.answer("❌ Airdrop not found!", show_alert=True)
            return
        
        db.remove_user_drop(username, airdrop_id)
        await query.answer(f"💔 Removed '{airdrop['title']}' from your wishlist!", show_alert=True)
        
        # Refresh the airdrop detail view
        await self.show_airdrop_detail(query, airdrop_id, username)

    async def show_reminder_options(self, query, airdrop_id: str):
        """Show reminder time options"""
        airdrop = db.get_airdrop_by_id(airdrop_id)
        
        if not airdrop:
            await query.answer("❌ Airdrop not found!", show_alert=True)
            return
        
        message = f"⏰ **Set Reminder for {airdrop['title']}**\n\n" \
                 f"Choose when you'd like to be reminded:"
        
        keyboard = []
        
        # Add reminder options
        for option_text, minutes in Config.REMINDER_OPTIONS.items():
            keyboard.append([InlineKeyboardButton(
                f"⏰ {option_text}", 
                callback_data=f"set_reminder_{airdrop_id}_{option_text.replace(' ', '_')}"
            )])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f"airdrop_{airdrop_id}")])
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

    async def set_reminder(self, query, username: str, airdrop_id: str, time_option: str):
        """Set reminder for airdrop"""
        airdrop = db.get_airdrop_by_id(airdrop_id)
        
        if not airdrop:
            await query.answer("❌ Airdrop not found!", show_alert=True)
            return
        
        # Convert time option back to readable format
        time_readable = time_option.replace('_', ' ')
        
        # Save reminder (simplified version - in production you'd integrate with a scheduler)
        db.save_user_reminder(username, airdrop_id, time_readable, "once")
        
        await query.answer(f"⏰ Reminder set for '{airdrop['title']}' in {time_readable}!", show_alert=True)
        
        # Go back to airdrop detail
        await self.show_airdrop_detail(query, airdrop_id, username)

    async def show_reminders(self, query, username: str):
        """Show user's active reminders"""
        reminders = db.load_user_reminders(username)
        
        if not reminders:
            await query.edit_message_text(
                "⏰ **My Reminders**\n\n📭 No active reminders.\n\nSet reminders from airdrop details to stay updated!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🌟 Browse Airdrops", callback_data="all_drops_1")],
                    [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
                ]),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        message = "⏰ **My Active Reminders**\n\n"
        
        all_data = db.load_all_airdrops()
        all_airdrops = {airdrop['id']: airdrop for airdrop in all_data.get("airdrops", [])}
        
        for i, reminder in enumerate(reminders[-10:], 1):  # Show last 10 reminders
            airdrop_id = reminder['airdrop_id']
            if airdrop_id in all_airdrops:
                airdrop_title = all_airdrops[airdrop_id]['title']
                message += f"{i}. 🎯 **{airdrop_title}**\n"
                message += f"   ⏰ Remind in: {reminder['remind_time']}\n"
                message += f"   📅 Set on: {reminder['created_at'][:10]}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
        ]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

    async def show_help(self, query):
        """Show help information"""
        await self.help_command(query, None)

    async def show_main_menu(self, query):
        """Show main menu"""
        message = "🎯 **Airdrop Hunter Bot**\n\n" \
                 "Choose an option below:"
        
        keyboard = self.get_main_keyboard()
        
        await query.edit_message_text(
            message,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        await update.message.reply_text(
            "🤖 Please use the buttons below to navigate the bot!",
            reply_markup=self.get_main_keyboard()
        )

    def run(self):
        """Run the bot"""
        logger.info("Starting Airdrop Hunter Bot...")
        self.application.run_polling()

# Global bot instance
bot = AirdropBot()

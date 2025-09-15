import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import asyncio
from datetime import datetime

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Get group and channel links from environment variables
GROUP_LINK = os.getenv("GROUP_LINK", "https://t.me/joinchat/example_group")
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/example_channel")

# Dictionary to track cleanup times for each group
group_cleanup_times = {}

async def send_join_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send group and channel join links on every message"""
    try:
        # Don't respond to bot's own messages
        if update.message and update.message.from_user.is_bot:
            return
            
        chat_id = update.effective_chat.id
        
        # Send join links
        message_text = f"📢 Join our community!\n\nGroup: {GROUP_LINK}\nChannel: {CHANNEL_LINK}"
        sent_message = await context.bot.send_message(chat_id=chat_id, text=message_text)
        
        # Schedule cleanup if not already scheduled for this group
        if chat_id not in group_cleanup_times or \
           (datetime.now() - group_cleanup_times[chat_id]).total_seconds() >= 600:
            asyncio.create_task(schedule_cleanup(chat_id, context))
            group_cleanup_times[chat_id] = datetime.now()
            
    except Exception as e:
        logger.error(f"Error in send_join_links: {e}")

async def schedule_cleanup(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Schedule a cleanup for this group after 600 seconds"""
    await asyncio.sleep(600)
    await cleanup_messages(chat_id, context)

async def cleanup_messages(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Delete all messages in the group"""
    try:
        # Get recent messages (last 100 messages)
        messages = []
        async for message in context.bot.get_chat_history(chat_id, limit=100):
            messages.append(message)
        
        # Delete each message
        for message in messages:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
                await asyncio.sleep(0.1)  # Small delay to avoid rate limiting
            except Exception as e:
                # Some messages might not be deletable (too old, etc.)
                logger.warning(f"Could not delete message {message.message_id}: {e}")
                
        # Send a notification that cleanup completed
        notice = await context.bot.send_message(
            chat_id=chat_id, 
            text="🧹 All messages have been cleaned up!"
        )
        
        # Delete the notice after 5 seconds
        await asyncio.sleep(5)
        await context.bot.delete_message(chat_id=chat_id, message_id=notice.message_id)
        
    except Exception as e:
        logger.error(f"Error in cleanup_messages: {e}")

def main():
    """Start the bot"""
    # Check if token is set
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable is not set!")
        return
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handler for all messages
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, send_join_links))

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

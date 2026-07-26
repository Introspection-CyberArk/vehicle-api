"""
Vehicle OSINT Bot - Vercel Serverless Handler
Powered By @Introspection007
"""

import os
import sys
import json
import logging
import re
from typing import Dict, Any

# Setup path for imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================
# GET BOT TOKEN
# ============================================

def get_bot_token() -> str:
    """Get bot token from environment"""
    token = (
        os.environ.get("BOT_TOKEN") or
        os.environ.get("bot_token") or
        os.environ.get("VERCEL_BOT_TOKEN") or
        os.environ.get("TELEGRAM_BOT_TOKEN")
    )
    
    if token:
        logger.info(f"✅ BOT_TOKEN found (length: {len(token)})")
        return token
    
    raise ValueError("❌ BOT_TOKEN not found in any source")

# Get token
try:
    BOT_TOKEN = get_bot_token()
    logger.info("✅ Bot token loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to get BOT_TOKEN: {e}")
    raise

# ============================================
# IMPORTS (After path setup)
# ============================================

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    logger.info("✅ Telegram module loaded")
except ImportError as e:
    logger.error(f"❌ Failed to import telegram: {e}")
    raise

try:
    from utils.scraper import get_vehicle_details
    from utils.formatter import VehicleDataFormatter
    logger.info("✅ Utils module loaded")
except ImportError as e:
    logger.error(f"❌ Failed to import utils: {e}")
    raise

# ============================================
# CREATE APPLICATION
# ============================================

try:
    application = Application.builder().token(BOT_TOKEN).build()
    logger.info("✅ Application created successfully")
except Exception as e:
    logger.error(f"❌ Failed to create application: {e}")
    raise

# ============================================
# COMMAND HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome = """🚗 *Vehicle OSINT Bot*

I can fetch vehicle details from Indian registration numbers!

*How to use:*
Simply send me a vehicle registration number like:
`DL01AB1234` or `KA01AB5678`

*Commands:*
/start - Show this message
/help - Get help
/about - About this bot

*Data Available:*
• Owner Name
• Model Name
• City & Address
• Phone Number
• Fuel Type
• Vehicle Class
• Registration Date
• Insurance Status

⚡ Powered By @Introspection007"""
    
    await update.message.reply_text(welcome, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """📖 *Vehicle OSINT Bot Help*

*How to use:*
1. Send a valid vehicle registration number
2. The bot will fetch and display details

*Example:*
`DL01AB1234`
`MH01AB5678`
`KA03XY9876`

*Supported Formats:*
• 10-digit alphanumeric (DL01AB1234)
• State code + RTO code + series + number

*Need support?*
Contact: @Introspection007"""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    about_text = """🤖 *Vehicle OSINT Bot*

*Version:* 1.0
*Creator:* @Introspection007

*Features:*
• Fetch vehicle details from RC numbers
• Owner information
• Vehicle specifications
• Insurance status

*Disclaimer:*
This bot uses public data sources. Use responsibly.

⚡ Powered By @Introspection007"""
    
    await update.message.reply_text(about_text, parse_mode="Markdown")

async def handle_rc_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process RC number and return vehicle details"""
    user_message = update.message.text.strip().upper()
    
    # Validate format
    rc_pattern = r'^[A-Z]{2}\d{2}[A-Z]{2}\d{4}$'
    if not re.match(rc_pattern, user_message):
        await update.message.reply_text(
            "❌ *Invalid RC Number Format*\n\n"
            "Please send a valid registration number in this format:\n"
            "`DL01AB1234`\n\n"
            "Example: `KA01AB5678`",
            parse_mode="Markdown"
        )
        return
    
    # Send typing indicator
    await update.message.chat.send_action(action="typing")
    
    try:
        # Fetch vehicle details
        data = get_vehicle_details(user_message)
        
        if data.get("error"):
            await update.message.reply_text(
                f"❌ *Error*\n\n{data['error']}\n\n"
                "Please check the RC number and try again.",
                parse_mode="Markdown"
            )
            return
        
        # Format response
        formatter = VehicleDataFormatter()
        response = formatter.format_vehicle_details(data)
        
        await update.message.reply_text(response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error processing RC: {e}")
        await update.message.reply_text(
            "❌ *Error*\n\n"
            "Something went wrong. Please try again later.\n\n"
            "If the problem persists, contact @Introspection007",
            parse_mode="Markdown"
        )

# ============================================
# REGISTER HANDLERS
# ============================================

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("about", about))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_rc_number))

# ============================================
# VERCEL SERVERLESS HANDLER
# ============================================

# This is the key fix - Vercel needs a top-level async function named 'handler'
# or an object with a 'handler' method.

async def handler(request):
    """Main Vercel serverless function handler."""
    try:
        logger.info("📨 Request received")
        
        # Parse the incoming request body
        body = await request.json() if hasattr(request, 'json') else {}
        logger.info(f"Body: {str(body)[:200]}...")
        
        # Create a Telegram Update object from the request body
        update = Update.de_json(body, application.bot)
        
        # Process the update through the application
        await application.process_update(update)
        logger.info("✅ Update processed successfully")
        
        # Return a success response
        return {
            "statusCode": 200,
            "body": "OK",
            "headers": {
                "Content-Type": "text/plain"
            }
        }
    except Exception as e:
        logger.error(f"❌ Handler error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "statusCode": 500,
            "body": f"Internal Server Error: {str(e)}"
        }

# For local testing
if __name__ == "__main__":
    logger.info("🚀 Starting Vehicle OSINT Bot (Local)...")
    logger.info(f"BOT_TOKEN: {BOT_TOKEN[:10]}...")
    application.run_polling()

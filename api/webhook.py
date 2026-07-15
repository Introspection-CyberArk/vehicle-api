import os
import sys
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.scraper import get_comprehensive_vehicle_details
from utils.formatter import VehicleDataFormatter

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================
# GET BOT TOKEN - MULTIPLE METHODS
# ============================================

def get_bot_token():
    """Try multiple ways to get bot token"""
    
    # Method 1: Direct from environment
    token = os.environ.get("BOT_TOKEN")
    if token:
        logger.info("✅ BOT_TOKEN found in environment")
        return token
    
    # Method 2: From Vercel's process.env
    token = os.environ.get("bot_token")
    if token:
        logger.info("✅ bot_token found in environment (lowercase)")
        return token
    
    # Method 3: From Vercel's secrets (if using vercel.json secrets)
    # Vercel injects secrets as environment variables with specific naming
    token = os.environ.get("BOT_TOKEN", os.environ.get("bot_token", os.environ.get("VERCEL_BOT_TOKEN")))
    if token:
        logger.info("✅ BOT_TOKEN found via fallback")
        return token
    
    # Method 4: Hardcoded fallback (ONLY FOR TESTING - REMOVE IN PRODUCTION)
    # token = "YOUR_BOT_TOKEN_HERE"  # Uncomment for testing
    
    logger.error("❌ BOT_TOKEN not found in environment")
    return None

# Get token
BOT_TOKEN = get_bot_token()

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set")

# Log token start (for debugging)
logger.info(f"BOT_TOKEN loaded: {BOT_TOKEN[:10]}... (length: {len(BOT_TOKEN)})")

# Create application
application = Application.builder().token(BOT_TOKEN).build()

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
    import re
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
        data = get_comprehensive_vehicle_details(user_message)
        
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
        
        # Send response
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

async def handler(request):
    """Vercel serverless function handler"""
    try:
        # Parse incoming request
        body = await request.json() if request.method == "POST" else {}
        
        # Create update object
        update = Update.de_json(body, application.bot)
        
        # Process update
        await application.process_update(update)
        
        return {"statusCode": 200, "body": "OK"}
        
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {"statusCode": 500, "body": str(e)}

# For local testing
if __name__ == "__main__":
    print("🚀 Starting Vehicle OSINT Bot...")
    print(f"Using token: {BOT_TOKEN[:10]}...")
    application.run_polling()

"""
Vehicle OSINT Bot - Flask API for Vercel
Powered By @Introspection007
"""

import os
import sys
import json
import logging
import re
from flask import Flask, request, jsonify

# Setup path for imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# GET BOT TOKEN
# ============================================

def get_bot_token() -> str:
    """Get bot token from environment"""
    token = (
        os.environ.get("BOT_TOKEN") or
        os.environ.get("bot_token") or
        os.environ.get("VERCEL_BOT_TOKEN")
    )
    if token:
        logger.info(f"✅ BOT_TOKEN found (length: {len(token)})")
        return token
    raise ValueError("❌ BOT_TOKEN not found in any source")

try:
    BOT_TOKEN = get_bot_token()
except Exception as e:
    logger.error(f"❌ Failed to get BOT_TOKEN: {e}")
    BOT_TOKEN = None

# ============================================
# IMPORTS
# ============================================

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    from utils.scraper import get_vehicle_details
    from utils.formatter import VehicleDataFormatter
    logger.info("✅ All modules loaded successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import modules: {e}")
    # We'll handle this gracefully

# ============================================
# CREATE FLASK APP
# ============================================

app = Flask(__name__)

# ============================================
# TELEGRAM BOT COMMAND HANDLERS
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
# CREATE TELEGRAM APPLICATION
# ============================================

telegram_app = None
if BOT_TOKEN:
    try:
        telegram_app = Application.builder().token(BOT_TOKEN).build()
        telegram_app.add_handler(CommandHandler("start", start))
        telegram_app.add_handler(CommandHandler("help", help_command))
        telegram_app.add_handler(CommandHandler("about", about))
        telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_rc_number))
        logger.info("✅ Telegram application created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create Telegram application: {e}")

# ============================================
# FLASK ROUTES
# ============================================

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        "status": "online",
        "service": "Vehicle OSINT Bot",
        "version": "1.0",
        "endpoints": {
            "webhook": "/webhook",
            "health": "/health"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "bot_token_loaded": bool(BOT_TOKEN),
        "telegram_app_loaded": bool(telegram_app)
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram webhook endpoint"""
    try:
        # Get the incoming request body
        body = request.get_json()
        logger.info(f"📨 Webhook received: {str(body)[:200]}...")
        
        if not telegram_app:
            logger.error("❌ Telegram app not initialized")
            return jsonify({"status": "error", "message": "Bot not initialized"}), 500
        
        # Create update object
        update = Update.de_json(body, telegram_app.bot)
        
        # Process the update
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(telegram_app.process_update(update))
        loop.close()
        
        logger.info("✅ Update processed successfully")
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================
# LOCAL TESTING
# ============================================

if __name__ == "__main__":
    if BOT_TOKEN:
        logger.info("🚀 Starting Vehicle OSINT Bot (Local)...")
        logger.info(f"BOT_TOKEN: {BOT_TOKEN[:10]}...")
        # For local testing, run polling OR Flask
        import sys
        if '--webhook' in sys.argv:
            app.run(debug=True, port=5000)
        else:
            if telegram_app:
                telegram_app.run_polling()
    else:
        logger.error("❌ Cannot start bot: BOT_TOKEN not set")

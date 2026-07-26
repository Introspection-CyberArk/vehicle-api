"""
Vehicle OSINT Bot - Vercel Serverless Handler (HTTP Handler)
Powered By @Introspection007
"""

import os
import json
import logging
import re
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

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

# We'll import these only when needed to avoid import errors during build
# if the dependencies aren't installed yet.

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    from utils.scraper import get_vehicle_details
    from utils.formatter import VehicleDataFormatter
    logger.info("✅ All modules loaded successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import modules: {e}")
    # This will fail gracefully at runtime if dependencies aren't installed

# ============================================
# CREATE APPLICATION (if token exists)
# ============================================

application = None
if BOT_TOKEN:
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        logger.info("✅ Telegram application created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create application: {e}")

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

# Register handlers if application exists
if application:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_rc_number))

# ============================================
# VERCEL HTTP HANDLER
# ============================================

class handler(BaseHTTPRequestHandler):
    """
    Vercel HTTP handler for the Python runtime.
    This is the entry point Vercel will look for.
    """
    
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            "status": "online",
            "service": "Vehicle OSINT Bot",
            "message": "Bot is running. Send POST requests for webhook updates."
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_POST(self):
        """Handle POST requests (Telegram webhook)"""
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))
            
            logger.info(f"📨 Webhook received: {str(body)[:200]}...")
            
            # Process the update if application exists
            if application and body:
                update = Update.de_json(body, application.bot)
                # Run the async update processing
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(application.process_update(update))
                loop.close()
                logger.info("✅ Update processed successfully")
            else:
                logger.warning("⚠️ Application not initialized or empty body")
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"❌ Handler error: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{}')

# ============================================
# LOCAL TESTING
# ============================================

if __name__ == "__main__":
    if BOT_TOKEN:
        logger.info("🚀 Starting Vehicle OSINT Bot (Local)...")
        logger.info(f"BOT_TOKEN: {BOT_TOKEN[:10]}...")
        # For local testing, run the polling
        if application:
            application.run_polling()
    else:
        logger.error("❌ Cannot start bot: BOT_TOKEN not set")

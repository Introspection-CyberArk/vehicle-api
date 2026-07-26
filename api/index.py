"""
Vehicle OSINT Bot - Full Version
Powered By @Introspection007
"""

import os
import sys
import json
import logging
import re
import requests
from flask import Flask, request, jsonify

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# GET BOT TOKEN
# ============================================

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not found!")
    BOT_TOKEN = None

# ============================================
# RAPIDAPI CONFIG
# ============================================

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "212fbc324fmsh0bc26391652a8acp11e9dfjsn8e204268a7f4")
RAPIDAPI_HOST = "vehicle-rc-verification-advanced.p.rapidapi.com"
API_BASE_URL = "https://vehicle-rc-verification-advanced.p.rapidapi.com"

# ============================================
# CREATE FLASK APP
# ============================================

app = Flask(__name__)

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_vehicle_details(rc_number):
    """Fetch vehicle details from RapidAPI"""
    rc = rc_number.strip().upper()
    
    endpoints = [
        f"/v1/vehicle/rc/{rc}",
        f"/api/vehicle/{rc}",
        f"/rc/{rc}"
    ]
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
        "Content-Type": "application/json"
    }
    
    for endpoint in endpoints:
        url = f"{API_BASE_URL}{endpoint}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": data,
                    "registration_number": rc
                }
        except:
            continue
    
    return {"success": False, "error": "Vehicle not found"}

def send_telegram_message(chat_id, text):
    """Send a message via Telegram API"""
    if not BOT_TOKEN:
        return False
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except:
        return False

def format_vehicle_info(data):
    """Format vehicle data for Telegram"""
    if not data.get("success"):
        return "❌ *Vehicle not found*\n\nPlease check the RC number and try again."
    
    info = data.get("data", {})
    rc = data.get("registration_number", "Unknown")
    
    # Extract fields
    owner = info.get("ownerName") or info.get("owner_name") or "N/A"
    model = info.get("modelName") or info.get("model") or "N/A"
    make = info.get("make") or info.get("maker") or "N/A"
    city = info.get("city") or info.get("city_name") or "N/A"
    fuel = info.get("fuelType") or info.get("fuel_type") or "N/A"
    reg_date = info.get("registrationDate") or info.get("reg_date") or "N/A"
    
    insurance = info.get("insuranceStatus") or info.get("insurance_status") or "N/A"
    
    message = f"""🚗 *Vehicle Details*
📋 *RC:* `{rc}`

👤 *Owner:* {owner}
🚙 *Model:* {model}
🏭 *Make:* {make}
📍 *City:* {city}
⛽ *Fuel:* {fuel}
📆 *Registration:* {reg_date}
🛡️ *Insurance:* {insurance}

━━━━━━━━━━━━━━━━━━━━━
⚡ @Introspection007"""
    
    return message

# ============================================
# FLASK ROUTES
# ============================================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "service": "Vehicle OSINT Bot",
        "version": "2.0",
        "endpoints": {
            "webhook": "/webhook",
            "health": "/health"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "bot_token_loaded": bool(BOT_TOKEN)
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Main webhook handler"""
    try:
        body = request.get_json()
        logger.info(f"📨 Webhook received")
        
        if not BOT_TOKEN:
            return jsonify({"error": "BOT_TOKEN not set"}), 500
        
        from telegram import Update
        
        update = Update.de_json(body, None)
        
        if not update or not update.message:
            return jsonify({"status": "ok"}), 200
        
        chat_id = update.message.chat.id
        user_message = update.message.text.strip()
        
        # Handle /start
        if user_message == "/start":
            welcome = """🚗 *Vehicle OSINT Bot*

Send me any Indian vehicle registration number to get details!

*Example:* `MH48AS2241`

*Commands:*
/start - This message
/help - Help

⚡ Powered By @Introspection007"""
            send_telegram_message(chat_id, welcome)
            return jsonify({"status": "ok"}), 200
        
        # Handle /help
        if user_message == "/help":
            help_text = """📖 *How to use:*

Simply send a vehicle registration number like:
`MH48AS2241` or `DL01AB1234`

The bot will fetch and display:
• Owner name
• Vehicle model
• Make
• City
• Fuel type
• Registration date
• Insurance status

⚡ Powered By @Introspection007"""
            send_telegram_message(chat_id, help_text)
            return jsonify({"status": "ok"}), 200
        
        # Check if it's an RC number
        rc_pattern = r'^[A-Z]{2}\d{2}[A-Z]{2}\d{4}$'
        if re.match(rc_pattern, user_message.upper()):
            # Send typing indicator
            send_telegram_message(chat_id, "🔍 *Fetching vehicle details...*")
            
            # Get vehicle info
            result = get_vehicle_details(user_message)
            
            # Format and send response
            response = format_vehicle_info(result)
            send_telegram_message(chat_id, response)
            
            return jsonify({"status": "ok"}), 200
        
        # Unknown command
        send_telegram_message(
            chat_id,
            "❌ *Unknown command*\n\nSend a vehicle number like `MH48AS2241` or use /help"
        )
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================
# LOCAL TESTING
# ============================================

if __name__ == "__main__":
    logger.info("🚀 Starting Vehicle OSINT Bot...")
    app.run(debug=True, port=5000)

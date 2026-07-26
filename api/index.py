"""
Vehicle OSINT Bot - With Vahanx.in Fallback
Powered By @Introspection007
"""

import os
import sys
import json
import logging
import re
import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup

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
# API CONFIGURATIONS
# ============================================

# Primary API (Cloudflare)
WORKING_API_URL = "https://findings-mens-gathering-guaranteed.trycloudflare.com/api/vehicle"

# Vahanx.in as fallback
VAHANX_URL = "https://vahanx.in/rc-search"

# ============================================
# CREATE FLASK APP
# ============================================

app = Flask(__name__)

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_vehicle_details_vahanx(rc_number):
    """Fetch vehicle details from Vahanx.in (web scraping fallback)"""
    rc = rc_number.strip().upper()
    
    try:
        url = f"{VAHANX_URL}/{rc}"
        logger.info(f"🔍 Trying Vahanx: {rc}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://vahanx.in/"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Try to extract registration number from h1
            reg_number = None
            h1 = soup.find("h1")
            if h1:
                reg_number = h1.text.strip()
            
            # Extract card details
            def extract_card(label):
                for div in soup.select(".hrcd-cardbody"):
                    span = div.find("span")
                    if span and label.lower() in span.text.lower():
                        p = div.find("p")
                        return p.get_text(strip=True) if p else None
                return None
            
            def get_value(label):
                try:
                    div = soup.find("span", string=label)
                    if div:
                        div = div.find_parent("div")
                        p = div.find("p") if div else None
                        return p.get_text(strip=True) if p else None
                except:
                    return None
            
            # Extract data
            owner = extract_card("Owner Name") or get_value("Owner Name") or "N/A"
            model = extract_card("Modal Name") or get_value("Model Name") or "N/A"
            city = extract_card("City Name") or get_value("City Name") or "N/A"
            address = extract_card("Address") or get_value("Address") or "N/A"
            phone = extract_card("Phone") or get_value("Phone") or "N/A"
            fuel = get_value("Fuel Type") or "N/A"
            vehicle_class = get_value("Vehicle Class") or "N/A"
            reg_date = get_value("Registration Date") or "N/A"
            rto = get_value("Registered RTO") or "N/A"
            
            # Insurance
            insurance = get_value("Insurance Company") or "N/A"
            insurance_upto = get_value("Insurance Upto") or get_value("Insurance Expiry") or "N/A"
            
            # PUC
            puc = get_value("PUC Upto") or "N/A"
            
            # Check if we got valid data
            if owner != "N/A" or model != "N/A":
                return {
                    "success": True,
                    "data": {
                        "owner_name": owner,
                        "model": model,
                        "make": "N/A",
                        "city": city,
                        "address": address,
                        "phone": phone,
                        "vehicle_type": vehicle_class,
                        "fuel_descritpion": fuel,
                        "registration_date": reg_date,
                        "registered_at": rto,
                        "previous_insurance_carrier": insurance,
                        "previous_policy_valid_upto": insurance_upto,
                        "pucc_expiry_date": puc
                    },
                    "registration_number": reg_number or rc,
                    "source": "vahanx.in"
                }
                
    except Exception as e:
        logger.error(f"❌ Vahanx error: {e}")
    
    return None

def get_vehicle_details(rc_number):
    """Fetch vehicle details from primary API, fallback to Vahanx"""
    rc = rc_number.strip().upper()
    
    # Try primary API first
    try:
        url = f"{WORKING_API_URL}/{rc}"
        logger.info(f"🔍 Trying primary API: {rc}")
        
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Primary API found data for {rc}")
            return {
                "success": True,
                "data": data,
                "registration_number": rc,
                "source": "primary"
            }
        else:
            logger.warning(f"⚠️ Primary API returned {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Primary API error: {e}")
    
    # Fallback to Vahanx
    logger.info(f"🔄 Falling back to Vahanx for {rc}")
    vahanx_result = get_vehicle_details_vahanx(rc)
    if vahanx_result:
        return vahanx_result
    
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
    except Exception as e:
        logger.error(f"❌ Send message error: {e}")
        return False

def format_vehicle_info(data):
    """Format vehicle data for Telegram"""
    if not data.get("success"):
        return "❌ *Vehicle not found*\n\nPlease check the RC number and try again."
    
    info = data.get("data", {})
    rc = data.get("registration_number", "Unknown")
    source = data.get("source", "primary")
    
    # Extract fields
    owner = info.get("owner_name") or info.get("ownerName") or "N/A"
    model = info.get("model") or info.get("modelName") or info.get("modal_name") or "N/A"
    make = info.get("make") or info.get("maker") or info.get("internal_make_name") or "N/A"
    city = info.get("city") or info.get("city_name") or "N/A"
    address = info.get("address") or info.get("permanent_address") or info.get("correspondence_address") or "N/A"
    phone = info.get("phone") or info.get("phone_number") or info.get("Phone") or "N/A"
    
    # Vehicle type
    vehicle_type = info.get("vehicle_type") or info.get("class_category") or info.get("vehicle_class") or "N/A"
    
    # Fuel type
    fuel = info.get("fuel_descritpion") or info.get("fuel_type") or "N/A"
    
    # Registration date
    reg_date = info.get("registration_date") or info.get("registrationDate") or "N/A"
    
    # Insurance
    insurance = info.get("previous_insurance_carrier") or info.get("insuranceStatus") or info.get("insurance_company") or "N/A"
    insurance_upto = info.get("previous_policy_valid_upto") or info.get("insuranceExpiry") or info.get("insurance_upto") or "N/A"
    
    # RTO
    rto = info.get("registered_at") or info.get("rto") or info.get("Registered RTO") or "N/A"
    
    # PUC
    puc = info.get("pucc_expiry_date") or info.get("pucExpiry") or info.get("PUC Upto") or "N/A"
    
    # Chassis and Engine (if available)
    chassis = info.get("chassis_number") or "N/A"
    engine = info.get("engine_number") or "N/A"
    
    message = f"""🚗 *Vehicle Details*
📋 *RC:* `{rc}`

👤 *Owner:* {owner}
🚙 *Model:* {model}
🏭 *Make:* {make}
📍 *City:* {city}
📞 *Phone:* {phone}
🏷️ *Type:* {vehicle_type}
⛽ *Fuel:* {fuel}
📆 *Registration:* {reg_date}
🏢 *RTO:* {rto}
🛡️ *Insurance:* {insurance}
📅 *Insurance Upto:* {insurance_upto}
🔍 *PUC Expiry:* {puc}"""
    
    # Add chassis and engine if available
    if chassis != "N/A":
        message += f"\n🔧 *Chassis:* `{chassis}`"
    if engine != "N/A":
        message += f"\n⚙️ *Engine:* `{engine}`"
    
    # Add address if available and different from city
    if address != "N/A" and address != city:
        message += f"\n📍 *Address:* {address}"
    
    # Add source info
    source_label = "Vahanx.in" if source == "vahanx.in" else "Primary"
    message += f"\n\n📡 *Source:* {source_label}"
    message += f"\n━━━━━━━━━━━━━━━━━━━━━\n⚡ @Introspection007"
    
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
        logger.info("📨 Webhook received")
        
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

Send me any Indian vehicle registration number to get complete details!

*Commands:*
/start - Show this message
/help - Get help

⚡ Powered By @Introspection007"""
            send_telegram_message(chat_id, welcome)
            return jsonify({"status": "ok"}), 200
        
        # Handle /help
        if user_message == "/help":
            help_text = """📖 *How to use:*

Simply send any Indian vehicle registration number.

The bot will fetch and display:
• Owner name
• Vehicle model and make
• City and address
• Vehicle type
• Fuel type
• Registration date
• RTO details
• Insurance information
• PUC expiry

⚡ Powered By @Introspection007"""
            send_telegram_message(chat_id, help_text)
            return jsonify({"status": "ok"}), 200
        
        # Check if it's an RC number
        rc_pattern = r'^[A-Z]{2,3}\d{1,4}[A-Z]{1,3}\d{1,4}$'
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
            "❌ *Invalid input*\n\nPlease send a valid vehicle registration number or use /help"
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

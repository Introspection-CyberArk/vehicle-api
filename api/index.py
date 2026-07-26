"""
Vehicle OSINT Bot - Flask API for Vercel (DEBUG VERSION)
Powered By @Introspection007
"""

import os
import sys
import json
import logging
import traceback
from flask import Flask, request, jsonify

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ============================================
# GET BOT TOKEN
# ============================================

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not found in environment!")
    BOT_TOKEN = None
else:
    logger.info(f"✅ BOT_TOKEN found (length: {len(BOT_TOKEN)})")

# ============================================
# CREATE FLASK APP
# ============================================

app = Flask(__name__)

# ============================================
# SIMPLE TEST ENDPOINTS
# ============================================

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        "status": "online",
        "service": "Vehicle OSINT Bot",
        "version": "1.0-debug",
        "bot_token_loaded": bool(BOT_TOKEN),
        "endpoints": {
            "webhook": "/webhook",
            "health": "/health",
            "test": "/test"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "bot_token_loaded": bool(BOT_TOKEN)
    })

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint to verify bot token"""
    if not BOT_TOKEN:
        return jsonify({"error": "BOT_TOKEN not set"}), 500
    
    try:
        import requests
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=10)
        return jsonify({
            "token_valid": response.status_code == 200,
            "response": response.json() if response.status_code == 200 else None,
            "status_code": response.status_code
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram webhook endpoint - DEBUG VERSION"""
    try:
        # Log the request
        logger.info("=" * 50)
        logger.info("📨 Webhook received")
        
        # Get the incoming request body
        body = request.get_json()
        logger.info(f"Body: {json.dumps(body)[:500]}...")
        
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN not set")
            return jsonify({"status": "error", "message": "BOT_TOKEN not set"}), 500
        
        # Test import telegram
        try:
            from telegram import Update
            logger.info("✅ telegram imported")
        except ImportError as e:
            logger.error(f"❌ telegram import error: {e}")
            return jsonify({"status": "error", "message": f"Import error: {str(e)}"}), 500
        
        # Create update object
        update = Update.de_json(body, None)
        logger.info(f"✅ Update created: {update}")
        
        # Simple response for testing
        if update.message and update.message.text:
            user_message = update.message.text
            logger.info(f"User message: {user_message}")
            
            # Send a simple reply
            try:
                import requests
                reply_text = f"✅ Bot is working! You said: {user_message}"
                send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                send_data = {
                    "chat_id": update.message.chat.id,
                    "text": reply_text
                }
                response = requests.post(send_url, json=send_data, timeout=10)
                logger.info(f"✅ Reply sent: {response.status_code}")
            except Exception as e:
                logger.error(f"❌ Failed to send reply: {e}")
        
        logger.info("✅ Webhook processed successfully")
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500

# ============================================
# LOCAL TESTING
# ============================================

if __name__ == "__main__":
    logger.info("🚀 Starting DEBUG bot...")
    app.run(debug=True, port=5000)

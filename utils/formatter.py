"""
Vehicle OSINT Bot - Formatter Module
Formats vehicle data for Telegram display
Powered By @Introspection007
"""

import re
from datetime import datetime
from typing import Dict, Any, Optional

class VehicleDataFormatter:
    """Format vehicle data for Telegram messages"""
    
    @staticmethod
    def format_vehicle_details(data: Dict[str, Any]) -> str:
        """
        Format vehicle data into a clean Telegram message
        
        Args:
            data: Vehicle data dictionary from scraper
            
        Returns:
            Formatted string for Telegram
        """
        if data.get("error"):
            return f"❌ *Error*\n\n{data['error']}"
        
        rc_number = data.get("registration_number", "Unknown")
        
        # Build response
        response = f"🚗 *Vehicle Details*\n"
        response += f"📋 *RC:* `{rc_number}`\n\n"
        
        # Add all available fields
        fields = [
            ("owner_name", "👤 *Owner:* "),
            ("model_name", "🚙 *Model:* "),
            ("maker", "🏭 *Maker:* "),
            ("city", "🏙️ *City:* "),
            ("address", "📍 *Address:* "),
            ("phone", "📞 *Phone:* "),
            ("fuel_type", "⛽ *Fuel Type:* "),
            ("vehicle_class", "🏷️ *Class:* "),
            ("registration_date", "📆 *Registration:* "),
            ("vehicle_age", "⏳ *Age:* "),
            ("seating_capacity", "💺 *Seating:* "),
            ("cubic_capacity", "🔧 *Engine CC:* "),
            ("rto", "🏢 *RTO:* "),
            ("financer", "🏦 *Financer:* "),
        ]
        
        for key, label in fields:
            value = data.get(key)
            if value:
                response += f"{label}{value}\n"
        
        # Insurance section
        insurance = data.get("insurance", {})
        if insurance:
            status = insurance.get("status", "Unknown")
            status_emoji = "✅" if status.lower() == "active" else "⚠️"
            response += f"🛡️ *Insurance:* {status_emoji} {status}\n"
            
            if insurance.get("company"):
                response += f"🏢 *Company:* {insurance['company']}\n"
            if insurance.get("policy_number"):
                response += f"📄 *Policy:* `{insurance['policy_number']}`\n"
            if insurance.get("expiry_date"):
                response += f"📅 *Expiry:* {insurance['expiry_date']}\n"
        
        # PUC Details
        puc = data.get("puc_details", {})
        if puc:
            if puc.get("puc_number"):
                response += f"🔍 *PUC Number:* {puc['puc_number']}\n"
            if puc.get("puc_valid_upto"):
                response += f"📅 *PUC Valid:* {puc['puc_valid_upto']}\n"
        
        # Validity
        validity = data.get("validity", {})
        if validity:
            if validity.get("fitness_upto"):
                response += f"✅ *Fitness Upto:* {validity['fitness_upto']}\n"
            if validity.get("tax_upto"):
                response += f"💵 *Tax Upto:* {validity['tax_upto']}\n"
        
        # Blacklist Status
        if data.get("blacklist_status") and data.get("blacklist_status") != "NA":
            response += f"⚠️ *Blacklist:* {data['blacklist_status']}\n"
        
        # Footer
        response += f"\n━━━━━━━━━━━━━━━━━━━━━\n⚡ @Introspection007"
        
        return response
    
    @staticmethod
    def format_compact(data: Dict[str, Any]) -> str:
        """Compact format for quick display"""
        if data.get("error"):
            return f"❌ {data['error']}"
        
        lines = []
        rc = data.get("registration_number", "Unknown")
        lines.append(f"🚗 {rc}")
        
        owner = data.get("owner_name")
        if owner:
            lines.append(f"👤 {owner}")
        
        model = data.get("model_name") or data.get("maker")
        if model:
            lines.append(f"🚙 {model}")
        
        city = data.get("city")
        if city:
            lines.append(f"📍 {city}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_error(error_msg: str) -> str:
        """Format error message"""
        return f"❌ *Error*\n\n{error_msg}\n\nPlease try again or contact @Introspection007"
    
    @staticmethod
    def format_rc_validation(rc_number: str) -> str:
        """Format invalid RC message"""
        return f"""❌ *Invalid RC Number Format*

Please send a valid registration number in this format:
`DL01AB1234` or `KA01AB5678`

*You sent:* `{rc_number}`

*Valid formats:*
• 10-digit alphanumeric
• State code + RTO code + series + number
• Example: `DL01AB1234`

━━━━━━━━━━━━━━━━━━━━━
⚡ @Introspection007"""
    
    @staticmethod
    def format_help() -> str:
        """Format help message"""
        return """📖 *Vehicle OSINT Bot Help*

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

*Data Available:*
• Owner Name
• Model Name
• City & Address
• Phone Number
• Fuel Type
• Vehicle Class
• Registration Date
• Insurance Status

*Commands:*
/start - Welcome message
/help - This help
/about - About this bot

━━━━━━━━━━━━━━━━━━━━━
⚡ @Introspection007"""
    
    @staticmethod
    def format_about() -> str:
        """Format about message"""
        return """🤖 *Vehicle OSINT Bot*

*Version:* 1.0
*Creator:* @Introspection007

*Features:*
• Fetch vehicle details from RC numbers
• Owner information
• Vehicle specifications
• Insurance status
• PUC details

*Privacy Notice:*
Data is fetched from public sources.
Use responsibly and ethically.

*Disclaimer:*
This bot is for informational purposes only.
Always verify official documents.

━━━━━━━━━━━━━━━━━━━━━
⚡ @Introspection007"""


# ============================================
# UTILITY FUNCTIONS
# ============================================

def clean_text(text: str) -> str:
    """Clean text for Telegram display"""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters that break Markdown
    text = re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)
    return text.strip()

def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate long text for Telegram"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def format_phone(phone: str) -> str:
    """Format phone number"""
    if not phone:
        return ""
    # Remove non-digits
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f"+91 {digits[:5]} {digits[5:]}"
    return phone

def format_date(date_str: str) -> str:
    """Format date string"""
    if not date_str:
        return ""
    try:
        # Try to parse date
        for fmt in ["%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y"]:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%d %b %Y")
            except:
                continue
        return date_str
    except:
        return date_str

def get_vehicle_emoji(vehicle_class: str) -> str:
    """Get appropriate emoji for vehicle class"""
    if not vehicle_class:
        return "🚗"
    vc = vehicle_class.lower()
    if "car" in vc or "sedan" in vc or "hatch" in vc:
        return "🚗"
    elif "suv" in vc or "jeep" in vc or "muv" in vc:
        return "🚙"
    elif "bike" in vc or "motor" in vc or "two" in vc:
        return "🏍️"
    elif "truck" in vc or "lorry" in vc or "goods" in vc:
        return "🚛"
    elif "bus" in vc:
        return "🚌"
    elif "auto" in vc or "rickshaw" in vc:
        return "🛺"
    else:
        return "🚗"

def get_insurance_emoji(status: str) -> str:
    """Get emoji for insurance status"""
    if not status:
        return "❓"
    if status.lower() == "active":
        return "✅"
    elif status.lower() == "expired":
        return "⚠️"
    else:
        return "❓"

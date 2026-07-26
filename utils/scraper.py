"""
Vehicle OSINT Bot - Scraper Module
Uses IDfy RapidAPI for vehicle information
Powered By @Introspection007
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)

# ============================================
# RAPIDAPI CONFIGURATION
# ============================================

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "212fbc324fmsh0bc26391652a8acp11e9dfjsn8e204268a7f4")
RAPIDAPI_HOST = "vehicle-rc-verification-advanced.p.rapidapi.com"
API_BASE_URL = "https://vehicle-rc-verification-advanced.p.rapidapi.com"

def get_vehicle_details(rc_number: str) -> dict:
    """
    Fetch vehicle details using IDfy's official API via RapidAPI.
    """
    rc = rc_number.strip().upper()
    
    # Try multiple possible endpoints
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
        logger.info(f"🔍 Trying: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ API response received for: {rc}")
                
                # Clean up the response
                if data.get("status") == "error" or data.get("error"):
                    continue
                
                return {
                    "registration_number": rc,
                    "status": "success",
                    "owner_name": data.get("ownerName") or data.get("owner_name"),
                    "model_name": data.get("modelName") or data.get("model"),
                    "maker": data.get("make") or data.get("maker"),
                    "city": data.get("city") or data.get("city_name"),
                    "address": data.get("address") or data.get("permanent_address"),
                    "fuel_type": data.get("fuelType") or data.get("fuel_type"),
                    "vehicle_class": data.get("vehicleClass") or data.get("class_category"),
                    "registration_date": data.get("registrationDate") or data.get("reg_date"),
                    "insurance": {
                        "status": data.get("insuranceStatus", "Unknown"),
                        "company": data.get("insuranceCompany"),
                        "expiry_date": data.get("insuranceExpiry")
                    }
                }
                
        except Exception as e:
            logger.warning(f"⚠️ Endpoint {endpoint} failed: {e}")
            continue
    
    return {"error": f"Vehicle with RC {rc} not found or API error"}

def test_api():
    """Test the API connection"""
    test_rc = "UP80FZ7850"
    result = get_vehicle_details(test_rc)
    print(f"Test result for {test_rc}:")
    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    import json
    test_api()

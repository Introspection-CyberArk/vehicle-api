"""
Vehicle OSINT Bot - Scraper Module
Uses IDfy RapidAPI for vehicle information
Powered By @Introspection007
"""

import os
import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# ============================================
# RAPIDAPI CONFIGURATION
# ============================================

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "212fbc324fmsh0bc26391652a8acp11e9dfjsn8e204268a7f4")
RAPIDAPI_HOST = "vehicle-rc-verification-advanced.p.rapidapi.com"
API_BASE_URL = "https://vehicle-rc-verification-advanced.p.rapidapi.com"

def get_vehicle_details(rc_number: str) -> Dict[str, Any]:
    """
    Fetch vehicle details using IDfy's official API via RapidAPI.
    
    Args:
        rc_number: Vehicle registration number (e.g., DL01AB1234)
        
    Returns:
        Dictionary containing vehicle details or error
    """
    rc = rc_number.strip().upper()
    
    # The endpoint may vary - adjust based on API documentation
    # Common endpoints:
    # Option 1: /v1/vehicle/rc/{rc}
    # Option 2: /api/vehicle/{rc}
    # Option 3: /rc/{rc}
    url = f"{API_BASE_URL}/v1/vehicle/rc/{rc}"
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
        "Content-Type": "application/json"
    }
    
    logger.info(f"🔍 Fetching details for: {rc}")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        logger.info(f"✅ API response received for: {rc}")
        
        # Check if the API returned an error
        if data.get("status") == "error" or data.get("error"):
            error_msg = data.get("message", "API returned an error")
            return {"error": error_msg}
        
        # Map the response to our format
        mapped_data = map_api_response(data, rc)
        mapped_data["status"] = "success"
        
        return mapped_data
        
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"error": f"Vehicle with RC {rc} not found."}
        elif e.response.status_code == 429:
            return {"error": "API rate limit exceeded. Please try again later."}
        return {"error": f"API error: {str(e)}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to vehicle API: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"An unexpected error occurred: {str(e)}"}

def map_api_response(api_data: Dict[str, Any], rc_number: str) -> Dict[str, Any]:
    """
    Map the API response to our bot's format.
    
    Note: This mapping depends on the actual API response structure.
    You may need to adjust field names based on what the API returns.
    """
    
    # Try to extract data from various possible response structures
    # Most APIs return data in a 'data' or 'result' field
    data = api_data.get("data", api_data.get("result", api_data))
    
    # Common fields in vehicle verification APIs
    mapped = {
        "registration_number": data.get("registrationNumber") or data.get("reg_no") or rc_number,
        "owner_name": data.get("ownerName") or data.get("owner_name") or data.get("owner"),
        "model_name": data.get("modelName") or data.get("model_name") or data.get("model"),
        "maker": data.get("make") or data.get("maker") or data.get("make_name"),
        "city": data.get("city") or data.get("city_name") or data.get("rto_city"),
        "address": data.get("address") or data.get("permanent_address"),
        "phone": data.get("phone") or data.get("mobile") or data.get("phone_number"),
        "fuel_type": data.get("fuelType") or data.get("fuel_type"),
        "vehicle_class": data.get("vehicleClass") or data.get("class_category"),
        "registration_date": data.get("registrationDate") or data.get("reg_date"),
        "vehicle_age": data.get("vehicleAge") or data.get("age"),
        "seating_capacity": data.get("seatingCapacity") or data.get("seat_capacity"),
        "cubic_capacity": data.get("cubicCapacity") or data.get("engine_cc"),
        "chassis_number": data.get("chassisNumber") or data.get("chassis_no"),
        "engine_number": data.get("engineNumber") or data.get("engine_no"),
        "rto": data.get("rto") or data.get("registered_rto") or data.get("registered_at"),
        "financer": data.get("financer") or data.get("financier"),
        "blacklist_status": data.get("blacklistStatus") or data.get("black_list_status"),
        "insurance": {
            "status": data.get("insuranceStatus") or data.get("insurance_status", "Unknown"),
            "company": data.get("insuranceCompany") or data.get("insurance_company"),
            "policy_number": data.get("policyNumber") or data.get("policy_no"),
            "expiry_date": data.get("insuranceExpiry") or data.get("insurance_upto")
        },
        "puc_details": {
            "puc_number": data.get("pucNumber") or data.get("pucc_number"),
            "puc_valid_upto": data.get("pucExpiry") or data.get("pucc_expiry_date")
        },
        "validity": {
            "fitness_upto": data.get("fitnessUpto") or data.get("rc_fit_upto"),
            "tax_upto": data.get("taxUpto") or data.get("tax_paid_upto")
        }
    }
    
    # Remove None values
    def clean_dict(d):
        if isinstance(d, dict):
            return {k: clean_dict(v) for k, v in d.items() if v is not None and v != ""}
        return d
    
    return clean_dict(mapped)

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

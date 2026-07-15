import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36",
    "Referer": "https://vahanx.in/",
    "Accept-Language": "en-US,en;q=0.9"
}

def get_comprehensive_vehicle_details(rc_number: str) -> dict:
    """Enhanced scraper for vehicle details"""
    rc = rc_number.strip().upper()
    url = f"https://vahanx.in/rc-search/{rc}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        return {"error": f"Failed to fetch data: {str(e)}"}

    # Helper function to extract card values
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
    registration_number = soup.find("h1").text.strip() if soup.find("h1") else rc
    
    data = {
        "registration_number": registration_number,
        "status": "success",
        "owner_name": extract_card("Owner Name") or get_value("Owner Name"),
        "model_name": extract_card("Modal Name") or get_value("Model Name"),
        "city": extract_card("City Name") or get_value("City Name"),
        "address": extract_card("Address") or get_value("Address"),
        "phone": extract_card("Phone") or get_value("Phone"),
        "fuel_type": get_value("Fuel Type"),
        "vehicle_class": get_value("Vehicle Class"),
        "registration_date": get_value("Registration Date"),
        "insurance_status": "Active" if not extract_card("Insurance Expired") else "Expired"
    }
    
    # Clean None values
    return {k: v for k, v in data.items() if v is not None and v != ""}

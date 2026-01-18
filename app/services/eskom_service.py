import requests
import os
import logging

logger = logging.getLogger(__name__)

def get_loadshedding_status(area_id="gauteng-soweto"):
    """
    Fetches status from EskomSePush.
    Get a token here: https://eskomsepush.gumroad.com/l/api
    """
    api_token = os.environ.get("ESKOM_API_TOKEN")
    
    # Mock Response (If no API key is set, so the app doesn't crash)
    if not api_token:
        return {
            "stage": "2",
            "next_slot": "18:00 - 20:30",
            "source": "Mock Data (Add API Key)"
        }

    headers = {"token": api_token}
    try:
        # 1. Get Status (Global)
        status_url = "https://developer.sepush.co.za/business/2.0/status"
        resp = requests.get(status_url, headers=headers, timeout=5)
        if resp.ok:
            data = resp.json()
            # "eskom" usually holds the national status
            stage = data.get("status", {}).get("eskom", {}).get("stage", "Unknown")
            return {
                "stage": stage,
                "next_slot": "Check ESP App", # Getting exact slots requires a second API call
                "source": "EskomSePush API"
            }
    except Exception as e:
        logger.error(f"ESP Error: {e}")
        
    return {"stage": "?", "next_slot": "Unavailable", "source": "Error"}
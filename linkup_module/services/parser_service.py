class MessageParser:
    """
    Responsible for extracting intent (what they want) and entities (details)
    from the raw message.
    """
    
    CITIES = ["johannesburg", "pretoria", "soweto"]
    
    CATEGORIES = {
        "house": ["house", "rent", "apartment", "flat"],
        "job": ["job", "work", "umsebenzi"],
        "service": ["service", "help", "cleaning", "hair", "repair"]
    }

    @staticmethod
    def parse(message: str):
        """
        Parses the message and returns a structured dictionary.
        """
        message = message.lower()
        result = {
            "type": "unknown", # default
            "city": None,
            "category": None,
            "query": message
        }

        # 1. Check for Weather Intent
        if "weather in" in message:
            result["type"] = "weather"
            result["city"] = message.replace("weather in", "").strip()
            return result

        # 2. Check for Listing Intent (City + Category)
        # Find City
        for city in MessageParser.CITIES:
            if city in message:
                result["city"] = city
                break
        
        # Find Category
        for cat_key, keywords in MessageParser.CATEGORIES.items():
            if any(word in message for word in keywords):
                result["category"] = cat_key
                break
        
        # If we found both, it's a listing search
        if result["city"] and result["category"]:
            result["type"] = "search_listings"
            
        return result
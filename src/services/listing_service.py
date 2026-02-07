from src.models.listing_model import Listing
from src.utils.geo_utils import calculate_distance

class ListingService:
    
    def get_listings_near_me(self, category, user_lat, user_lon, radius_km=50):
        """
        Finds listings within X km of the user's GPS coordinates.
        """
        all_listings = Listing.query.all()
        nearby_listings = []

        for item in all_listings:
            # Filter by Category (if specific)
            if category and category != 'service' and item.category != category:
                continue

            # Calculate Distance
            dist = calculate_distance(user_lat, user_lon, item.latitude, item.longitude)
            
            if dist <= radius_km:
                item_data = item.to_dict()
                item_data['distance'] = round(dist, 1)
                nearby_listings.append(item_data)

        # Sort by distance (closest first)
        nearby_listings.sort(key=lambda x: x['distance'])
        return nearby_listings

    def get_listings(self, location, category, keyword=None):
        try:
            query = Listing.query
            
            # 1. Filter by Category
            if category and category != 'service':
                query = query.filter(Listing.category == category)
                
            # 2. Filter by Location
            if location and isinstance(location, str) and location.lower() != 'near me':
                query = query.filter(Listing.address.contains(location))

            # 3. [FIXED] Filter by Keywords (Split the list!)
            if keyword:
                from sqlalchemy import or_
                
                # Split "salon, hairdresser" into ["salon", "hairdresser"]
                search_terms = [k.strip() for k in keyword.split(',')]
                
                # Create a list of conditions (Is title like 'salon'? OR like 'hairdresser'?)
                conditions = []
                for term in search_terms:
                    term_pattern = f"%{term}%"
                    conditions.append(Listing.title.ilike(term_pattern))
                    conditions.append(Listing.keywords.ilike(term_pattern))
                
                # Apply the OR filter
                query = query.filter(or_(*conditions))
            
            # 4. Limit results (so we don't spam WhatsApp)
            results = query.limit(5).all()
            return [item.to_dict() for item in results]

        except Exception as e:
            print(f"⚠️ Search Error: {e}")
            return []
        
    def format_listings_response(self, listings, context):
        if not listings:
            return (
                f"😕 I couldn't find any *{context}*.\n\n"
                "Try searching for something else, or reply *'Menu'* to see options."
            )
        
        # Friendly Header
        message = f"🔍 *Here is what I found for {context}:*\n\n"
        
        for i, item in enumerate(listings, 1):
            # We add a number (1. 2. 3.) to make it look like a menu
            verified = "✅" if item['is_verified'] else ""
            
            message += (
                f"*{i}. {item['title']}* {verified}\n"
                f"   💰 {item['price']}\n"
                f"   📍 {item['address']}\n"
                f"   📞 {item['contact']}\n\n"
            )
            
        # Call to Action (The Interactive Part)
        message += (
            "💡 *Tip:* You can save a contact by clicking their phone number above.\n"
            "Reply *'New Search'* to look for something else."
        )
        return message
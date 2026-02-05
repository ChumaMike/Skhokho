from app import db
from app.models import LocationTag
from geoalchemy2.elements import WKTElement
from sqlalchemy import func

def scan_surroundings(lat, long, radius_meters=5000):
    """
    Takes user coordinates and finds interesting spots nearby.
    Default radius: 5km (5000m) for testing.
    """
    
    # 1. Convert user's Lat/Long into a Spatial Point
    # PostGIS expects format: POINT(Longitude Latitude)
    user_point = WKTElement(f'POINT({long} {lat})', srid=4326)

    # 2. The Spatial Query (The Magic) 🪄
    # We ask DB: Find all tags where distance(tag, user) < radius
    nearby_tags = LocationTag.query.filter(
        func.ST_DWithin(
            LocationTag.coordinates, 
            user_point, 
            radius_meters,  # Distance in meters (if using geography type) or degrees (geometry)
            True # Use sphere calculation (more accurate)
        )
    ).all()

    # 3. Format the results
    results = []
    for tag in nearby_tags:
        results.append(f"📍 FOUND: {tag.name} ({tag.category})")
        
    return results if results else ["📭 Nothing nearby. You are in the wild."]
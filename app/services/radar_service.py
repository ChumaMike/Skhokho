from app import db
from app.models import Opportunity, NewsItem, Goal
from math import radians, sin, cos, sqrt, atan2

# Earth radius in meters
EARTH_RADIUS = 6371000

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = EARTH_RADIUS
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)
    
    a = sin(delta_phi/2)**2 + cos(phi1) * cos(phi2) * sin(delta_lambda/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return distance

def scan_surroundings(lat, long, radius_meters=5000):
    """
    Takes user coordinates and finds interesting spots nearby.
    Default radius: 5km (5000m) for testing.
    """
    nearby_tags = []
    
    # Get nearby opportunities
    opportunities = Opportunity.query.all()
    for opp in opportunities:
        distance = haversine(lat, long, opp.latitude, opp.longitude)
        if distance <= radius_meters:
            nearby_tags.append(f"🎯 OPPORTUNITY: {opp.title} ({opp.category})")
    
    # Get nearby news items
    news_items = NewsItem.query.all()
    for news in news_items:
        if news.latitude and news.longitude:
            distance = haversine(lat, long, news.latitude, news.longitude)
            if distance <= radius_meters:
                tag = f"📰 NEWS: {news.title}"
                if news.is_breaking:
                    tag = f"🚨 BREAKING: {news.title}"
                nearby_tags.append(tag)
    
    return nearby_tags if nearby_tags else ["📭 Nothing nearby. You are in the wild."]

def get_breaking_news(lat, long, radius_meters=10000):
    """Get breaking news within specified radius"""
    breaking_news = []
    news_items = NewsItem.query.filter_by(is_breaking=True).all()
    
    for news in news_items:
        if news.latitude and news.longitude:
            distance = haversine(lat, long, news.latitude, news.longitude)
            if distance <= radius_meters:
                breaking_news.append({
                    'id': news.id,
                    'title': news.title,
                    'description': news.description,
                    'category': news.category,
                    'location': news.location_name,
                    'source': news.source,
                    'published_at': news.published_at,
                    'is_breaking': news.is_breaking
                })
    
    return breaking_news

def match_opportunities(user, lat, long, radius_meters=5000):
    """Match user goals with nearby opportunities"""
    matched_opportunities = []
    user_goals = Goal.query.filter_by(user_id=user.id, is_completed=False).all()
    opportunities = Opportunity.query.all()
    
    for goal in user_goals:
        for opp in opportunities:
            distance = haversine(lat, long, opp.latitude, opp.longitude)
            if distance <= radius_meters:
                if is_goal_match(goal, opp):
                    matched_opportunities.append({
                        'opportunity': {
                            'id': opp.id,
                            'title': opp.title,
                            'description': opp.description,
                            'category': opp.category,
                            'company': opp.company,
                            'location': opp.location_name,
                            'salary': opp.salary
                        },
                        'goal': {
                            'id': goal.id,
                            'title': goal.title,
                            'description': goal.description
                        },
                        'match_score': calculate_match_score(goal, opp),
                        'distance': distance
                    })
    
    return sorted(matched_opportunities, key=lambda x: x['match_score'], reverse=True)

def is_goal_match(goal, opportunity):
    """Check if an opportunity matches a user's goal"""
    goal_text = (goal.title + " " + (goal.description or "")).lower()
    opp_text = (opportunity.title + " " + (opportunity.description or "") + " " + (opportunity.requirements or "")).lower()
    
    # Look for key skill matches
    tech_keywords = ['software', 'engineering', 'developer', 'programmer', 'coding', 'web', 'app', 'mobile']
    business_keywords = ['business', 'entrepreneur', 'marketing', 'sales', 'management']
    creative_keywords = ['design', 'art', 'creative', 'media']
    
    for keywords in [tech_keywords, business_keywords, creative_keywords]:
        goal_matches = any(keyword in goal_text for keyword in keywords)
        opp_matches = any(keyword in opp_text for keyword in keywords)
        if goal_matches and opp_matches:
            return True
    
    # Also match by category
    if goal.category.lower() in opportunity.category.lower() or opportunity.category.lower() in goal.category.lower():
        return True
    
    return False

def calculate_match_score(goal, opportunity):
    """Calculate a match score between a goal and an opportunity"""
    score = 0
    goal_text = (goal.title + " " + (goal.description or "")).lower()
    opp_text = (opportunity.title + " " + (opportunity.description or "") + " " + (opportunity.requirements or "")).lower()
    
    # Keyword matching
    tech_keywords = ['software', 'engineering', 'developer', 'programmer', 'coding', 'web', 'app', 'mobile']
    business_keywords = ['business', 'entrepreneur', 'marketing', 'sales', 'management']
    creative_keywords = ['design', 'art', 'creative', 'media']
    
    for keywords in [tech_keywords, business_keywords, creative_keywords]:
        goal_count = sum(1 for keyword in keywords if keyword in goal_text)
        opp_count = sum(1 for keyword in keywords if keyword in opp_text)
        score += goal_count * opp_count * 10
    
    # Category matching
    if goal.category.lower() in opportunity.category.lower() or opportunity.category.lower() in goal.category.lower():
        score += 20
    
    return score
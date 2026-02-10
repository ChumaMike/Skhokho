from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.radar_service import scan_surroundings, get_breaking_news, match_opportunities
from app.services.ai_service import get_skhokho_response

location_bp = Blueprint('location', __name__)

@location_bp.route('/scan', methods=['POST'])
@login_required
def scan_area():
    data = request.json
    lat = data.get('latitude')
    lng = data.get('longitude')
    
    if not lat or not lng:
        return jsonify({'error': 'No GPS signal.'}), 400

    # 1. Ask PostGIS what is nearby
    findings = scan_surroundings(lat, lng)
    
    # 2. Prepare the context for the AI
    context_text = f"""
    USER LOCATION REPORT:
    The user is currently standing at Lat: {lat}, Long: {lng}.
    
    RADAR DETECTED THESE SPOTS NEARBY:
    {findings}
    
    INSTRUCTION:
    Based on what is nearby, give the user specific advice. 
    - If it's a Career spot, tell them to network.
    - If it's a Danger zone, warn them to be safe.
    - If nothing is nearby, tell them to keep moving.
    """

    # 3. Ask Skhokho for advice
    ai_advice = get_skhokho_response(
        user_message="What should I do here?", 
        context_data=context_text
    )
    
    return jsonify({
        'findings': findings,
        'advice': ai_advice
    })

@location_bp.route('/local-intel', methods=['POST'])
@login_required
def get_local_intel():
    """Get local breaking news and matching opportunities"""
    data = request.json
    lat = data.get('latitude')
    lng = data.get('longitude')
    
    if not lat or not lng:
        return jsonify({'error': 'No GPS signal.'}), 400

    # Get breaking news
    breaking_news = get_breaking_news(lat, lng)
    
    # Match opportunities with user goals
    matched_opportunities = match_opportunities(current_user, lat, lng)
    
    # Generate AI advice for matched opportunities
    if matched_opportunities:
        opportunities_text = "\n".join([
            f"- {opp['opportunity']['title']} ({opp['opportunity']['category']}) at {opp['opportunity']['location']}"
            for opp in matched_opportunities
        ])
        
        goals_text = "\n".join([
            f"- {goal['title']}"
            for goal in current_user.goals
            if not goal.is_completed
        ])
        
        context_text = f"""
        USER GOALS:
        {goals_text}
        
        MATCHED OPPORTUNITIES NEARBY:
        {opportunities_text}
        
        INSTRUCTION:
        The user has goals and there are matching opportunities nearby. 
        Give specific advice on what the user should do to take advantage of these opportunities.
        Be encouraging and specific about each opportunity.
        """
        
        ai_advice = get_skhokho_response(
            user_message="What should I do about these opportunities?",
            context_data=context_text
        )
    else:
        ai_advice = "No matching opportunities found for your current goals. Keep exploring!"
    
    return jsonify({
        'breaking_news': breaking_news,
        'opportunities': matched_opportunities,
        'advice': ai_advice
    })

@location_bp.route('/intel-update', methods=['GET'])
@login_required
def get_intel_update():
    """Get quick intel update (for dashboard refresh)"""
    # For now, we'll use a default location if no coordinates are provided
    # In production, this would use the user's last known location
    lat = -26.2041  # Johannesburg
    lng = 28.0473
    
    breaking_news = get_breaking_news(lat, lng, 20000)
    matched_opportunities = match_opportunities(current_user, lat, lng, 20000)
    
    return jsonify({
        'breaking_news': breaking_news[:3],  # Return top 3 news items
        'opportunities': matched_opportunities[:2]  # Return top 2 opportunities
    })
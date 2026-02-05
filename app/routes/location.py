from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.radar_service import scan_surroundings
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
    # (We assume the user is at the Microsoft coordinates for testing if they are on localhost)
    # For now, let's trust the browser's coordinates
    findings = scan_surroundings(lat, lng)
    
    # 2. Prepare the context for the AI
    # If findings are empty, we just say "Unknown area"
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
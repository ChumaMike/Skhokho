import base64
import io
import os
from flask import Blueprint, request, jsonify
from PIL import Image
from app.services.ai_service import get_skhokho_response

api_bp = Blueprint('api', __name__)

@api_bp.route('/v1/ask', methods=['POST'])
def public_api():
    # 1. SECURITY CHECK (Middleware) 🛡️
    client_key = request.headers.get('X-API-KEY')
    internal_secret = os.environ.get('SKHOKHO_CLIENT_SECRET')
    
    if not client_key or client_key != internal_secret:
        return jsonify({"error": "Unauthorized Access. Invalid API Key."}), 401

    try:
        # 2. GET DATA FROM THE APP (Macalaa)
        data = request.get_json()
        user_message = data.get('message', '')
        image_data = data.get('image_base64', None) # Expecting Base64 string
        
        # 3. PROCESS IMAGE (If Macalaa sent one) 👁️
        pil_image = None
        if image_data:
            # Decode the base64 string back into an image
            image_bytes = base64.b64decode(image_data)
            pil_image = Image.open(io.BytesIO(image_bytes))

        # 4. ASK SKHOKHO (Reuse your existing brain!) 🧠
        # We pass context="Public API User" since we don't have login info for this
        reply = get_skhokho_response(
            user_message=user_message, 
            context_data="External App User (Macalaa/Blind Assist)", 
            image=pil_image
        )

        # 5. RETURN JSON
        return jsonify({
            "status": "success",
            "reply": reply
        })

    except Exception as e:
        print(f"⚠️ API ERROR: {e}")
        return jsonify({"error": "Skhokho Brain Malfunction"}), 500
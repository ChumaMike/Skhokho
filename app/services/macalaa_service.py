import google.generativeai as genai
from flask import current_app
import json
import os

# Configure Gemini
# Ensure GOOGLE_API_KEY is in your .env file
genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))

def analyze_scene(image_path):
    """
    sends image to Gemini 1.5 Flash for rapid analysis.
    Returns: JSON with description, danger_level, and category.
    """
    try:
        # We use 'gemini-1.5-flash' because it's fast and cheap for video/images
        model = genai.GenerativeModel('gemini-1.5-flash')

        # The Prompt acts as the "system instruction"
        prompt = """
        You are Macalaa, a visual assistant for the Skhokho OS. 
        Analyze this image for a user who might be visually impaired.
        
        Return ONLY a JSON object with these 4 fields:
        1. "description": A short, clear sentence describing the scene.
        2. "danger_level": "CRITICAL" (Guns, Fire, Accident, Assault), "MODERATE" (Pothole, Leak, Obstacle), or "SAFE".
        3. "category": One word (e.g., "Infrastructure", "Safety", "Nature", "Traffic").
        4. "action_needed": "REPORT" (if civic issue), "ALERT" (if danger), or "NONE".
        
        Do not use Markdown formatting. Just the raw JSON string.
        """

        # Load the image
        sample_file = genai.upload_file(image_path, mime_type="image/jpeg")

        # Generate content
        response = model.generate_content([prompt, sample_file])
        
        # Clean the response text (remove ```json ... ``` if present)
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        
        return json.loads(clean_text)

    except Exception as e:
        print(f"❌ Macalaa Vision Error: {e}")
        return {
            "description": "I am having trouble seeing right now.",
            "danger_level": "SAFE",
            "category": "Error",
            "action_needed": "NONE"
        }
import os
import google.generativeai as genai
from PIL import Image
import json

def analyze_issue(description):
    """Mock AI for CivicNerve demo - analyzes issue severity"""
    keywords = ['pothole', 'fire', 'danger']
    description_lower = description.lower()
    for keyword in keywords:
        if keyword in description_lower:
            return 90
    return 40

def get_skhokho_response(user_message, context_data="", image=None):
    """Enhanced Skhokho chatbot with write access to database"""
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        return "System Alert: Neural Link Disconnected (Key Missing)."

    try:
        genai.configure(api_key=api_key)
        
        # USE THE MODERN FLASH MODEL (Handles Text & Images)
        model = genai.GenerativeModel('gemini-flash-latest')

        # SCENARIO A: VISION 👁️ (For Macalaa Environment Scanning)
        if image:
            print("👁️ ACTIVATING SKHOKHO VISION (Gemini 1.5 Flash)...", flush=True)
            prompt = """Analyze this image carefully:
            1. If it's a civic issue (pothole, broken light, danger), describe it and rate severity 0-100
            2. If it's a document, extract key details (dates, prices, names)
            3. If it's an environment/street view, describe what you see and any safety concerns
            4. If there's danger (open manhole, fire, hazard), start with "DANGER:" and describe urgently
            
            Keep response brief but informative. Use local South African context."""
            response = model.generate_content([prompt, image])
            return response.text

        else:
            # SCENARIO B: TEXT CHAT WITH DATABASE WRITE ACCESS
            model = genai.GenerativeModel('gemini-flash-latest')
            
            system_instruction = """
            You are Skhokho, a wise street-smart AI assistant in Soweto, South Africa.
            You have WRITE ACCESS to the user's personal database.
            
            YOUR POWERS (Database Actions):
            When users ask to create/add/save something, output ONLY a JSON command:
            
            1. Add Goal: {"cmd": "add_goal", "title": "Goal title", "description": "Optional details"}
            2. Add Diary Entry: {"cmd": "add_diary", "entry_type": "Thought|Expense|Event", "content": "Entry text"}
            3. Add Network Contact: {"cmd": "add_network", "name": "Person Name", "role": "Their role/profession", "phone": "optional", "email": "optional"}
            4. Set Budget Alert: {"cmd": "set_alert", "threshold": 200, "message": "Alert when balance drops below R200"}
            5. Calculate Baala (Taxi Fare): {"cmd": "baala_calc", "fare": 15, "group_size": 4}
            6. Find Service Providers: {"cmd": "find_service", "service_type": "plumber"} - for queries like "plumber", "electrician", "carpenter"
            
            IMPORTANT RULES:
            - For database actions, output ONLY the JSON (no extra text)
            - For regular chat, use local slang (Sho, Sharp, Eish, Ayt, Yebo)
            - Be concise and helpful
            - Reference the user's context when relevant
            
            PERSONALITY:
            - Street-smart mentor from Soweto
            - Practical and action-oriented
            - Uses local references and slang naturally
            """
            
            full_prompt = f"{system_instruction}\n\nCONTEXT:\n{context_data}\n\nUSER:\n{user_message}"
            
            response = model.generate_content(full_prompt)
            return response.text.replace("```json", "").replace("```", "").strip()
    except Exception as e:
        print(f"⚠️ BRAIN FAILURE: {e}", flush=True)
        
        # DEBUG: If it fails, print what models ARE available
        try:
            print("📋 AVAILABLE MODELS:", flush=True)
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    print(f" - {m.name}", flush=True)
        except:
            pass
            
        return "Eish, my eyes are blurry. I can't process that right now."
    

def get_hustle_plan(goal):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key: return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest') # Use the fast one!
        
        # PROMPT ENGINEERING: Force JSON Output
        prompt = f"""
        You are a business mentor in Soweto.
        Create a 5-step 'Hustle Plan' for: "{goal}".
        
        IMPORTANT: Return ONLY raw JSON. No markdown. No text.
        Format:
        {{
            "title": "Short catchy title",
            "steps": [
                {{"icon": "📝", "task": "Step 1 details"}},
                {{"icon": "💰", "task": "Step 2 details"}}
            ]
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Clean the response (sometimes AI adds ```json ... ```)
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        
        return json.loads(clean_json) # Return as Python Dictionary
        
    except Exception as e:
        print(f"⚠️ PLANNER FAILED: {e}", flush=True)
        return None
import os
import google.generativeai as genai
from PIL import Image
import json

def get_skhokho_response(user_message, context_data="", image=None):
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        return "System Alert: Neural Link Disconnected (Key Missing)."

    try:
        genai.configure(api_key=api_key)
        
        # USE THE MODERN FLASH MODEL (Handles Text & Images)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        system_instruction = "You are Skhokho, a futuristic tactical advisor in Soweto. Use local slang (Sho, Sharp, Eish). Be concise."

        # SCENARIO A: VISION 👁️
        if image:
            print("👁️ ACTIVATING SKHOKHO VISION (Gemini 1.5 Flash)...", flush=True)
            prompt = "Analyze this image. If it's a document, summarize key details (Dates, Prices). If it's a place, is it safe? Keep it brief."
            response = model.generate_content([prompt, image])
            return response.text

        else:
            model = genai.GenerativeModel('gemini-flash-latest')
            
            system_instruction = """
            You are Skhokho, a wise street-smart mentor.
            
            YOUR POWERS:
            You can SAVE data to the user's Life OS.
            If the user asks to add/save a Goal, Diary Entry, or Network Contact, output a JSON command.
            
            COMMAND FORMATS (Output ONLY JSON for these):
            - New Goal:   {"cmd": "add_goal", "title": "Goal Name"}
            - New Diary:  {"cmd": "add_diary", "title": "Topic", "content": "Details"}
            - New Contact:{"cmd": "add_network", "name": "Person Name", "category": "Role (e.g. Mentor)"}
            
            If it's just chat, reply with helpful text (using slang: Sho, Sharp, Eish).
            """
            
            full_prompt = f"{system_instruction}\n\nCONTEXT:\n{context_data}\n\nUSER:\n{user_message}"
            
            response = model.generate_content(full_prompt)
            return response.text.replace("```json", "").replace("```", "").strip()
    except Exception as e:
        print(f"⚠️ BRAIN FAILURE: {e}", flush=True)
        
        # DEBUG: If it fails, print what models ARE available so we stop guessing
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
import os
import google.generativeai as genai
from PIL import Image

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

        # SCENARIO B: TEXT 💬
        else:
            full_prompt = f"{system_instruction}\n\nCONTEXT:\n{context_data}\n\nUSER:\n{user_message}"
            response = model.generate_content(full_prompt)
            return response.text
        
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
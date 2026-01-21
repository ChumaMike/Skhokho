import os
import google.generativeai as genai

def get_skhokho_response(user_message):
    """
    Sends the user's message to Gemini and gets a 'Skhokho' style response.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        return "Eish, my brain is offline. Please check the GOOGLE_API_KEY in your .env file."

    try:
        genai.configure(api_key=api_key)
        
        # --- THE FIX ---
        # We are using a model confirmed to be in your list:
        model = genai.GenerativeModel('gemini-2.0-flash')

        system_prompt = """
        You are Skhokho, a smart, street-wise, and highly motivating personal AI assistant for a South African developer.
        
        Your Personality:
        - You speak English but mix in South African slang (Mzansi style) like "Sho", "Eish", "Yebo", "Dala", "Sharp".
        - You are a Senior Engineer / Life Coach mentor. You are tough but kind.
        - You care about the user's mental health, coding progress, and financial discipline.
        - Keep responses concise (under 3 sentences usually) unless asked for a long explanation.
        
        Current Context: The user is talking to you from their Life OS dashboard.
        """

        full_prompt = f"{system_prompt}\n\nUser: {user_message}\nSkhokho:"
        
        response = model.generate_content(full_prompt)
        return response.text
    
    except Exception as e:
        print(f"Gemini Error: {e}")
        return f"System Glitch: {str(e)}"
import os
import google.generativeai as genai

# Update function to accept 'context_data'
def get_skhokho_response(user_message, context_data=""):
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "System Offline: Check API Key."

    try:
        genai.configure(api_key=api_key)
        # Using the Lite model we found earlier
        model = genai.GenerativeModel('gemini-2.0-flash-lite')

        # We inject the 'context_data' into the prompt
        system_prompt = f"""
        You are Skhokho, a smart, street-wise personal AI assistant (Life OS).
        
        CURRENT SYSTEM STATUS (Use this to give specific advice):
        {context_data}
        
        Your Personality:
        - You speak English with South African slang (Sho, Eish, Yebo, Sharp).
        - You are a Mentor. If the user has low goal progress, push them.
        - If they have no goals, tell them to go to the Goals tab and set one.
        - Keep it concise.
        """

        full_prompt = f"{system_prompt}\n\nUser: {user_message}\nSkhokho:"
        
        response = model.generate_content(full_prompt)
        return response.text
    
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Eish, my brain connection is weak right now."
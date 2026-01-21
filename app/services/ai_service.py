import os
import google.generativeai as genai

# Note: We added 'context_data' as a second argument
def get_skhokho_response(user_message, context_data=None):
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        return "System Offline: Check API Key."

    try:
        genai.configure(api_key=api_key)
        
        # Using the Lite model (Cost efficient)
        model = genai.GenerativeModel('gemini-2.0-flash-lite')

        # This is where the magic happens. We inject the database info.
        system_prompt = f"""
        You are Skhokho, a smart, street-wise personal AI assistant (Life OS).
        
        /// SYSTEM INTELLIGENCE (DATABASE REALITY) ///
        {context_data if context_data else "No user data available."}
        /////////////////////////////////////////////
        
        Your Personality:
        - You speak English with South African slang (Sho, Eish, Yebo, Sharp, Mzansi).
        - You are an Accountability Partner. 
        - USE THE DATA ABOVE. If their goal progress is low (under 20%), push them to work.
        - If they mention money, refer to their recent Balaa stats if relevant.
        - Keep it concise (2-3 sentences max).
        """

        full_prompt = f"{system_prompt}\n\nUser: {user_message}\nSkhokho:"
        
        response = model.generate_content(full_prompt)
        return response.text
    
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Eish, the signal is weak. I can't reach the cloud right now."
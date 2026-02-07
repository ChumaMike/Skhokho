import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class AIService:
    def __init__(self):
        # 1. Setup Google Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ WARNING: GEMINI_API_KEY not found in .env")
        
        genai.configure(api_key=api_key)
        
        # 2. Use the Universal Model Alias (Safer than version numbers)
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def parse_intent(self, user_text, history=None):
        """
        Analyzes the message WITH context from history.
        """
        try:
            # Convert the list of messages into a string for the AI to read
            history_text = ""
            if history:
                for msg in history:
                    role = "User" if msg['role'] == 'user' else "LinkUp Bot"
                    history_text += f"{role}: {msg['text']}\n"

            prompt = f"""
            You are 'LinkUp', a helpful, friendly automated assistant for a Kasi Service App.
            Your goal is to help users find services (plumbers, jobs, rooms).

            CONVERSATION HISTORY:
            {history_text}

            CURRENT MESSAGE: "{user_text}"
            
            TASK:
            Return a JSON object.
            1. If the user greets (hi, hello, sawubona), intent = 'greeting'.
            2. If the user asks for a service (I need x, find me y), intent = 'search_listings'.
            3. If the user is just chatting (Thank you, that's cool), intent = 'chat'.
            
            JSON FORMAT:
            {{
                "intent": "search_listings" OR "greeting" OR "chat",
                "category": "service/house/job",
                "keywords": "extracted keywords",
                "location": "extracted location",
                "chat_response": "If intent is 'chat', write a friendly short reply here."
            }}
            """
            
            response = self.model.generate_content(prompt)
            clean_text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(clean_text)

        except Exception as e:
            print(f"🧠 AI Brain Error: {e}")
            return {"intent": "unknown"}

    def generate_keywords(self, title, category):
        """
        [NEW] Auto-tagging feature for the Dashboard.
        Generates search tags for a new listing.
        """
        try:
            prompt = f"""
            Generate 5 comma-separated search synonyms for a service.
            Title: "{title}"
            Category: "{category}"
            
            Rules:
            1. Return ONLY the words separated by commas.
            2. No intro text, no markdown.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.lower().strip()
        except Exception as e:
            print(f"⚠️ Tagging Failed: {e}")
            return title.lower()

# --- INSTANCE CREATION ---
# We create the single instance HERE, at the bottom.
# This allows other files to say: "from src.services.ai_service import ai_brain"
ai_brain = AIService()
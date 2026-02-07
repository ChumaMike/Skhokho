from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from src.services.ai_service import ai_brain
from src.services.listing_service import ListingService

bot_bp = Blueprint('bot', __name__)
listing_service = ListingService()

# 🧠 MEMORY: Stores chat history for each user
# Format: { 'whatsapp:+27123...': [ {'role': 'user', 'text': 'Hi'}, ... ] }
user_sessions = {}

@bot_bp.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    # 1. Get the Sender's ID and Message
    sender_id = request.values.get('From', '')
    incoming_msg = request.values.get('Body', '').strip()
    
    print(f"📩 New Message from {sender_id}: {incoming_msg}")

    # 2. Initialize Memory if new user
    if sender_id not in user_sessions:
        user_sessions[sender_id] = []
        
    # 3. Add User's Message to History
    user_sessions[sender_id].append({"role": "user", "text": incoming_msg})
    
    # Limit memory to last 10 messages to keep it fast
    user_sessions[sender_id] = user_sessions[sender_id][-10:]

    # 4. Ask the Brain (Sending the whole history!)
    # We pass the history so the AI knows what we talked about previously
    analysis = ai_brain.parse_intent(incoming_msg, history=user_sessions[sender_id])
    
    intent = analysis.get('intent')
    reply = ""

    # --- LOGIC FLOW ---
    if intent == "greeting":
        reply = (
            "👋 *Welcome to LinkUp!* \n\n"
            "I connect you with the best services in the Kasi. "
            "I can help you find a *Plumber*, *Electrician*, *Room to Rent*, or even a *Job*.\n\n"
            "How can I help you today?"
        )
        
    elif intent == "search_listings":
        category = analysis.get("category", "service")
        location = analysis.get("location", "Soweto")
        keywords = analysis.get("keywords", "")
        
        results = listing_service.get_listings(location, category, keyword=keywords)
        reply = listing_service.format_listings_response(results, f"{keywords or category} in {location}")

    elif intent == "clear_memory":
        # Hidden command to reset chat
        user_sessions[sender_id] = []
        reply = "🧹 Memory cleared! We can start fresh."

    else:
        # Fallback: Let the AI Chat naturally using the persona
        reply = analysis.get("chat_response", "I'm not sure how to help with that. Try asking for a service like 'Plumber'.")

    # 5. Add Bot's Reply to History (So it remembers what it said)
    user_sessions[sender_id].append({"role": "model", "text": reply})

    # 6. Send to WhatsApp
    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)
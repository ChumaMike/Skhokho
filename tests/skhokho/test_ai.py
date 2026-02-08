from unittest.mock import patch

def test_ai_chatbot_response(client, auth):
    auth.register()
    auth.login()

    # ✅ FIX: Patch where it is USED (the route file), not where it's defined.
    # Assuming your chat route is in 'app/routes/chat.py'
    with patch('app.routes.chat.get_skhokho_response') as mock_brain:
        mock_brain.return_value = "Sho boss"

        response = client.post('/chat/send', json={
            'message': 'Hello'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert response.json['response'] == "Sho boss"
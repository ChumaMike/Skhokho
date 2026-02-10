from app.models import User
from app.extensions import db

def test_map_interface_loads(client, auth):
    """QA: Does the LinkUp dashboard render?"""
    # Create a user directly and log in
    with client.application.app_context():
        user = User(username="map_test_user", email="map@example.com", wallet_balance=0, reputation_points=0)
        user.set_password("testpassword")
        db.session.add(user)
        db.session.commit()
    
    # Login using auth.login
    auth.login(username="map_test_user", password="testpassword")
    
    response = client.get('/linkup/', follow_redirects=True)
    assert response.status_code == 200
    # We look for the unique CSS ID for the map container
    assert b'id="map"' in response.data or b'LinkUp' in response.data

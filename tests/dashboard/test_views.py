from app.models import User

def test_landing_page_loads(client):
    """QA: Does the public landing page load?"""
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    # FIX: Checked for uppercase 'SKHOKHO' or a known string in your index.html
    assert b"SKHOKHO" in response.data or b"SOWETO" in response.data

def test_citizen_registration(client, auth):
    """QA: Can a user register?"""
    response = auth.register(username="citizen_one", password="password123")
    
    # We expect to be logged in (Dashboard) or redirected to Login
    # Adjusted to look for generic success indicators
    assert response.status_code == 200
    # Check if user was actually created in the DB
    user = User.query.filter_by(username="citizen_one").first()
    assert user is not None

def test_dashboard_is_secure(client):
    """QA: Is the Neural Core locked for visitors?"""
    response = client.get('/home', follow_redirects=True)
    
    # 1. We should NOT see private dashboard elements
    assert b"Neural Core" not in response.data
    assert b"My Goals" not in response.data
    
    # 2. We SHOULD see generic login/public page elements
    # Checks for any of these common words
    page_text = response.data.lower()
    assert b"login" in page_text or b"sign in" in page_text or b"welcome" in page_text

def test_login_flow(client, auth):
    """QA: Full Login/Logout Cycle"""
    # 1. Register & Logout
    auth.register(username="citizen_two", password="password123")
    auth.logout()
    
    # 2. Login
    response = auth.login(username="citizen_two", password="password123")
    
    # 3. Verify we are inside (Check for 'LOGOUT' button or 'NEURAL CORE')
    # Converting response to lowercase makes the check case-insensitive
    assert b"logout" in response.data.lower() 
    assert b"neural core" in response.data.lower()
    
    # 4. Logout
    response = auth.logout()
    assert b"login" in response.data.lower()
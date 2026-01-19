from app.models import User

def test_register(client, app):
    """Test that a new user can register."""
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'securepassword'
    }, follow_redirects=True)
    
    # Check if the registration message appears
    assert b"Registration successful" in response.data
    
    # Check if user actually exists in the Fake DB
    with app.app_context():
        assert User.query.filter_by(username='newuser').first() is not None

def test_login_logout(client, auth):
    """Test login and logout flow."""
    # 1. Register first
    auth.register()

    # 2. Login
    response = auth.login()
    assert b"Login successful" in response.data

    # 3. Logout
    response = auth.logout()
    assert b"Logged out successfully" in response.data

def test_invalid_login(client, auth):
    """Test that wrong passwords fail."""
    auth.register()
    response = auth.login(password='wrongpassword')
    assert b"Invalid username or password" in response.data
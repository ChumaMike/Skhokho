from app.models import NetworkContact

def test_add_network_asset(client, auth, app):
    """QA: Can we add a strategic contact?"""
    auth.register()
    auth.login()

    # 1. Add a Contact
    response = client.post('/network/dashboard', data={
        'name': 'Bra Tshepo',
        'role': 'Investor',
        'phone': '0721234567',
        'email': 'tshepo@kasi.com'
    }, follow_redirects=True)

    # 2. Check Success Message
    assert b"Bra Tshepo" in response.data
    
    # 3. Verify Database
    with app.app_context():
        contact = NetworkContact.query.filter_by(name="Bra Tshepo").first()
        assert contact is not None
        assert contact.role == "Investor"

def test_network_privacy(client, auth, app):
    """QA: Ensure I cannot see other people's contacts."""
    # 1. User A adds a contact
    auth.register(username="userA", password="password")
    auth.login(username="userA", password="password")
    client.post('/network/add', data={'name': 'Secret Contact'})
    auth.logout()

    # 2. User B logs in
    auth.register(username="userB", password="password")
    auth.login(username="userB", password="password")

    # 3. User B views Network
    response = client.get('/network/')
    
    # 4. Should NOT see User A's contact
    assert b"Secret Contact" not in response.data
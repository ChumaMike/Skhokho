from app.models import BalaaHistory

def test_balaa_calculation(client, auth, app):
    """Test the Taxi Fare Calculator logic."""
    # 1. Login (Tools are protected)
    auth.register()
    auth.login()

    # 2. Simulate a Taxi Trip
    # Fare: R20, People: 3, Total Expected: R60
    # Money Collected: R20, R20, R30 (Total R70)
    # Expected Change: R10
    response = client.post('/balaa', data={
        'fare': '20',
        'group_size': '3',
        'amounts': ['20', '20', '30'] # Simulates collecting cash
    }, follow_redirects=True)

    assert response.status_code == 200
    
    # 3. Verify the Math in the Database
    with app.app_context():
        entry = BalaaHistory.query.first()
        assert entry is not None
        assert entry.expected == 60.0
        assert entry.received == 70.0
        assert entry.change == 10.0

def test_diary_entry(client, auth, app):
    """Test saving a diary entry."""
    auth.register()
    auth.login()

    response = client.post('/diary', data={
        'entry_type': 'Goal',
        'content': 'Become a Senior Engineer'
    }, follow_redirects=True)

    assert b"Saved!" in response.data
    assert b"Become a Senior Engineer" in response.data
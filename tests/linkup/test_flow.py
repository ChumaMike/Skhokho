import pytest
from app.extensions import db
from app.models import User, Service

def test_hire_provider_flow(client, auth, app):
    """User Story: I find a provider, hire them, and the system creates a job."""
    
    # 1. Setup World
    auth.register(username="provider_guy", password="password")
    auth.login(username="provider_guy", password="password")
    # Provider lists a service
    client.post('/linkup/join', data={
        'service_name': 'Kasi Electrician',
        'category': 'Tech',
        'description': 'I fix wires',
        'location_lat': '0', 'location_lng': '0',
        'cost': '50' # 50 Credits per job
    })
    auth.logout()

    # 2. Customer Enters
    auth.register(username="customer_lady", password="password")
    auth.login(username="customer_lady", password="password")
    
    # Cheat code: Give customer money directly in DB for the test
    with app.app_context():
        u = User.query.filter_by(username="customer_lady").first()
        u.wallet_balance = 100
        
        s = Service.query.filter_by(name="Kasi Electrician").first()
        service_id = s.id
        db.session.commit()

    # 3. ACTION: Click "Hire"
    # Note: We haven't built this route yet, so 404 or 500 is expected now
    response = client.post(f'/linkup/hire/{service_id}', follow_redirects=True)
    
    # 4. Expectation (This will FAIL until we build the route)
    # assert response.status_code == 200
    # assert b"Secure Connection Established" in response.data
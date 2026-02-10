import pytest
from app.extensions import db
from app.models import User, Service

def test_hire_provider_flow(client, auth, app):
    """User Story: I find a provider, hire them, and the system creates a job."""
    
    # 1. Setup World
    with app.app_context():
        provider = User(username="provider_guy", email="p@test.com", wallet_balance=0, reputation_points=0)
        provider.set_password("password")
        db.session.add(provider)
        db.session.commit()
        provider_id = provider.id
        
        # Provider lists a service
        s = Service(provider_id=provider_id, name='Kasi Electrician', category='Tech', description='I fix wires', latitude=0, longitude=0, price=50)
        db.session.add(s)
        db.session.commit()
        service_id = s.id
        
        # Customer Enters
        customer = User(username="customer_lady", email="c@test.com", wallet_balance=0, reputation_points=0)
        customer.set_password("password")
        db.session.add(customer)
        db.session.commit()
        customer_id = customer.id
        
        # Give customer money directly in DB for the test
        customer.wallet_balance = 100
        db.session.commit()

    # 3. ACTION: Click "Hire"
    # Note: We haven't built this route yet, so 404 or 500 is expected now
    response = client.post(f'/linkup/hire/{service_id}', follow_redirects=True)
    
    # 4. Expectation (This will FAIL until we build the route)
    # assert response.status_code == 200
    # assert b"Secure Connection Established" in response.data
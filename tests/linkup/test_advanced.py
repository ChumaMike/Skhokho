import pytest
from app.extensions import db
from app.models import User, Service, Job


def test_wallet_logic(client, auth, app):
    """QA: Can a user earn and hold credits?"""
    with app.app_context():
        u = User(username="citizen_one", email="citizen@example.com", wallet_balance=0, reputation_points=0)
        u.set_password("password")
        db.session.add(u)
        db.session.commit()
        u_id = u.id
        
        u.wallet_balance += 50
        db.session.commit()
        
        # Verify
        saved = db.session.get(User, u_id)
        assert saved.wallet_balance == 50


def test_hiring_flow_escrow(client, auth, app):
    """QA: Does hiring someone lock the credits correctly?"""
    # 1. Setup
    with app.app_context():
        p = User(username="test_plumber", email="p@test.com", password_hash="x", wallet_balance=0)
        p.set_password("x")
        c = User(username="test_customer", email="c@test.com", password_hash="x", wallet_balance=200)
        c.set_password("x")
        
        db.session.add(p)
        db.session.add(c)
        db.session.commit() # Commit users to generate IDs
        
        # Capture IDs dynamically
        p_id = p.id
        c_id = c.id
        
        s = Service(provider_id=p_id, name="Test Plumber", category="Plumbing", price=100, latitude=0.0, longitude=0.0)
        db.session.add(s)
        db.session.commit()
        s_id = s.id

    # 2. Bypass auth fixture and set session directly
    with client.session_transaction() as session:
        session['_user_id'] = str(c_id)
        session['_fresh'] = True
        print(f"Session variables: {session}")

    # 3. Hire
    response = client.post(f'/linkup/hire/{s_id}', follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Secure Comms" in response.data

    # 4. Verify
    with app.app_context():
        c_saved = db.session.get(User, c_id)
        assert c_saved.wallet_balance == 100


def test_secure_chat_creation(client, auth, app):
    """QA: Is a private chat log created for the job?"""
    # 1. Setup - Create user, service, and job directly in test context
    with app.app_context():
        u = User(username="chatty", email="chat@k.com")
        u.set_password("x")
        db.session.add(u)
        db.session.commit()
        u_id = u.id
        
        # Create a service first
        s = Service(provider_id=u_id, name="Test Service", category="Testing", price=50, latitude=0.0, longitude=0.0)
        db.session.add(s)
        db.session.commit()
        s_id = s.id

        job = Job(client_id=u_id, provider_id=u_id, service_id=s_id, status="In_Progress", price=50)
        db.session.add(job)
        db.session.commit()
        job_id = job.id

        # 2. Action - Send chat without redirect
        # We'll directly call the send_chat route without login to avoid session issues
        with client.session_transaction() as session:
            session['_user_id'] = str(u_id)
            session['_fresh'] = True
        response = client.post('/linkup/chat/send', data={
            'job_id': job_id,
            'message': 'Hola testing'
        }, follow_redirects=False)

        assert response.status_code == 302  # Should redirect to job chat

        # 3. Verify chat message
        job = db.session.get(Job, job_id)
        assert job is not None
        assert any(msg.message == 'Hola testing' for msg in job.messages)

import pytest
from app.extensions import db
from app.models import User, Service, Job

def test_wallet_logic(client, auth, app):
    """QA: Can a user earn and hold credits?"""
    auth.register(username="citizen_one", password="password")
    
    with app.app_context():
        # Dynamic ID: Get whatever ID was assigned
        u = User.query.filter_by(username="citizen_one").first()
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
        p = User(username="plumber", email="p@kasi.com", password_hash="x", wallet_balance=0)
        p.set_password("x")
        c = User(username="rich_customer", email="c@kasi.com", password_hash="x", wallet_balance=200)
        c.set_password("x")
        
        db.session.add(p)
        db.session.add(c)
        db.session.commit() # Commit users to generate IDs
        
        # Capture IDs dynamically
        p_id = p.id
        c_id = c.id
        
        s = Service(user_id=p_id, name="Kasi Plumber", cost=100)
        db.session.add(s)
        db.session.commit()
        s_id = s.id

    # 2. Login
    auth.login(username="rich_customer", password="x")
    
    # 3. Hire
    response = client.post(f'/linkup/hire/{s_id}', follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Job" in response.data

    # 4. Verify
    with app.app_context():
        c_saved = db.session.get(User, c_id)
        assert c_saved.wallet_balance == 100

def test_secure_chat_creation(client, auth, app):
    """QA: Is a private chat log created for the job?"""
    # 1. Setup
    with app.app_context():
        u = User(username="chatty", email="chat@k.com")
        u.set_password("x")
        db.session.add(u)
        db.session.commit() # ✅ CRITICAL FIX: Commit User FIRST so ID exists
        
        u_id = u.id # Capture the real ID
        
        job = Job(customer_id=u_id, provider_id=u_id, status="In_Progress")
        db.session.add(job)
        db.session.commit()
        
        job_id = job.id

    # 2. Action
    auth.login(username="chatty", password="x")
    
    client.post('/linkup/chat/send', data={
        'job_id': job_id,
        'message': 'Hola testing'
    }, follow_redirects=True)

    # 3. Verify
    response = client.get(f'/linkup/job/{job_id}', follow_redirects=True)
    assert b"Hola testing" in response.data
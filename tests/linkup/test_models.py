import pytest
from app.extensions import db
from app.models import User, Job, JobChat

def test_wallet_mechanics(app):
    with app.app_context():
        u = User(username="wallet_tester", email="w@test.com", password_hash="x", wallet_balance=0)
        db.session.add(u)
        db.session.commit()
        
        u.wallet_balance += 100
        db.session.commit()
        
        saved = db.session.get(User, u.id)
        assert saved.wallet_balance == 100

def test_job_escrow_logic(app):
    with app.app_context():
        p = User(username="escrow_provider", email="ep@test.com", password_hash="x", wallet_balance=0)
        c = User(username="escrow_customer", email="ec@test.com", password_hash="x", wallet_balance=200)
        db.session.add_all([p, c])
        db.session.commit()
        
        job = Job(customer_id=c.id, provider_id=p.id, status="In_Progress", agreed_price=50)
        db.session.add(job)
        
        # Simulate logic
        c.wallet_balance -= job.agreed_price
        db.session.commit()
        
        assert c.wallet_balance == 150
        assert p.wallet_balance == 0

def test_chat_ownership(app):
    with app.app_context():
        u1 = User(username="chat_u1", email="c1@test.com", password_hash="x")
        u2 = User(username="chat_u2", email="c2@test.com", password_hash="x")
        db.session.add_all([u1, u2])
        db.session.commit()

        job = Job(customer_id=u1.id, provider_id=u2.id, status="Open")
        db.session.add(job)
        db.session.commit()
        
        msg = JobChat(job_id=job.id, sender_id=u1.id, message="Test msg")
        db.session.add(msg)
        db.session.commit()
        
        saved = db.session.get(JobChat, msg.id)
        assert saved.job_id == job.id
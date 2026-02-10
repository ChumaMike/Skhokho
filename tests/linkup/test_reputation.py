import pytest
from datetime import datetime
from app.extensions import db
from app.models import User, Service, Job, Review

class TestReputationSystem:
    """QA: Do ratings affect user reputation points?"""
    
    def test_provider_reputation_increases(self, client, auth, app):
        """Provider should gain reputation points from good ratings"""
        with app.app_context():
            p = User(username="gardener", email="garden@test.com")
            p.set_password("test123")
            p.reputation_points = 10
            
            c = User(username="yard", email="yard@test.com")
            c.set_password("test123")
            
            db.session.add(p)
            db.session.add(c)
            db.session.commit()
            p_id = p.id
            c_id = c.id
            
            s = Service(user_id=p_id, name="Gardening", cost=60)
            db.session.add(s)
            db.session.commit()
            
            job = Job(
                customer_id=c_id,
                provider_id=p_id,
                service_id=s.id,
                status="Completed",
                agreed_price=60,
                completed_at=datetime.utcnow()
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.id
        
        auth.login(username="yard", password="test123")
        client.post(
            f'/linkup/rate/{job_id}',
            data={'rating': '5', 'comment': 'Amazing!', 'role': 'provider'},
            follow_redirects=True
        )
        
        # Verify reputation increased
        with app.app_context():
            provider_after = db.session.get(User, p_id)
            assert provider_after.reputation_points > 10
import pytest
from datetime import datetime
from app.extensions import db
from app.models import User, Service, Job, Review

class TestRatingSystem:
    """QA: Can users rate each other after job completion?"""
    
    def test_customer_can_rate_provider(self, client, auth, app):
        """Customer should be able to rate the service provider"""
        with app.app_context():
            # Setup completed job
            p = User(username="carpenter", email="carp@test.com")
            p.set_password("test123")
            c = User(username="renter", email="renter@test.com")
            c.set_password("test123")
            
            db.session.add(p)
            db.session.add(c)
            db.session.commit()
            
            p_id = p.id
            c_id = c.id
            
            s = Service(user_id=p_id, name="Furniture", cost=50)
            db.session.add(s)
            db.session.commit()
            
            job = Job(
                customer_id=c_id,
                provider_id=p_id,
                service_id=s.id,
                status="Completed",
                agreed_price=50,
                is_paid=True,
                completed_at=datetime.utcnow()
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.id
        
        # Customer rates provider
        auth.login(username="renter", password="test123")
        
        response = client.post(
            f'/linkup/rate/{job_id}',
            data={
                'rating': '5',
                'comment': 'Excellent work!',
                'role': 'provider'
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        
        # Verify review created
        with app.app_context():
            review = Review.query.filter_by(job_id=job_id).first()
            assert review.rating == 5
            assert review.reviewee_id == p_id
            assert review.reviewer_id == c_id
    
    def test_cannot_rate_before_job_completion(self, client, auth, app):
        """Users should not be able to rate incomplete jobs"""
        with app.app_context():
            p = User(username="tech", email="tech@test.com")
            p.set_password("test123")
            c = User(username="user", email="user@test.com")
            c.set_password("test123")
            
            db.session.add(p)
            db.session.add(c)
            db.session.commit()
            
            job = Job(
                customer_id=c.id,
                provider_id=p.id,
                status="In_Progress",  # Not completed!
                agreed_price=50
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.id
        
        auth.login(username="user", password="test123")
        
        client.post(
            f'/linkup/rate/{job_id}',
            data={'rating': '5', 'role': 'provider'},
            follow_redirects=True
        )
        
        # Should fail - no review created
        with app.app_context():
            review_count = Review.query.filter_by(job_id=job_id).count()
            assert review_count == 0
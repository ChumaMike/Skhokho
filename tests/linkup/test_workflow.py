import pytest
from app.extensions import db
from app.models import User, Service, Job, JobChat, Review

class TestEndToEndWorkflow:
    """QA: Does the complete gig workflow function correctly?"""
    
    def test_full_gig_lifecycle(self, client, auth, app):
        """Complete test: Post service → Hire → Chat → Complete → Rate"""
        with app.app_context():
            # 1. Create users
            provider = User(username="freelancer", email="free@test.com")
            provider.set_password("test123")
            provider.wallet_balance = 0
            
            customer = User(username="buyer", email="buyer@test.com")
            customer.set_password("test123")
            customer.wallet_balance = 200
            
            db.session.add(provider)
            db.session.add(customer)
            db.session.commit()
            
            p_id = provider.id
            c_id = customer.id
            
            # 2. Provider posts service
            service = Service(user_id=p_id, name="Logo Design", cost=80)
            db.session.add(service)
            db.session.commit()
            s_id = service.id
            
            # 3. Customer hires (escrow deducted)
            customer.wallet_balance -= 80
            
            job = Job(
                customer_id=c_id,
                provider_id=p_id,
                service_id=s_id,
                status="In_Progress",
                agreed_price=80,
                is_paid=False
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.id
            
            # 4. Chat exchange
            chat1 = JobChat(job_id=job_id, sender_id=c_id, message="Hi!")
            chat2 = JobChat(job_id=job_id, sender_id=p_id, message="Hello!")
            db.session.add(chat1)
            db.session.add(chat2)
            db.session.commit()
        
        # 5. Customer completes job
        auth.login(username="buyer", password="test123")
        client.post(f'/linkup/complete/{job_id}', follow_redirects=True)
        
        # 6. Both parties rate
        client.post(
            f'/linkup/rate/{job_id}',
            data={'rating': '5', 'comment': 'Great work!', 'role': 'provider'}
        )
        
        auth.logout()
        auth.login(username="freelancer", password="test123")
        client.post(
            f'/linkup/rate/{job_id}',
            data={'rating': '5', 'comment': 'Good client!', 'role': 'customer'}
        )
        
        # 7. Verify final state
        with app.app_context():
            final_job = db.session.get(Job, job_id)
            assert final_job.status == "Completed"
            
            final_provider = db.session.get(User, p_id)
            assert final_provider.wallet_balance == 80
            assert final_provider.reputation_points > 0
            
            reviews = Review.query.filter_by(job_id=job_id).count()
            assert reviews == 2
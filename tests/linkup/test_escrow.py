import pytest
from app.extensions import db
from app.models import User, Service, Job, Transaction

class TestEscrowCompletion:
    """QA: Can a customer mark a job as complete and release payment?"""
    
    def test_customer_can_complete_job(self, client, auth, app):
        """Customer should be able to mark job as completed"""
        with app.app_context():
            # Setup: Create provider, customer, service, and job
            provider = User(username="plumber_pro", email="plumber@test.com")
            provider.set_password("test123")
            provider.wallet_balance = 0
            
            customer = User(username="home_owner", email="customer@test.com")
            customer.set_password("test123")
            customer.wallet_balance = 200
            
            db.session.add(provider)
            db.session.add(customer)
            db.session.commit()
            
            # Capture IDs
            p_id = provider.id
            c_id = customer.id
            
            service = Service(user_id=p_id, name="Emergency Plumbing", cost=100)
            db.session.add(service)
            db.session.commit()
            
            # Create job with escrow
            job = Job(
                customer_id=c_id,
                provider_id=p_id,
                service_id=service.id,
                status="In_Progress",
                agreed_price=100,
                is_paid=False
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.id
            
            # Deduct from customer (simulate hiring)
            customer.wallet_balance -= 100
            db.session.commit()
        
        # Login as customer and complete job
        auth.login(username="home_owner", password="test123")
        
        response = client.post(f'/linkup/complete/{job_id}', follow_redirects=True)
        assert response.status_code == 200
        
        # Verify job status updated
        with app.app_context():
            completed_job = db.session.get(Job, job_id)
            assert completed_job.status == "Completed"
            assert completed_job.is_paid == True
            assert completed_job.completed_at is not None
    
    def test_payment_released_to_provider_on_completion(self, client, auth, app):
        """Provider should receive payment when job is completed"""
        with app.app_context():
            # Setup
            provider = User(username="electrician", email="elec@test.com")
            provider.set_password("test123")
            provider.wallet_balance = 50
            
            customer = User(username="client", email="client@test.com")
            customer.set_password("test123")
            customer.wallet_balance = 150
            
            db.session.add(provider)
            db.session.add(customer)
            db.session.commit()
            
            p_id = provider.id
            c_id = customer.id
            
            service = Service(user_id=p_id, name="Wiring", cost=75)
            db.session.add(service)
            db.session.commit()
            
            job = Job(
                customer_id=c_id,
                provider_id=p_id,
                service_id=service.id,
                status="In_Progress",
                agreed_price=75,
                is_paid=False
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.id
            
            # Deduct escrow from customer
            customer.wallet_balance -= 75
            db.session.commit()
        
        # Complete job
        auth.login(username="client", password="test123")
        client.post(f'/linkup/complete/{job_id}', follow_redirects=True)
        
        # Verify payment released
        with app.app_context():
            provider_after = db.session.get(User, p_id)
            assert provider_after.wallet_balance == 125  # 50 + 75
            
            # Verify transaction record created
            transaction = Transaction.query.filter_by(
                user_id=p_id,
                transaction_type="Earning"
            ).first()
            assert transaction is not None
            assert transaction.amount == 75
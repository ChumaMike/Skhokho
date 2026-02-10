"""
Phase 2: Advanced Features - Escrow Completion & Rating System
Test-Driven Development (TDD) Approach

This module tests:
- Job completion flow
- Escrow payment release
- Rating system (customer rates provider, provider rates customer)
- Reputation points calculation
"""

import pytest
from datetime import datetime
from app.extensions import db
from app.models import User, Service, Job, JobChat, Review, Transaction


# =============================================================================
# ESCROW COMPLETION TESTS
# =============================================================================

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
            
            provider_id = provider.id
            customer_id = customer.id
            
            service = Service(
                user_id=provider_id,
                name="Emergency Plumbing",
                cost=100
            )
            db.session.add(service)
            db.session.commit()
            service_id = service.id
            
            # Create job with escrow
            job = Job(
                customer_id=customer_id,
                provider_id=provider_id,
                service_id=service_id,
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
        
        response = client.post(
            f'/linkup/complete/{job_id}',
            follow_redirects=True
        )
        
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
            
            provider_id = provider.id
            customer_id = customer.id
            
            service = Service(user_id=provider_id, name="Wiring", cost=75)
            db.session.add(service)
            db.session.commit()
            
            job = Job(
                customer_id=customer_id,
                provider_id=provider_id,
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
            provider_after = db.session.get(User, provider_id)
            assert provider_after.wallet_balance == 125  # 50 + 75
            
            # Verify transaction record created
            transaction = Transaction.query.filter_by(
                user_id=provider_id,
                transaction_type="Earning"
            ).first()
            assert transaction is not None
            assert transaction.amount == 75


# =============================================================================
# RATING SYSTEM TESTS
# =============================================================================

class TestRatingSystem:
    """QA: Can users rate each other after job completion?"""
    
    def test_customer_can_rate_provider(self, client, auth, app):
        """Customer should be able to rate the service provider"""
        with app.app_context():
            # Setup completed job
            provider = User(username="carpenter", email="carp@test.com")
            provider.set_password("test123")
            
            customer = User(username="renter", email="renter@test.com")
            customer.set_password("test123")
            
            db.session.add(provider)
            db.session.add(customer)
            db.session.commit()
            
            provider_id = provider.id
            customer_id = customer.id
            
            service = Service(user_id=provider_id, name="Furniture", cost=50)
            db.session.add(service)
            db.session.commit()
            
            job = Job(
                customer_id=customer_id,
                provider_id=provider_id,
                service_id=service.id,
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
                'comment': 'Excellent work! Very professional.',
                'role': 'provider'  # Rating the provider
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        
        # Verify review created
        with app.app_context():
            review = Review.query.filter_by(job_id=job_id).first()
            assert review is not None
            assert review.rating == 5
            assert review.reviewee_id == provider_id
            assert review.reviewer_id == customer_id
    
    def test_provider_can_rate_customer(self, client, auth, app):
        """Provider should be able to rate the customer"""
        with app.app_context():
            provider = User(username="painter", email="paint@test.com")
            provider.set_password("test123")
            
            customer = User(username="home", email="home@test.com")
            customer.set_password("test123")
            
            db.session.add(provider)
            db.session.add(customer)
            db.session.commit()
            
            provider_id = provider.id
            customer_id = customer.id
            
            service = Service(user_id=provider_id, name="Painting", cost=100)
            db.session.add(service)
            db.session.commit()
            
            job = Job(
                customer_id=customer_id,
                provider_id=provider_id,
                service_id=service.id,
                status="Completed",
                agreed_price=100,
                is_paid=True,
                completed_at=datetime.utcnow()
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.id
        
        # Provider rates customer
        auth.login(username="painter", password="test123")
        
        response = client.post(
            f'/linkup/rate/{job_id}',
            data={
                'rating': '4',
                'comment': 'Good communication, prompt payment.',
                'role': 'customer'
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        
        with app.app_context():
            review = Review.query.filter_by(job_id=job_id, reviewer_id=provider_id).first()
            assert review is not None
            assert review.rating == 4
            assert review.reviewee_id == customer_id
    
    def test_cannot_rate_before_job_completion(self, client, auth, app):
        """Users should not be able to rate incomplete jobs"""
        with app.app_context():
            provider = User(username="tech", email="tech@test.com")
            provider.set_password("test123")
            
            customer = User(username="user", email="user@test.com")
            customer.set_password("test123")
            
            db.session.add(provider)
            db.session.add(customer)
            db.session.commit()
            
            job = Job(
                customer_id=customer.id,
                provider_id=provider.id,
                status="In_Progress",  # Not completed!
                agreed_price=50,
                is_paid=False
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.id
        
        auth.login(username="user", password="test123")
        
        response = client.post(
            f'/linkup/rate/{job_id}',
            data={'rating': '5', 'role': 'provider'},
            follow_redirects=True
        )
        
        # Should fail or redirect with error
        with app.app_context():
            review_count = Review.query.filter_by(job_id=job_id).count()
            assert review_count == 0


# =============================================================================
# REPUTATION SYSTEM TESTS
# =============================================================================

class TestReputationSystem:
    """QA: Do ratings affect user reputation points?"""
    
    def test_provider_reputation_increases_with_good_rating(self, client, auth, app):
        """Provider should gain reputation points from good ratings"""
        with app.app_context():
            provider = User(username="gardener", email="garden@test.com")
            provider.set_password("test123")
            provider.reputation_points = 10
            
            customer = User(username="yard", email="yard@test.com")
            customer.set_password("test123")
            
            db.session.add(provider)
            db.session.add(customer)
            db.session.commit()
            provider_id = provider.id
            customer_id = customer.id
            
            service = Service(user_id=provider_id, name="Gardening", cost=60)
            db.session.add(service)
            db.session.commit()
            
            job = Job(
                customer_id=customer_id,
                provider_id=provider_id,
                service_id=service.id,
                status="Completed",
                agreed_price=60,
                is_paid=True,
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
            provider_after = db.session.get(User, provider_id)
            assert provider_after.reputation_points > 10  # Should have increased
    
    def test_only_participants_can_rate(self, client, auth, app):
        """Only job participants should be able to rate"""
        with app.app_context():
            provider = User(username="pro", email="pro@test.com")
            provider.set_password("test123")
            
            customer = User(username="cli", email="cli@test.com")
            customer.set_password("test123")
            
            outsider = User(username="stranger", email="stranger@test.com")
            outsider.set_password("test123")
            
            db.session.add(provider)
            db.session.add(customer)
            db.session.add(outsider)
            db.session.commit()
            
            job = Job(
                customer_id=customer.id,
                provider_id=provider.id,
                status="Completed",
                agreed_price=50,
                is_paid=True,
                completed_at=datetime.utcnow()
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.id
        
        # Outsider tries to rate
        auth.login(username="stranger", password="test123")
        
        response = client.post(
            f'/linkup/rate/{job_id}',
            data={'rating': '1', 'role': 'provider'},
            follow_redirects=True
        )
        
        with app.app_context():
            review_count = Review.query.filter_by(job_id=job_id).count()
            assert review_count == 0


# =============================================================================
# END-TO-END WORKFLOW TESTS
# =============================================================================

class TestEndToEndWorkflow:
    """QA: Does the complete gig workflow function correctly?"""
    
    def test_full_gig_lifecycle(self, client, auth, app):
        """Complete test: Post service → Hire → Chat → Complete → Rate"""
        with app.app_context():
            # 1. Create users
            provider = User(username="freelancer", email="free@test.com")
            provider.set_password("test123")
            provider.wallet_balance = 0
            provider.reputation_points = 0
            
            customer = User(username="buyer", email="buyer@test.com")
            customer.set_password("test123")
            customer.wallet_balance = 200
            
            db.session.add(provider)
            db.session.add(customer)
            db.session.commit()
            
            provider_id = provider.id
            customer_id = customer.id
            
            # 2. Provider posts service
            service = Service(
                user_id=provider_id,
                name="Logo Design",
                category="Design",
                description="Professional logos",
                cost=80
            )
            db.session.add(service)
            db.session.commit()
            service_id = service.id
            
            # 3. Customer hires (escrow deducted)
            customer.wallet_balance -= 80
            
            job = Job(
                customer_id=customer_id,
                provider_id=provider_id,
                service_id=service_id,
                status="In_Progress",
                agreed_price=80,
                is_paid=False
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.id
            
            # 4. Chat exchange
            chat1 = JobChat(job_id=job_id, sender_id=customer_id, message="Hi, need a logo!")
            chat2 = JobChat(job_id=job_id, sender_id=provider_id, message="Got it, working on it.")
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
            assert final_job.is_paid == True
            
            final_provider = db.session.get(User, provider_id)
            assert final_provider.wallet_balance == 80
            assert final_provider.reputation_points > 0
            
            reviews = Review.query.filter_by(job_id=job_id).count()
            assert reviews == 2  # Both rated

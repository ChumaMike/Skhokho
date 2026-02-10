# Phase 2 Technical Specification: The Engagement Layer

## Executive Summary

This document outlines the implementation plan for Phase 2 of the Skhokho platform, focusing on three core modules:
- **Module A**: LinkUp Maturity (Gig Economy workflow, Reviews, Disputes)
- **Module B**: Civic Connect (Issue Reporting, Voting, Status Tracking)
- **Module C**: Map Interface (Geospatial data, Unified API endpoint)

**Constraint Compliance**: All database interactions will continue using the NullPool pattern. Phase 1 tests must remain passing.

---

## 1. MODEL CHANGES (app/models.py)

### 1.1 Module A: LinkUp Maturity

#### A.1 Enhanced Job Model
```python
class Job(db.Model):
    """The Contract between Customer and Provider - ENHANCED"""
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)
    
    # Status: 'Pending' -> 'In_Progress' -> 'Completed' -> 'Paid'
    # Additional: 'Disputed', 'Cancelled'
    status = db.Column(db.String(50), default='Pending')
    
    # 💰 Escrow Data
    agreed_price = db.Column(db.Integer, default=0)
    is_paid = db.Column(db.Boolean, default=False)
    
    # NEW: Timestamps for workflow tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)  # When status -> In_Progress
    completed_at = db.Column(db.DateTime, nullable=True)  # When status -> Completed
    paid_at = db.Column(db.DateTime, nullable=True)  # When is_paid -> True
    
    # NEW: Relationships
    messages = db.relationship('JobChat', backref='job', lazy=True)
    reviews = db.relationship('Review', backref='job', lazy=True)
    disputes = db.relationship('Dispute', backref='job', lazy=True)
```

#### A.2 New Review Model
```python
class Review(db.Model):
    """Rating and feedback system for completed jobs"""
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Rating: 1-5 stars
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text, nullable=True)
    
    # Role context: 'provider' (customer rating provider) or 'customer' (provider rating customer)
    role_rated = db.Column(db.String(20), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # NEW: Ensure one review per role per job
    __table_args__ = (
        db.UniqueConstraint('job_id', 'reviewer_id', name='unique_review_per_user_per_job'),
    )
```

#### A.3 New Dispute Model
```python
class Dispute(db.Model):
    """Simple dispute flagging system for problematic jobs"""
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    raised_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Dispute details
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Open')  # 'Open', 'Under_Review', 'Resolved', 'Rejected'
    
    # Resolution
    resolution_notes = db.Column(db.Text, nullable=True)
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
```

### 1.2 Module B: Civic Connect

#### B.1 New CivicIssue Model (Replaces/Enhances CivicTicket)
```python
class CivicIssue(db.Model):
    """Community-reported civic issues with voting and status tracking"""
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Issue details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)  # 'Pothole', 'Broken Light', 'Illegal Dumping', etc.
    
    # 📍 Geospatial Data
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    # 📊 Status Tracking: 'Reported' -> 'Under_Review' -> 'In_Progress' -> 'Resolved'
    status = db.Column(db.String(50), default='Reported')
    
    # 🗳️ Voting System
    upvote_count = db.Column(db.Integer, default=0)
    
    # 🔐 Verification
    image_url = db.Column(db.String(500), nullable=True)  # Photo evidence
    guardian_seal = db.Column(db.String(64), nullable=True)  # SHA-256 tamper-proof seal
    ai_risk_score = db.Column(db.Integer, default=0)  # 0-100 severity score
    
    # 👤 Admin tracking
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    votes = db.relationship('CivicIssueVote', backref='issue', lazy=True, cascade='all, delete-orphan')
```

#### B.2 New CivicIssueVote Model
```python
class CivicIssueVote(db.Model):
    """Upvote tracking for civic issues - one vote per user per issue"""
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('civic_issue.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one vote per user per issue
    __table_args__ = (
        db.UniqueConstraint('issue_id', 'user_id', name='unique_vote_per_user_per_issue'),
    )
```

### 1.3 Module C: Map Interface

#### C.1 Service Model Enhancement (Already has lat/lng - VERIFY ACCURACY)
```python
class Service(db.Model):
    # ... existing fields ...
    
    # ENSURE these fields exist and are properly typed
    latitude = db.Column(db.Float, nullable=True)  # -90 to 90
    longitude = db.Column(db.Float, nullable=True)  # -180 to 180
    
    # OPTIONAL: Add validation helper
    def has_valid_location(self):
        return (self.latitude is not None and 
                self.longitude is not None and
                -90 <= self.latitude <= 90 and
                -180 <= self.longitude <= 180)
```

#### C.2 User Model Enhancement (Optional - for reputation display)
```python
class User(db.Model):
    # ... existing fields ...
    
    # Relationships for new models
    reviews_given = db.relationship('Review', foreign_keys='Review.reviewer_id', backref='reviewer', lazy=True)
    reviews_received = db.relationship('Review', foreign_keys='Review.reviewee_id', backref='reviewee', lazy=True)
    disputes_raised = db.relationship('Dispute', foreign_keys='Dispute.raised_by_id', backref='dispute_raiser', lazy=True)
    civic_issues = db.relationship('CivicIssue', foreign_keys='CivicIssue.reporter_id', backref='reporter', lazy=True)
    civic_votes = db.relationship('CivicIssueVote', backref='voter', lazy=True)
```

### 1.4 Summary of Model Changes

| Model | Action | Purpose |
|-------|--------|---------|
| `Job` | MODIFY | Add `started_at`, `completed_at`, `paid_at` timestamps |
| `Review` | NEW | 1-5 star ratings with comments |
| `Dispute` | NEW | Flag problematic jobs |
| `CivicIssue` | NEW | Replace CivicTicket with enhanced issue tracking |
| `CivicIssueVote` | NEW | Upvote system for prioritization |
| `Service` | VERIFY | Confirm lat/lng fields exist |
| `User` | VERIFY | Confirm reputation_points exists |

---

## 2. API ENDPOINTS

### 2.1 Module A: LinkUp Routes (app/routes/linkup.py)

#### A.1 Job Workflow Endpoints
```python
# State Machine: Pending -> In Progress -> Completed -> Paid

@linkup_bp.route('/start/<int:job_id>', methods=['POST'])
@login_required
def start_job(job_id):
    """Provider accepts job: Pending -> In_Progress"""
    # Validation:
    # - Job exists and status is 'Pending'
    # - Current user is the provider
    # - Set started_at = datetime.utcnow()
    pass

@linkup_bp.route('/complete/<int:job_id>', methods=['POST'])
@login_required
def complete_job(job_id):
    """Customer marks job complete: In_Progress -> Completed
    
    This triggers:
    1. status = 'Completed'
    2. completed_at = datetime.utcnow()
    3. Release escrow: provider.wallet_balance += job.agreed_price
    4. is_paid = True
    5. paid_at = datetime.utcnow()
    6. Create Transaction record (type='Earning')
    7. Update provider reputation_points
    """
    pass

@linkup_bp.route('/cancel/<int:job_id>', methods=['POST'])
@login_required
def cancel_job(job_id):
    """Cancel job and refund escrow (if in Pending or In_Progress)"""
    # Validation:
    # - Job status allows cancellation
    # - User is either customer or provider
    # - Refund customer if escrow was deducted
    pass
```

#### A.2 Review System Endpoints
```python
@linkup_bp.route('/rate/<int:job_id>', methods=['POST'])
@login_required
def rate_job(job_id):
    """Leave a review for the other party
    
    Form data:
    - rating: 1-5 (integer)
    - comment: text (optional)
    - role: 'provider' or 'customer' (who you're rating)
    
    Validation:
    - Job status is 'Completed'
    - User is participant (customer or provider)
    - User hasn't already rated this job
    - Update reviewee's reputation_points
    """
    pass

@linkup_bp.route('/reviews/<int:user_id>')
def view_reviews(user_id):
    """View all reviews for a user"""
    # Return JSON or render template with review list
    pass
```

#### A.3 Dispute Handling Endpoints
```python
@linkup_bp.route('/dispute/<int:job_id>', methods=['POST'])
@login_required
def flag_dispute(job_id):
    """Flag a job as disputed
    
    Form data:
    - reason: text (required)
    
    Actions:
    - Create Dispute record
    - Change job status to 'Disputed'
    - Notify admin (future: via notification system)
    """
    pass

@linkup_bp.route('/dispute/<int:dispute_id>/resolve', methods=['POST'])
@login_required
def resolve_dispute(dispute_id):
    """Admin resolves a dispute (requires admin role)"""
    # Only accessible by users with role='admin'
    pass
```

### 2.2 Module B: Civic Routes (app/routes/civic.py)

#### B.1 Issue Reporting Endpoints
```python
@civic_bp.route('/issue', methods=['POST'])
@login_required
def report_issue():
    """Report a new civic issue
    
    Form data:
    - title: string (required)
    - description: text (required)
    - category: string (required) - 'Pothole', 'Broken Light', 'Illegal Dumping', etc.
    - latitude: float (required)
    - longitude: float (required)
    - image: file (optional)
    
    Actions:
    - Generate guardian_seal (SHA-256)
    - Get AI risk score (optional)
    - Create CivicIssue record
    - Auto-upvote by reporter
    """
    pass

@civic_bp.route('/issues')
def list_issues():
    """List all civic issues with filtering/sorting"""
    # Query params:
    # - status: filter by status
    # - category: filter by category
    # - sort: 'newest', 'most_voted', 'nearest' (requires lat/lng)
    pass

@civic_bp.route('/issue/<int:issue_id>')
def view_issue(issue_id):
    """View single issue details"""
    pass
```

#### B.2 Voting Endpoints
```python
@civic_bp.route('/issue/<int:issue_id>/upvote', methods=['POST'])
@login_required
def upvote_issue(issue_id):
    """Upvote a civic issue
    
    Validation:
    - User hasn't already upvoted
    - Increment upvote_count on issue
    - Create CivicIssueVote record
    """
    pass

@civic_bp.route('/issue/<int:issue_id>/unvote', methods=['POST'])
@login_required
def unvote_issue(issue_id):
    """Remove upvote from an issue"""
    pass
```

#### B.3 Status Tracking Endpoints
```python
@civic_bp.route('/issue/<int:issue_id>/status', methods=['POST'])
@login_required
def update_issue_status(issue_id):
    """Update issue status (admin/official only)
    
    Form data:
    - status: 'Reported', 'Under_Review', 'In_Progress', 'Resolved'
    - resolution_notes: text (optional)
    
    Validation:
    - User has role 'admin' or 'official'
    - If status='Resolved', set resolved_at
    """
    pass
```

### 2.3 Module C: Location/Map Routes (app/routes/location.py or api.py)

#### C.1 Unified Map Data Endpoint
```python
@location_bp.route('/api/map-data')
@login_required
def get_map_data():
    """Return geospatial data for frontend map visualization
    
    Query Parameters:
    - lat: center latitude (required)
    - lng: center longitude (required)
    - radius: search radius in meters (default: 5000)
    - types: comma-separated list of 'services', 'issues' (default: both)
    
    Returns JSON:
    {
        "services": [
            {
                "id": 1,
                "type": "service",
                "name": "Kasi Electrician",
                "category": "Technology",
                "latitude": -26.2309,
                "longitude": 27.8596,
                "cost": 50,
                "provider": "username"
            }
        ],
        "issues": [
            {
                "id": 1,
                "type": "issue",
                "title": "Big Pothole",
                "category": "Pothole",
                "latitude": -26.2310,
                "longitude": 27.8597,
                "status": "Reported",
                "upvotes": 5,
                "severity": 85
            }
        ],
        "center": {"lat": -26.2309, "lng": 27.8596},
        "radius": 5000
    }
    """
    pass
```

### 2.4 Summary of API Endpoints

| Route | Method | Description | Module |
|-------|--------|-------------|--------|
| `/linkup/start/<job_id>` | POST | Provider accepts job | A |
| `/linkup/complete/<job_id>` | POST | Customer completes, releases payment | A |
| `/linkup/cancel/<job_id>` | POST | Cancel job and refund | A |
| `/linkup/rate/<job_id>` | POST | Leave review | A |
| `/linkup/reviews/<user_id>` | GET | View user reviews | A |
| `/linkup/dispute/<job_id>` | POST | Flag dispute | A |
| `/linkup/dispute/<id>/resolve` | POST | Admin resolve dispute | A |
| `/civic/issue` | POST | Report new issue | B |
| `/civic/issues` | GET | List all issues | B |
| `/civic/issue/<id>` | GET | View issue details | B |
| `/civic/issue/<id>/upvote` | POST | Upvote issue | B |
| `/civic/issue/<id>/unvote` | POST | Remove upvote | B |
| `/civic/issue/<id>/status` | POST | Update status (admin) | B |
| `/api/map-data` | GET | Get services + issues for map | C |

---

## 3. TEST PLAN

### 3.1 Module A: LinkUp Maturity Tests

Create/Update `tests/linkup/test_phase2.py`:

```python
# =============================================================================
# JOB WORKFLOW STATE MACHINE TESTS
# =============================================================================

class TestJobWorkflow:
    """QA: Does the job state machine work correctly?"""
    
    def test_pending_to_in_progress_transition(self, client, auth, app):
        """Provider can accept a pending job"""
        # Setup: Create job with status='Pending'
        # Provider posts to /linkup/start/<job_id>
        # Assert: status='In_Progress', started_at is set
        pass
    
    def test_in_progress_to_completed_transition(self, client, auth, app):
        """Customer can mark job as completed"""
        # Setup: Job with status='In_Progress'
        # Customer posts to /linkup/complete/<job_id>
        # Assert: status='Completed', completed_at is set, is_paid=True
        pass
    
    def test_unauthorized_status_changes_blocked(self, client, auth, app):
        """Only appropriate roles can change status"""
        # Test: Customer cannot call start_job
        # Test: Provider cannot call complete_job
        # Test: Outsider cannot modify job
        pass

# =============================================================================
# ESCROW & PAYMENT TESTS
# =============================================================================

class TestEscrowPayment:
    """QA: Is payment released correctly on completion?"""
    
    def test_payment_released_on_completion(self, client, auth, app):
        """Provider receives payment when job completed"""
        # Setup: Job with escrow deducted
        # Complete job
        # Assert: Provider wallet_balance increased, Transaction created
        pass
    
    def test_refund_on_cancellation(self, client, auth, app):
        """Customer gets refund if job cancelled"""
        # Setup: Job with escrow deducted
        # Cancel job
        # Assert: Customer wallet_balance restored
        pass

# =============================================================================
# REVIEW SYSTEM TESTS
# =============================================================================

class TestReviewSystem:
    """QA: Can users rate each other after job completion?"""
    
    def test_customer_can_rate_provider(self, client, auth, app):
        """Customer rates provider after completed job"""
        # Setup: Completed job
        # Customer posts rating=5, comment='Great!', role='provider'
        # Assert: Review created, provider reputation increased
        pass
    
    def test_provider_can_rate_customer(self, client, auth, app):
        """Provider rates customer after completed job"""
        # Similar to above, reversed roles
        pass
    
    def test_cannot_rate_before_completion(self, client, auth, app):
        """Rating blocked for incomplete jobs"""
        # Setup: In_Progress job
        # Attempt to rate
        # Assert: No review created, error message
        pass
    
    def test_cannot_rate_twice(self, client, auth, app):
        """One review per user per job"""
        # Rate once successfully
        # Attempt second rating
        # Assert: Blocked or updates existing
        pass
    
    def test_only_participants_can_rate(self, client, auth, app):
        """Outsiders cannot rate a job"""
        # Setup: Completed job
        # Third user attempts to rate
        # Assert: Blocked
        pass
    
    def test_rating_affects_reputation(self, client, auth, app):
        """5-star rating increases reputation more than 3-star"""
        # Test reputation calculation formula
        pass

# =============================================================================
# DISPUTE HANDLING TESTS
# =============================================================================

class TestDisputeHandling:
    """QA: Can users flag disputes?"""
    
    def test_customer_can_flag_dispute(self, client, auth, app):
        """Customer can flag a problematic job"""
        # Setup: In_Progress job
        # Post to /linkup/dispute/<job_id> with reason
        # Assert: Dispute created, job status='Disputed'
        pass
    
    def test_provider_can_flag_dispute(self, client, auth, app):
        """Provider can also flag disputes"""
        pass
    
    def test_dispute_blocks_payment(self, client, auth, app):
        """Disputed job cannot be completed/paid"""
        # Setup: Disputed job
        # Attempt to complete
        # Assert: Blocked
        pass
    
    def test_admin_can_resolve_dispute(self, client, auth, app):
        """Admin can resolve disputes"""
        # Setup: Dispute with admin user
        # Post resolution
        # Assert: Dispute status='Resolved'
        pass
```

### 3.2 Module B: Civic Connect Tests

Create `tests/civic/test_civic.py`:

```python
# =============================================================================
# ISSUE REPORTING TESTS
# =============================================================================

class TestIssueReporting:
    """QA: Can users report civic issues?"""
    
    def test_report_pothole(self, client, auth, app):
        """User can report a pothole issue"""
        # Login
        # POST /civic/issue with title, description, category='Pothole', lat, lng
        # Assert: CivicIssue created, status='Reported', guardian_seal present
        pass
    
    def test_report_broken_light(self, client, auth, app):
        """User can report broken street light"""
        # Similar with category='Broken Light'
        pass
    
    def test_report_requires_location(self, client, auth, app):
        """Issue requires valid lat/lng"""
        # Post without coordinates
        # Assert: Error, no issue created
        pass
    
    def test_guardian_seal_generated(self, client, auth, app):
        """Each issue gets a tamper-proof seal"""
        # Create issue
        # Assert: guardian_seal is SHA-256 hash (64 chars)
        pass

# =============================================================================
# VOTING SYSTEM TESTS
# =============================================================================

class TestVotingSystem:
    """QA: Can users upvote issues?"""
    
    def test_upvote_increases_count(self, client, auth, app):
        """Upvoting increments upvote_count"""
        # Setup: Existing issue
        # POST /civic/issue/<id>/upvote
        # Assert: upvote_count=1, CivicIssueVote record exists
        pass
    
    def test_cannot_upvote_twice(self, client, auth, app):
        """One vote per user per issue"""
        # Upvote once
        # Upvote again
        # Assert: Still only 1 vote, error or ignored
        pass
    
    def test_unvote_decreases_count(self, client, auth, app):
        """User can remove their upvote"""
        # Upvote
        # POST /civic/issue/<id>/unvote
        # Assert: upvote_count=0, vote record deleted
        pass
    
    def test_issues_sorted_by_votes(self, client, auth, app):
        """Most voted issues appear first when sorted"""
        # Create 2 issues
        # Upvote one multiple times
        # GET /civic/issues?sort=most_voted
        # Assert: Highly voted issue first
        pass

# =============================================================================
# STATUS TRACKING TESTS
# =============================================================================

class TestStatusTracking:
    """QA: Can officials update issue status?"""
    
    def test_admin_can_update_status(self, client, auth, app):
        """Admin can mark issue as resolved"""
        # Setup: admin user, reported issue
        # POST /civic/issue/<id>/status with status='Resolved'
        # Assert: Issue status updated, resolved_at set
        pass
    
    def test_citizen_cannot_update_status(self, client, auth, app):
        """Regular users cannot change status"""
        # Setup: regular user, reported issue
        # Attempt status update
        # Assert: Blocked, status unchanged
        pass
    
    def test_status_workflow(self, client, auth, app):
        """Full status lifecycle: Reported -> Under_Review -> In_Progress -> Resolved"""
        # Test each transition
        pass
```

### 3.3 Module C: Map Interface Tests

Create `tests/location/test_map_data.py`:

```python
# =============================================================================
# MAP DATA API TESTS
# =============================================================================

class TestMapDataAPI:
    """QA: Does /api/map-data return correct geospatial data?"""
    
    def test_map_data_returns_services(self, client, auth, app):
        """API returns services within radius"""
        # Setup: Service at lat=-26.23, lng=27.86
        # GET /api/map-data?lat=-26.23&lng=27.86&radius=1000
        # Assert: Service in response, correct format
        pass
    
    def test_map_data_returns_issues(self, client, auth, app):
        """API returns civic issues within radius"""
        # Setup: CivicIssue at nearby location
        # GET /api/map-data?lat=-26.23&lng=27.86&radius=1000
        # Assert: Issue in response
        pass
    
    def test_map_data_filters_by_type(self, client, auth, app):
        """Can filter to return only services or only issues"""
        # Setup: Both services and issues
        # GET /api/map-data?types=services
        # Assert: Only services returned
        pass
    
    def test_map_data_respects_radius(self, client, auth, app):
        """Items outside radius are excluded"""
        # Setup: Service at 10km away
        # GET with radius=5000 (5km)
        # Assert: Service not in results
        pass
    
    def test_map_data_requires_auth(self, client, app):
        """Endpoint requires login"""
        # GET without auth
        # Assert: 302 redirect to login or 401
        pass
    
    def test_map_data_json_structure(self, client, auth, app):
        """Response has expected JSON structure"""
        # Verify fields: id, type, name/title, lat, lng, etc.
        pass
```

### 3.4 Integration & End-to-End Tests

```python
# =============================================================================
# END-TO-END WORKFLOW TESTS
# =============================================================================

class TestFullGigLifecycle:
    """QA: Complete gig economy workflow"""
    
    def test_full_lifecycle(self, client, auth, app):
        """Provider posts → Customer hires → Chat → Complete → Rate"""
        # 1. Provider registers service
        # 2. Customer hires (escrow)
        # 3. Provider starts job
        # 4. Chat exchange
        # 5. Customer completes (payment released)
        # 6. Both rate each other
        # 7. Verify final state
        pass

class TestCivicWorkflow:
    """QA: Complete civic issue workflow"""
    
    def test_full_issue_lifecycle(self, client, auth, app):
        """Report → Upvotes → Status updates → Resolved"""
        # 1. User reports issue
        # 2. Multiple users upvote
        # 3. Admin marks in progress
        # 4. Admin marks resolved
        pass
```

### 3.5 Test Coverage Summary

| Test Category | Tests | File |
|---------------|-------|------|
| Job Workflow | 4 tests | tests/linkup/test_phase2.py |
| Escrow & Payment | 2 tests | tests/linkup/test_phase2.py |
| Review System | 6 tests | tests/linkup/test_phase2.py |
| Dispute Handling | 4 tests | tests/linkup/test_phase2.py |
| Issue Reporting | 4 tests | tests/civic/test_civic.py |
| Voting System | 4 tests | tests/civic/test_civic.py |
| Status Tracking | 3 tests | tests/civic/test_civic.py |
| Map Data API | 6 tests | tests/location/test_map_data.py |
| E2E Workflows | 2 tests | tests/ (appropriate files) |

---

## 4. IMPLEMENTATION ORDER

### Phase 2A: Models & Foundation (Week 1)
1. Create `Review` model
2. Create `Dispute` model  
3. Create `CivicIssue` model
4. Create `CivicIssueVote` model
5. Modify `Job` model (add timestamps)
6. Run migrations
7. Write model tests

### Phase 2B: LinkUp Maturity (Week 1-2)
1. Implement job state machine routes
2. Implement escrow release on completion
3. Implement review system
4. Implement dispute flagging
5. Write Phase 2 LinkUp tests

### Phase 2C: Civic Connect (Week 2)
1. Implement issue reporting
2. Implement voting system
3. Implement status tracking
4. Write Civic tests

### Phase 2D: Map Interface (Week 2-3)
1. Verify geospatial fields on Service
2. Create /api/map-data endpoint
3. Implement radius-based querying
4. Write Map API tests
5. Full integration testing

---

## 5. CONSTRAINTS & CONSIDERATIONS

### 5.1 NullPool Compliance
- All database connections must use NullPool (already configured in conftest.py)
- No long-lived sessions outside request context
- Use `db.session.remove()` appropriately

### 5.2 Backward Compatibility
- Existing Phase 1 tests must pass
- Do not remove existing models (CivicTicket can coexist with CivicIssue initially)
- Maintain existing route signatures where possible

### 5.3 Security
- Verify user permissions before state changes
- Validate all form inputs
- Ensure only participants can view/modify jobs
- Admin routes require role check

### 5.4 Data Integrity
- Use database constraints (UniqueConstraint) for votes and reviews
- Validate latitude (-90 to 90) and longitude (-180 to 180)
- Ensure reputation calculation is consistent

---

## 6. APPENDIX: Sample Test Patterns

### Using NullPool in Tests (from conftest.py)
```python
@pytest.fixture(scope='function', autouse=True)
def clean_db(app):
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
    yield
    with app.app_context():
        db.session.remove()
```

### Creating Test Data Pattern
```python
with app.app_context():
    provider = User(username="pro", email="p@test.com")
    provider.set_password("test")
    db.session.add(provider)
    db.session.commit()
    provider_id = provider.id  # Capture ID before session closes
```

### Making Authenticated Requests
```python
auth.login(username="customer", password="test123")
response = client.post(f'/linkup/complete/{job_id}', follow_redirects=True)
assert response.status_code == 200
```

---

## 7. ACCEPTANCE CRITERIA

### Module A: LinkUp Maturity
- [ ] Job can transition: Pending → In_Progress → Completed → Paid
- [ ] Customer can rate provider (1-5 stars) after completion
- [ ] Provider can rate customer after completion
- [ ] Dispute can be flagged by either party
- [ ] Payment is held in escrow and released on completion
- [ ] Reputation points update based on ratings

### Module B: Civic Connect
- [ ] Users can report issues (Pothole, Broken Light, etc.)
- [ ] Each issue has lat/lng coordinates
- [ ] Users can upvote issues (one per user)
- [ ] Issues display upvote count
- [ ] Admins can update issue status
- [ ] Status history is tracked

### Module C: Map Interface
- [ ] Service model has valid lat/lng fields
- [ ] CivicIssue model has valid lat/lng fields
- [ ] `/api/map-data` returns JSON with services and issues
- [ ] API supports radius-based filtering
- [ ] API supports type filtering (services/issues)

### Quality Gates
- [ ] All new tests pass
- [ ] All Phase 1 tests still pass
- [ ] No database connection leaks (NullPool)
- [ ] Code follows existing patterns

---

**Document Version**: 1.0  
**Date**: 2026-02-10  
**Status**: Ready for Implementation Review
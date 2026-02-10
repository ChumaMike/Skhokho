from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    wallet_balance = db.Column(db.Integer, default=0)
    reputation_points = db.Column(db.Integer, default=0)
    role = db.Column(db.String(20), default='citizen')  # citizen, provider, official
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<User {self.username}>'


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    provider = db.relationship('User', backref=db.backref('services', lazy=True))

    def __repr__(self):
        return f'<Service {self.name}>'


class Job(db.Model):
    """The Contract between Customer and Provider - ENHANCED for Phase 2"""
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Status: 'Pending' -> 'In_Progress' -> 'Completed' -> 'Paid'
    # Additional: 'Disputed', 'Cancelled'
    status = db.Column(db.String(20), default='Pending')
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(200), nullable=True)
    
    # Escrow Data
    agreed_price = db.Column(db.Integer, default=0)
    is_paid = db.Column(db.Boolean, default=False)
    
    # Timestamps for workflow tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)  # When status -> In_Progress
    completed_at = db.Column(db.DateTime, nullable=True)  # When status -> Completed
    paid_at = db.Column(db.DateTime, nullable=True)  # When is_paid -> True

    service = db.relationship('Service', backref=db.backref('jobs', lazy=True))
    client = db.relationship('User', foreign_keys=[client_id], backref=db.backref('client_jobs', lazy=True))
    provider = db.relationship('User', foreign_keys=[provider_id], backref=db.backref('provider_jobs', lazy=True))

    def __repr__(self):
        return f'<Job {self.id}>'


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
    
    # Relationships
    job = db.relationship('Job', backref=db.backref('reviews', lazy=True))
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref=db.backref('reviews_given', lazy=True))
    reviewee = db.relationship('User', foreign_keys=[reviewee_id], backref=db.backref('reviews_received', lazy=True))
    
    # Ensure one review per role per job
    __table_args__ = (
        db.UniqueConstraint('job_id', 'reviewer_id', name='unique_review_per_user_per_job'),
    )

    def __repr__(self):
        return f'<Review {self.id}>'


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
    
    # Relationships
    job = db.relationship('Job', backref=db.backref('disputes', lazy=True))
    raised_by = db.relationship('User', foreign_keys=[raised_by_id], backref=db.backref('disputes_raised', lazy=True))
    resolved_by = db.relationship('User', foreign_keys=[resolved_by_id], backref=db.backref('disputes_resolved', lazy=True))

    def __repr__(self):
        return f'<Dispute {self.id}>'


class CivicIssue(db.Model):
    """Community-reported civic issues with voting and status tracking - ENHANCED for Phase 2"""
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Issue details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)  # 'Pothole', 'Broken Light', 'Illegal Dumping', etc.
    
    # Geospatial Data
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    # Status Tracking: 'Reported' -> 'Under_Review' -> 'In_Progress' -> 'Resolved'
    status = db.Column(db.String(50), default='Reported')
    
    # Voting System
    upvote_count = db.Column(db.Integer, default=0)
    
    # Verification
    image_url = db.Column(db.String(500), nullable=True)  # Photo evidence
    guardian_seal = db.Column(db.String(64), nullable=True)  # SHA-256 tamper-proof seal
    ai_risk_score = db.Column(db.Integer, default=0)  # 0-100 severity score
    
    # Admin tracking
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref=db.backref('civic_issues', lazy=True))
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref=db.backref('assigned_issues', lazy=True))

    def __repr__(self):
        return f'<CivicIssue {self.title}>'


class CivicIssueVote(db.Model):
    """Upvote tracking for civic issues - one vote per user per issue"""
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('civic_issue.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    issue = db.relationship('CivicIssue', backref=db.backref('votes', lazy=True, cascade='all, delete-orphan'))
    voter = db.relationship('User', backref=db.backref('civic_votes', lazy=True))
    
    # Ensure one vote per user per issue
    __table_args__ = (
        db.UniqueConstraint('issue_id', 'user_id', name='unique_vote_per_user_per_issue'),
    )

    def __repr__(self):
        return f'<CivicIssueVote {self.id}>'


class JobChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    job = db.relationship('Job', backref=db.backref('messages', lazy=True))
    sender = db.relationship('User', backref=db.backref('chat_messages', lazy=True))

    def __repr__(self):
        return f'<JobChat {self.id}>'


class MacalaaLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    query = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=True)
    query_type = db.Column(db.String(50), nullable=True)  # voice or chat
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('macalaa_logs', lazy=True))

    def __repr__(self):
        return f'<MacalaaLog {self.id}>'


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), default='Personal', nullable=False)
    target_date = db.Column(db.DateTime, nullable=True)
    progress = db.Column(db.Integer, default=0)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('goals', lazy=True))
    parent = db.relationship('Goal', remote_side=[id], backref=db.backref('subgoals', lazy=True))

    def __repr__(self):
        return f'<Goal {self.title}>'


class Milestone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    goal = db.relationship('Goal', backref=db.backref('milestones', lazy=True))

    def __repr__(self):
        return f'<Milestone {self.title}>'

class NetworkContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('network_contacts', lazy=True))

    def __repr__(self):
        return f'<NetworkContact {self.name}>'


class NetworkAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('network_contact.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    alert_type = db.Column(db.String(50), default='Email', nullable=False)  # Email, Call, Meeting
    alert_date = db.Column(db.DateTime, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('network_alerts', lazy=True))
    contact = db.relationship('NetworkContact', backref=db.backref('alerts', lazy=True))

    def __repr__(self):
        return f'<NetworkAlert {self.title}>'


class BalaaHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fare = db.Column(db.Float, nullable=False)
    group_size = db.Column(db.Integer, nullable=False)
    amounts = db.Column(db.Text, nullable=True)
    expected = db.Column(db.Float, nullable=False)
    received = db.Column(db.Float, nullable=False)
    change = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('balaa_history', lazy=True))

    def __repr__(self):
        return f'<BalaaHistory {self.id}>'


class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entry_type = db.Column(db.String(50), default='Thought', nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('diary_entries', lazy=True))

    def __repr__(self):
        return f'<DiaryEntry {self.id}>'


class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('chat_logs', lazy=True))

    def __repr__(self):
        return f'<ChatLog {self.id}>'

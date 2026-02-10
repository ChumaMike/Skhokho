from app.extensions import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# ==========================================
# 👤 CORE IDENTITY & WALLET
# ==========================================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True) # Added for notifications
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default="citizen") 
    
    # 💰 UNIVERSAL WALLET SYSTEM
    wallet_balance = db.Column(db.Float, default=0.0) # Stored as Float for flexibility
    reputation_points = db.Column(db.Integer, default=0) # Global reputation across all pillars
    
    # Relationships
    contacts = db.relationship('NetworkContact', backref='user', lazy=True)
    services = db.relationship('Service', backref='user', lazy=True)
    goals = db.relationship('Goal', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True, foreign_keys='Transaction.user_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# ==========================================
# 🌍 PILLAR 1: LINKUP (The Gig Economy)
# ==========================================
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    
    # 💰 Costing
    cost = db.Column(db.Integer, default=50) # Default price in credits
    
    # Location
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Job(db.Model):
    """The Contract between Customer and Provider"""
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)
    
    # Status: 'Pending', 'In_Progress', 'Completed', 'Cancelled'
    status = db.Column(db.String(50), default='Pending')
    
    # 💰 Escrow Data
    agreed_price = db.Column(db.Integer, default=0)
    is_paid = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chat Relationship
    messages = db.relationship('JobChat', backref='job', lazy=True)

class JobChat(db.Model):
    """Secure comms for a specific job"""
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ==========================================
# 📜 UNIVERSAL TRANSACTION SYSTEM
# ==========================================
class Transaction(db.Model):
    """Universal transaction model for all money movement"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False) # 'Deposit', 'Withdrawal', 'Payment', 'Earning'
    description = db.Column(db.String(255))
    related_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # For transfers
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Keep legacy for backward compatibility
class WalletTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(50)) # 'credit', 'debit'
    description = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ==========================================
# 🧱 LEGACY & OTHER PILLARS
# ==========================================
class NetworkContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    last_contacted = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CivicTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="Reported")
    risk_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text)
    response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entry_type = db.Column(db.String(50), default="Thought")
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BalaaHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fare = db.Column(db.Float)
    group_size = db.Column(db.Integer)
    amounts = db.Column(db.String(200))
    expected = db.Column(db.Float)
    received = db.Column(db.Float)
    change = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
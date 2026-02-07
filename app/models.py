from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from geoalchemy2 import Geometry


# ==========================================
# 👤 CORE USER (The Citizen)
# ==========================================
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    # --- 1. THE ECONOMY (Universal Wallet) ---
    # This balance works across LinkUp and CivicNerve
    civic_points = db.Column(db.Integer, default=0) 
    
    # --- 2. IDENTITY ---
    role = db.Column(db.String(20), default='citizen') # citizen, provider, admin
    phone_number = db.Column(db.String(15), nullable=True)
    
    # --- 3. THE NERVE (Life Management) ---
    # These relationships link the user to their life data
    goals = db.relationship('Goal', backref='owner', lazy='dynamic')
    contacts = db.relationship('NetworkContact', backref='owner', lazy='dynamic')
    
    # --- 4. SAFETY (Macalaa) ---
    # Emergency contacts for Macalaa to auto-dial
    emergency_contact = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        return f'<User {self.username} | Points: {self.civic_points}>'

# --- NEW: Network Contact Model (For your "Network Alerts") ---
class NetworkContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(64))
    action_needed = db.Column(db.String(64)) # e.g., "Call", "Email", "Pay"
    due_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_done = db.Column(db.Boolean, default=False)

# ==========================================
# 🌍 PILLAR 1: LINKUP GEO (The Economy)
# ==========================================
class ProviderProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    business_name = db.Column(db.String(100), nullable=False)
    service_category = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    location_name = db.Column(db.String(100))
    coordinates = db.Column(Geometry('POINT', srid=4326)) 

class JobRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="Open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==========================================
# 🏙️ PILLAR 2: CIVIC NERVE (The Community)
# ==========================================
class CivicTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    status = db.Column(db.String(20), default="Reported")
    ai_risk_score = db.Column(db.Integer)
    guardian_seal = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==========================================
# 🧠 PILLAR 3: MACALAA (Accessibility)
# ==========================================
class SafePoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    coordinates = db.Column(Geometry('POINT', srid=4326))

# ==========================================
# 🔒 LEGACY TOOLS (Personal OS)
# ==========================================

# --- 1. GOALS & MILESTONES ---
class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    target_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="Active")
    is_archived = db.Column(db.Boolean, default=False) # Fix for goals.py query
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    milestones = db.relationship('Milestone', backref='goal', cascade="all, delete-orphan", lazy=True)

    @property
    def progress(self):
        total = len(self.milestones)
        if total == 0: return 0
        completed = sum(1 for m in self.milestones if m.is_completed)
        return int((completed / total) * 100)

class Milestone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    is_completed = db.Column(db.Boolean, default=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'))

# --- 2. DIARY ---
class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry_type = db.Column(db.String(50))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# --- 3. BALAA (The Missing Piece!) ---
class BalaaHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fare = db.Column(db.Float)
    group_size = db.Column(db.Integer)
    amounts = db.Column(db.String) # "10,20,5"
    expected = db.Column(db.Float)
    received = db.Column(db.Float)
    change = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- 4. NETWORK (CRM) ---
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    role = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    last_contacted = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    interactions = db.relationship('Interaction', backref='contact', lazy=True)

class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))
    interaction_type = db.Column(db.String(50))
    completed_date = db.Column(db.DateTime)
    is_completed = db.Column(db.Boolean, default=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'))

# --- 5. CHAT LOG ---
class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text)
    response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
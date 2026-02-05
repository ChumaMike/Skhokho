from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from geoalchemy2 import Geometry

# --- CORE USER MODEL ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Relationships (The glue that holds the Life OS together)
    goals = db.relationship('Goal', backref='user', lazy=True)
    contacts = db.relationship('Contact', backref='user', lazy=True)
    diary_entries = db.relationship('DiaryEntry', backref='user', lazy=True)
    balaa_history = db.relationship('BalaaHistory', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- GOAL TRACKER SYSTEM ---
class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default="General") # Career, Health, Finance
    target_date = db.Column(db.DateTime)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship to sub-tasks
    milestones = db.relationship('Milestone', backref='goal', cascade="all, delete-orphan", lazy=True)

    @property
    def progress(self):
        """Calculates percentage based on completed milestones"""
        total = len(self.milestones)
        if total == 0:
            return 0
        completed = sum(1 for m in self.milestones if m.is_completed)
        return int((completed / total) * 100)

class Milestone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False)

# --- PERSONAL CRM SYSTEM ---
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100)) # e.g. "Recruiter", "Mentor", "Cousin"
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    # How often do you want to stay in touch? (in days)
    frequency_days = db.Column(db.Integer, default=30) 
    
    # Calculated field: When did we last interact?
    last_contacted = db.Column(db.DateTime)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # History of calls, meetings, and reminders
    interactions = db.relationship('Interaction', backref='contact', cascade="all, delete-orphan", lazy=True)

class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    
    description = db.Column(db.String(255), nullable=False) # e.g. "Call Joe at 8"
    interaction_type = db.Column(db.String(50), default="Note") # Call, Meeting, Email, Reminder
    
    scheduled_date = db.Column(db.DateTime) # If set, it's a REMINDER
    completed_date = db.Column(db.DateTime) # If set, it's HISTORY
    
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- EXISTING TOOLS ---
class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class BalaaHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fare = db.Column(db.Float, nullable=False)
    group_size = db.Column(db.Integer, nullable=False)
    amounts = db.Column(db.String, nullable=False)
    expected = db.Column(db.Float, nullable=False)
    received = db.Column(db.Float, nullable=False)
    change = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LocationTag(db.Model):
    """
    Stores 'Points of Interest' for the Super App.
    Examples:
    - Type: 'Internship', Name: 'Microsoft HQ', Coords: (-26.1, 28.0)
    - Type: 'Danger', Name: 'Hillbrow Zone C', Coords: (-26.1, 28.0)
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # 'Career', 'Safety', 'Social'
    description = db.Column(db.String(255))
    
    # THE SPATIAL COLUMN (Stores GPS data)
    # SRID 4326 is the standard for GPS (WGS84)
    coordinates = db.Column(Geometry('POINT', srid=4326)) 

    def __repr__(self):
        return f'<Location {self.name}>'
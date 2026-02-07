from ..extensions import db
from datetime import datetime
from flask_login import UserMixin  # <-- NEW: Helps Flask handle login sessions
from werkzeug.security import generate_password_hash, check_password_hash # <-- NEW: Security

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(20), default='client') # 'client', 'provider', 'admin'
    
    # SECURITY: We store the HASH, not the password
    password_hash = db.Column(db.String(128)) 
    
    is_active_user = db.Column(db.Boolean, default=True) # Renamed to avoid clash with UserMixin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    listings = db.relationship('Listing', backref='provider', lazy=True)

    def set_password(self, password):
        """Encrypts the password before saving."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the password matches the hash."""
        return check_password_hash(self.password_hash, password)

    # UserMixin requires this property to know if user is active
    @property
    def is_active(self):
        return self.is_active_user

    def __repr__(self):
        return f"<User {self.name} ({self.role})>"
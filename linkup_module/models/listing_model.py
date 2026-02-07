from linkup_module.extensions import db
from datetime import datetime

# --- LISTING MODEL ---
class Listing(db.Model):
    __tablename__ = 'listings'

    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Points to Skhokho User Table
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    price = db.Column(db.String(50), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    # Note: We use the string 'User' because standard SQLAlchemy finds the class by name
    provider = db.relationship('User', backref=db.backref('listings', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'description': self.description,
            'lat': self.latitude,
            'lon': self.longitude,
            'price': self.price
        }

# --- JOB REQUEST MODEL ---
class JobRequest(db.Model):
    __tablename__ = 'job_requests'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Points to Skhokho User
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='open') # open, in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    customer = db.relationship('User', backref=db.backref('job_requests', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'description': self.description,
            'status': self.status,
            'lat': self.latitude,
            'lon': self.longitude
        }
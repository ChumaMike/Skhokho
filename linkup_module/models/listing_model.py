from datetime import datetime
from ..extensions import db

# 1. THE LISTING (A Service Provider's Ad)
class Listing(db.Model):
    __tablename__ = 'listings'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False) # service, house, job
    price = db.Column(db.String(50))
    contact = db.Column(db.String(50))
    address = db.Column(db.String(200))
    
    # AI Tags (Hidden Search Keywords)
    keywords = db.Column(db.String(500), default="")
    
    # Provider linking
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_verified = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=0.0)
    
    # Location data
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'price': self.price,
            'contact': self.contact,
            'address': self.address,
            'is_verified': self.is_verified,
            'rating': self.rating,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'keywords': self.keywords
        }

# 2. THE LEAD (A Direct Request to a Specific Listing)
class Lead(db.Model):
    __tablename__ = 'leads'

    id = db.Column(db.Integer, primary_key=True)
    customer_phone = db.Column(db.String(20), nullable=False) # The WhatsApp User
    message = db.Column(db.String(200)) # "I need a callback"
    status = db.Column(db.String(20), default="new") # new, contacted, closed
    
    # Relationships
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'))
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'customer_phone': self.customer_phone,
            'status': self.status,
            'date': self.created_at.strftime("%Y-%m-%d %H:%M")
        }

class JobRequest(db.Model):
    __tablename__ = 'job_requests'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default="open")
    
    # [NEW] Coordinates (So the pin stays still!)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    customer = db.relationship('src.models.user_model.User', backref='jobs')

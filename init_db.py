from app import create_app
from app.extensions import db

def init_database():
    app = create_app()
    
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("Database initialized successfully!")
        print("Tables created: users, services, jobs, civic_issues, macalaa_logs")

if __name__ == "__main__":
    init_database()
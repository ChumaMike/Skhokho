from app import create_app
from app.extensions import db
from app.models import User, Service, CivicIssue
from werkzeug.security import generate_password_hash

def seed_database():
    app = create_app()
    
    with app.app_context():
        # 1. Create demo user
        user = User(
            username='citizen_one',
            email='citizen@skhokho.com',
            password_hash=generate_password_hash('password123'),
            wallet_balance=500,
            reputation_points=0,
            role='citizen'
        )
        db.session.add(user)
        db.session.commit()
        
        print("Created user: citizen_one (500 credits)")
        
        # 2. Create 5 services (Plumbers/Electricians in Soweto)
        services = [
            {
                'name': 'Quick Fix Plumbers',
                'category': 'Plumbing',
                'description': 'Emergency plumbing services',
                'price': 150,
                'latitude': -26.2321,
                'longitude': 27.8816
            },
            {
                'name': 'Bright Electricians',
                'category': 'Electrical',
                'description': 'Residential and commercial electrical services',
                'price': 200,
                'latitude': -26.2345,
                'longitude': 27.8830
            },
            {
                'name': 'Soweto Plumbers Inc',
                'category': 'Plumbing',
                'description': 'Professional plumbing solutions',
                'price': 180,
                'latitude': -26.2300,
                'longitude': 27.8800
            },
            {
                'name': 'Power Tech Electrical',
                'category': 'Electrical',
                'description': 'Expert electrical repairs and installations',
                'price': 220,
                'latitude': -26.2350,
                'longitude': 27.8840
            },
            {
                'name': 'Leak Busters',
                'category': 'Plumbing',
                'description': 'Specialized leak detection and repair',
                'price': 160,
                'latitude': -26.2280,
                'longitude': 27.8790
            }
        ]
        
        for service_data in services:
            service = Service(
                name=service_data['name'],
                category=service_data['category'],
                description=service_data['description'],
                price=service_data['price'],
                latitude=service_data['latitude'],
                longitude=service_data['longitude'],
                provider_id=user.id
            )
            db.session.add(service)
        
        db.session.commit()
        print("Created 5 services (Plumbers/Electricians) in Soweto")
        
        # 3. Create 3 civic issues (Potholes) in Soweto
        issues = [
            {
                'title': 'Large Pothole on Vilakazi Street',
                'description': 'Major pothole causing traffic issues',
                'latitude': -26.2325,
                'longitude': 27.8818,
                'ai_risk_score': 75,
                'city_status': 'Reported'
            },
            {
                'title': 'Pothole on Chris Hani Road',
                'description': 'Deep pothole dangerous for cyclists',
                'latitude': -26.2340,
                'longitude': 27.8825,
                'ai_risk_score': 85,
                'city_status': 'Investigating'
            },
            {
                'title': 'Pothole Near Orlando Stadium',
                'description': 'Pothole causing vehicle damage',
                'latitude': -26.2310,
                'longitude': 27.8805,
                'ai_risk_score': 65,
                'city_status': 'Reported'
            }
        ]
        
        for issue_data in issues:
            issue = CivicIssue(
                title=issue_data['title'],
                description=issue_data['description'],
                latitude=issue_data['latitude'],
                longitude=issue_data['longitude'],
                ai_risk_score=issue_data['ai_risk_score'],
                city_status=issue_data['city_status'],
                reporter_id=user.id
            )
            db.session.add(issue)
        
        db.session.commit()
        print("Created 3 civic issues (Potholes) in Soweto")
        
        # Verify data
        print(f"Users: {User.query.count()}")
        print(f"Services: {Service.query.count()}")
        print(f"Civic Issues: {CivicIssue.query.count()}")

if __name__ == "__main__":
    seed_database()
from app import create_app
from app.extensions import db
from app.models import User, Service, CivicIssue, Opportunity, NewsItem
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
                'status': 'Reported',
                'category': 'Pothole'
            },
            {
                'title': 'Pothole on Chris Hani Road',
                'description': 'Deep pothole dangerous for cyclists',
                'latitude': -26.2340,
                'longitude': 27.8825,
                'ai_risk_score': 85,
                'status': 'Investigating',
                'category': 'Pothole'
            },
            {
                'title': 'Pothole Near Orlando Stadium',
                'description': 'Pothole causing vehicle damage',
                'latitude': -26.2310,
                'longitude': 27.8805,
                'ai_risk_score': 65,
                'status': 'Reported',
                'category': 'Pothole'
            }
        ]
        
        for issue_data in issues:
            issue = CivicIssue(
                title=issue_data['title'],
                description=issue_data['description'],
                latitude=issue_data['latitude'],
                longitude=issue_data['longitude'],
                ai_risk_score=issue_data['ai_risk_score'],
                status=issue_data['status'],
                category=issue_data['category'],
                reporter_id=user.id
            )
            db.session.add(issue)
        
        db.session.commit()
        print("Created 3 civic issues (Potholes) in Soweto")
        
        # 4. Create 5 opportunities in Johannesburg
        opportunities = [
            {
                'title': 'Software Engineering Internship',
                'category': 'Internship',
                'description': '3-month internship for software engineering students. Learn Python, JavaScript, and web development.',
                'latitude': -26.2041,
                'longitude': 28.0473,
                'location_name': 'Sandton, Johannesburg',
                'company': 'Tech Innovations Ltd',
                'requirements': 'Python, JavaScript, Git',
                'salary': 'R5000/month',
            },
            {
                'title': 'Junior Web Developer',
                'category': 'Job',
                'description': 'Entry-level web developer position. Build responsive websites and web applications.',
                'latitude': -26.1952,
                'longitude': 28.0340,
                'location_name': 'Bryanston, Johannesburg',
                'company': 'Web Solutions',
                'requirements': 'HTML, CSS, JavaScript, React',
                'salary': 'R15000/month',
            },
            {
                'title': 'CodeCamp Johannesburg',
                'category': 'Training',
                'description': 'Weekend coding bootcamp for beginners. Learn full-stack web development.',
                'latitude': -26.2050,
                'longitude': 28.0450,
                'location_name': 'Rosebank, Johannesburg',
                'company': 'Coding Academy',
                'requirements': 'Basic computer skills',
                'salary': 'R2500',
            },
            {
                'title': 'Mobile App Development Workshop',
                'category': 'Event',
                'description': 'Workshop on cross-platform mobile app development with React Native.',
                'latitude': -26.1840,
                'longitude': 28.0300,
                'location_name': 'Randburg, Johannesburg',
                'company': 'Mobile Dev Meetup',
                'requirements': 'JavaScript knowledge',
                'salary': 'Free',
            },
            {
                'title': 'Full Stack Developer Position',
                'category': 'Job',
                'description': 'Experienced full stack developer needed for fintech startup.',
                'latitude': -26.2080,
                'longitude': 28.0520,
                'location_name': 'Parktown, Johannesburg',
                'company': 'FinTech Solutions',
                'requirements': 'Python, Django, React, Postgres',
                'salary': 'R35000/month',
            }
        ]
        
        for opp_data in opportunities:
            opp = Opportunity(
                title=opp_data['title'],
                category=opp_data['category'],
                description=opp_data['description'],
                latitude=opp_data['latitude'],
                longitude=opp_data['longitude'],
                location_name=opp_data['location_name'],
                company=opp_data['company'],
                requirements=opp_data['requirements'],
                salary=opp_data['salary']
            )
            db.session.add(opp)
        
        db.session.commit()
        print("Created 5 opportunities in Johannesburg")
        
        # 5. Create 3 breaking news items
        news_items = [
            {
                'title': 'Traffic Accident on Jan Smuts Avenue',
                'category': 'Traffic',
                'description': 'Major traffic accident causing delays on Jan Smuts Avenue. Avoid the area if possible.',
                'latitude': -26.1980,
                'longitude': 28.0380,
                'location_name': 'Bryanston, Johannesburg',
                'source': 'Traffic Alert SA',
                'is_breaking': True
            },
            {
                'title': 'Power Outage in Sandton',
                'category': 'Weather',
                'description': 'Planned power outage affecting Sandton area from 10 AM to 2 PM.',
                'latitude': -26.2041,
                'longitude': 28.0473,
                'location_name': 'Sandton, Johannesburg',
                'source': 'Eskom',
                'is_breaking': True
            },
            {
                'title': 'Community Safety Workshop',
                'category': 'Community',
                'description': 'Free community safety workshop at the local community center.',
                'latitude': -26.2100,
                'longitude': 28.0400,
                'location_name': 'Rosebank, Johannesburg',
                'source': 'Johannesburg Community Center',
                'is_breaking': False
            }
        ]
        
        for news_data in news_items:
            news = NewsItem(
                title=news_data['title'],
                category=news_data['category'],
                description=news_data['description'],
                latitude=news_data['latitude'],
                longitude=news_data['longitude'],
                location_name=news_data['location_name'],
                source=news_data['source'],
                is_breaking=news_data['is_breaking']
            )
            db.session.add(news)
        
        db.session.commit()
        print("Created 3 news items")
        
        # Verify data
        print(f"Users: {User.query.count()}")
        print(f"Services: {Service.query.count()}")
        print(f"Civic Issues: {CivicIssue.query.count()}")
        print(f"Opportunities: {Opportunity.query.count()}")
        print(f"News Items: {NewsItem.query.count()}")

if __name__ == "__main__":
    seed_database()

from app import create_app
from app.extensions import db
from app.models import User, Service, CivicIssue

def verify_seed_data():
    app = create_app()
    
    with app.app_context():
        # Verify user
        user = User.query.filter_by(username='citizen_one').first()
        if user:
            print(f"✅ User: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Wallet Balance: {user.wallet_balance}")
            print(f"   Reputation Points: {user.reputation_points}")
            print(f"   Role: {user.role}")
        else:
            print("❌ User not found")
        
        # Verify services
        services = Service.query.all()
        print(f"\n✅ Services ({len(services)}):")
        for service in services:
            print(f"   - {service.name} ({service.category}) - {service.price} credits")
            print(f"     Location: {service.latitude}, {service.longitude}")
        
        # Verify civic issues
        issues = CivicIssue.query.all()
        print(f"\n✅ Civic Issues ({len(issues)}):")
        for issue in issues:
            print(f"   - {issue.title}")
            print(f"     Severity: {issue.ai_severity_score}/100")
            print(f"     Status: {issue.city_status}")
            print(f"     Location: {issue.latitude}, {issue.longitude}")

if __name__ == "__main__":
    verify_seed_data()
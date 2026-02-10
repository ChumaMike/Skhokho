from app import create_app
from app.extensions import db
from app.models import Opportunity, NewsItem, CivicIssue, Goal

app = create_app()

with app.app_context():
    print("=== Database Statistics ===")
    print(f"Users: {db.session.query(User).count()}" if 'User' in globals() else "Users: N/A")
    print(f"Opportunities: {Opportunity.query.count()}")
    print(f"News Items: {NewsItem.query.count()}")
    print(f"Civic Issues: {CivicIssue.query.count()}")
    print(f"Goals: {Goal.query.count()}")
    
    print("\n=== Opportunities ===")
    for opp in Opportunity.query.all():
        print(f"- {opp.title} ({opp.category})")
    
    print("\n=== News Items ===")
    for news in NewsItem.query.all():
        print(f"- {news.title} (Breaking: {news.is_breaking})")
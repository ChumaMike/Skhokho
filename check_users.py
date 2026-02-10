from app import create_app
from app.extensions import db
from app.models import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print("Number of users:", len(users))
    for user in users:
        print(f"Username: {user.username}, Email: {user.email}, Balance: {user.wallet_balance}, Points: {user.reputation_points}")
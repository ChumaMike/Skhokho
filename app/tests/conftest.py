import pytest
from app import create_app
from app.extensions import db
from app.models import User

# 1. Create a "Simulation" App
@pytest.fixture
def app():
    # Use a temporary configuration
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # RAM Database (Fast & Disposable)
        "WTF_CSRF_ENABLED": False, # Disable complex form security for easier testing
        "SECRET_KEY": "test_key"
    })

    # Create tables in the fake DB
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

# 2. Create a "Test Client" (A fake browser)
@pytest.fixture
def client(app):
    return app.test_client()

# 3. Create an Auth Helper (To log us in quickly)
@pytest.fixture
def auth(client):
    class AuthActions:
        def register(self, username='testuser', password='password123'):
            return client.post('/register', data={
                'username': username, 
                'password': password
            }, follow_redirects=True)

        def login(self, username='testuser', password='password123'):
            return client.post('/login', data={
                'username': username, 
                'password': password
            }, follow_redirects=True)

        def logout(self):
            return client.get('/logout', follow_redirects=True)

    return AuthActions()
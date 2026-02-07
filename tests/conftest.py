import pytest
from app import create_app, db
from app.models import User
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Uses RAM, not a real file
    WTF_CSRF_ENABLED = False # Disable security tokens for easier testing

@pytest.fixture
def app():
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def auth_client(client):
    """A client that auto-logins a test user"""
    # Create a test user
    user = User(username='test_user', role='citizen')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    # Login
    client.post('/login', data={'username': 'test_user', 'password': 'password'})
    return client
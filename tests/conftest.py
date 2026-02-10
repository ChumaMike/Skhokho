import pytest
from app import create_app
from app.extensions import db
from sqlalchemy.pool import NullPool

@pytest.fixture(scope='session')
def app():
    """Create the app once for the session."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "postgresql://skhokho_user:skhokho_pass@db:5432/skhokho_db",
        "WTF_CSRF_ENABLED": False,
        # NullPool ensures connections close immediately, preventing deadlocks
        "SQLALCHEMY_ENGINE_OPTIONS": {"poolclass": NullPool}
    })
    
    with app.app_context():
        # Ensure schema exists at start
        db.create_all()
        yield app
        # Cleanup at end
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function', autouse=True)
def clean_db(app):
    """
    Standard Clean: Wipes tables before every test.
    """
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
    
    yield # Run test

    with app.app_context():
        db.session.remove()

class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username='testuser', password='testpassword'):
        return self._client.post(
            '/login',
            data={'username': username, 'password': password},
            follow_redirects=True
        )

    def logout(self):
        return self._client.get('/logout', follow_redirects=True)
        
    def register(self, username='testuser', password='testpassword'):
        return self._client.post(
            '/register',
            data={'username': username, 'password': password},
            follow_redirects=True
        )

@pytest.fixture
def auth(client):
    return AuthActions(client)
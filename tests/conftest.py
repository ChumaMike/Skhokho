import pytest
from app import create_app, db
from app.models import User
from sqlalchemy.orm import scoped_session, sessionmaker  # ✅ Added imports

# --- 1. CONFIGURATION ---
@pytest.fixture(scope='session')
def app():
    """
    Creates the Skhokho App instance for the entire test session.
    """
    app = create_app()
    app.config.update({
        "TESTING": True,
        # We use the REAL DB but rely on transactions to keep it clean
        "WTF_CSRF_ENABLED": False, 
        "SECRET_KEY": "qa_secret_key"
    })
    
    with app.app_context():
        yield app

# --- 2. THE BUBBLE (Transaction) ---
@pytest.fixture(scope='function')
def client(app):
    """
    Creates a test client inside a transaction bubble.
    """
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # ✅ FIX: expire_on_commit=False prevents "DetachedInstanceError"
        # This keeps 'current_user' alive even after we save a Goal.
        session_factory = sessionmaker(bind=connection, expire_on_commit=False)
        test_session = scoped_session(session_factory)
        
        _original_session = db.session
        db.session = test_session

        with app.test_client() as client:
            yield client

        db.session.remove()
        transaction.rollback()
        connection.close()
        db.session = _original_session

# --- 3. AUTH HELPER ---
@pytest.fixture
def auth(client):
    class AuthActions:
        # ✅ FIX: Removed '/auth' prefix. Now pointing to root URLs.
        def register(self, username='qa_user', password='password123'):
            return client.post('/register', data={ 
                'username': username, 
                'password': password,
                'confirm_password': password
            }, follow_redirects=True)

        def login(self, username='qa_user', password='password123'):
            return client.post('/login', data={
                'username': username, 
                'password': password
            }, follow_redirects=True)

        def logout(self):
            return client.get('/logout', follow_redirects=True)

    return AuthActions()
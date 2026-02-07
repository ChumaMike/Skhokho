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
    Anything this client does is undone after the test.
    """
    with app.app_context():
        # 1. Connect to the DB
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # 2. Create a specific session for this test that uses the connection
        # This bypasses the default session and ensures we are inside the transaction
        session_factory = sessionmaker(bind=connection)
        test_session = scoped_session(session_factory)
        
        # 3. Swap the app's session with our test session
        # Now, when the app says db.session.add(), it uses OUR bubble
        _original_session = db.session
        db.session = test_session

        with app.test_client() as client:
            yield client

        # 4. POP THE BUBBLE: Rollback everything
        db.session.remove()
        transaction.rollback()
        connection.close()
        
        # Restore original (good practice)
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
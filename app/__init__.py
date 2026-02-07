from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Security: Rate Limiter
limiter = Limiter(key_func=get_remote_address)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 1. Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    login_manager.login_view = 'auth.login'

    # 2. Register CORE Skhokho Blueprints
    # These are the native features living inside /app/routes
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.macalaa import macalaa_bp
    from app.routes.civic import civic_bp
    from app.routes.api import api_bp
    from app.routes.chat import chat_bp
    from app.routes.tools import tools_bp
    from app.routes.crm import crm_bp
    from app.routes.goals import goals_bp
    
    

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(macalaa_bp, url_prefix='/macalaa')
    app.register_blueprint(civic_bp, url_prefix='/civic')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(tools_bp, url_prefix='/tools')
    app.register_blueprint(crm_bp, url_prefix='/network')
    app.register_blueprint(goals_bp, url_prefix='/goals')

    # 3. Register EXTERNAL Modules (Separation of Concerns)
    # This loads the "LinkUp" system from the folder in your root directory
    try:
        # Based on your tree, the folder is named 'linkup_module'
        # Ensure linkup_module/__init__.py exposes 'linkup_bp'
        from linkup_module import linkup_bp 
        
        # We check if it's already registered to prevent the crash
        if 'linkup' not in app.blueprints:
            app.register_blueprint(linkup_bp, url_prefix='/linkup')
            print("✅ LinkUp Module Loaded Successfully")
            
    except ImportError as e:
        print(f"⚠️ LinkUp Module Not Found: {e}")
        # Optional: You could load a placeholder blueprint here if you wanted
        pass
    except ValueError as e:
        print(f"⚠️ LinkUp Blueprint Error: {e}")

    return app

# User Loader for Login Manager
from app.models import User
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
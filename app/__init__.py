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

    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    login_manager.login_view = 'auth.login'

    # --- IMPORT ALL ENGINES ---
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    
    # The Super App Modules
    from app.routes.linkup import linkup_bp
    from app.routes.macalaa import macalaa_bp
    from app.routes.civic import civic_bp
    from app.routes.api import api_bp
    
    # The "Neural Core" Engines (Legacy) 🛠️
    from app.routes.chat import chat_bp
    from app.routes.tools import tools_bp  
    from app.routes.crm import crm_bp      
    from app.routes.goals import goals_bp  



    # --- REGISTER ALL BLUEPRINTS ---
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    
    
    # Super App Routes
    app.register_blueprint(linkup_bp, url_prefix='/linkup')
    app.register_blueprint(macalaa_bp, url_prefix='/macalaa')
    app.register_blueprint(civic_bp, url_prefix='/civic')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Neural Core Routes
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(tools_bp, url_prefix='/tools') # Makes /tools/balaa work
    app.register_blueprint(crm_bp, url_prefix='/network') # Makes /network/dashboard work
    app.register_blueprint(goals_bp, url_prefix='/goals')

    return app

from app.models import User
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
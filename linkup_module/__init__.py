from flask import Blueprint
from .extensions import db, login_manager
from .models.user_model import User

# 1. DEFINE THE MASTER BLUEPRINT
# This is the "Plug" you will hand over to Skhokho.
linkup_bp = Blueprint('linkup', __name__, template_folder='templates', static_folder='static')

# 2. IMPORT SUB-MODULES (Using Relative Imports)
# We use dots (.) so Python looks inside the current folder
from .api.web.web_routes import web_bp
from .api.web.listing_routes import listings_bp
from .api.web.job_routes import jobs_bp
from .api.auth_routes import auth_bp
from .api.bot_routes import bot_bp
from .api.admin_routes import admin_bp

# 3. NEST THE BLUEPRINTS
# Instead of app.register_blueprint, we attach them to the Master Blueprint
linkup_bp.register_blueprint(auth_bp)
linkup_bp.register_blueprint(bot_bp)
linkup_bp.register_blueprint(admin_bp)
linkup_bp.register_blueprint(web_bp)
linkup_bp.register_blueprint(listings_bp)
linkup_bp.register_blueprint(jobs_bp)

# 4. SETUP USER LOADER (For Login)
# This allows LinkUp to handle its own user sessions
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 5. EXPORT DATABASE MODELS
# This ensures Skhokho can see your tables to create them
from .models.listing_model import Listing, JobRequest, Lead
from flask import Flask
from src.models.listing_model import db 
# IMPORT THE NEW MODEL so SQLAlchemy sees it
from src.models.user_model import User 

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///linkup.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()  # Now creates 'users' AND 'listings'

    from src.api.bot_routes import bot_bp
    app.register_blueprint(bot_bp)
    
    @app.route("/")
    def home():
        return "LinkUp Enterprise is Running!"
        
    return app
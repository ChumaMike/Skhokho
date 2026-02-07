from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# We define them here, but we DO NOT initialize them with an app yet.
db = SQLAlchemy()
login_manager = LoginManager()
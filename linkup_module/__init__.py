from flask import Blueprint

# 1. Define the Main Blueprint
linkup_bp = Blueprint('linkup', __name__, 
                      template_folder='templates',
                      static_folder='static')

# 2. Import Extensions
from . import extensions

# 3. Register the Child 'Web' Blueprint
try:
    from .api.web.web_routes import web_bp
    # This nests the routes: /linkup + /map = /linkup/map
    # But Flask names it 'linkup.web.map_view'
    linkup_bp.register_blueprint(web_bp) 
    print("✅ LinkUp Routes Registered")
except ImportError as e:
    print(f"⚠️ LinkUp Route Import Failed: {e}")
except Exception as e:
    print(f"⚠️ LinkUp General Error: {e}")
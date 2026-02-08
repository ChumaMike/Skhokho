from flask import Blueprint, render_template

macalaa_bp = Blueprint('macalaa', __name__)

@macalaa_bp.route('/')
def index():
    return render_template('base.html') # Placeholder until we build the template
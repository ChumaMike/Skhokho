from flask import Blueprint, render_template

macalaa_bp = Blueprint('macalaa', __name__)

@macalaa_bp.route('/')
def index():
    return "<h1>Macalaa Vision Interface (Under Construction)</h1>"
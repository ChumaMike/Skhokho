from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from collections import defaultdict
import requests
import os
import logging
from linkup_module import linkup_bp



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback-secret")

app.register_blueprint(linkup_bp, url_prefix='/marketplace')

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skhokho.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class BalaaHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fare = db.Column(db.Float, nullable=False)
    group_size = db.Column(db.Integer, nullable=False)
    amounts = db.Column(db.String, nullable=False)
    expected = db.Column(db.Float, nullable=False)
    received = db.Column(db.Float, nullable=False)
    change = db.Column(db.Float, nullable=False)
    time = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper functions
def get_weather(location):
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        logger.warning("No WEATHER_API_KEY found in environment.")
        return {'error': 'Missing API key'}

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()

        if response.ok:
            return {
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description'],
                'location': data['name']
            }
        return {'error': data.get('message', 'Weather fetch failed')}
    except Exception as e:
        logger.error(f"Weather fetch failed: {e}")
        return {'error': str(e)}

def get_loadshedding_status(location):
    return f"Current load shedding status in {location}: Stage 2. Stay charged, skhokho!"

def get_daily_quote():
    try:
        response = requests.get("https://api.quotable.io/random")
        data = response.json()
        return f"Skhokho, here's a quote for you: \"{data['content']}\" — {data['author']}"
    except Exception as e:
        logger.error(f"Quote fetch failed: {e}")
        return "Couldn't fetch a quote today, skhokho."

def get_news_headlines(city):
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        return ["NewsAPI key missing, skhokho."]

    try:
        url = f"https://newsapi.org/v2/everything?q={city}&apiKey={api_key}&pageSize=3"
        response = requests.get(url)
        if response.ok:
            articles = response.json().get('articles', [])
            return [f"{i+1}. {a['title']}" for i, a in enumerate(articles)]
        return [f"News fetch error: {response.status_code}"]
    except Exception as e:
        logger.error(f"News fetch failed: {e}")
        return ["No news right now, skhokho."]

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def group_entries_by_date(entries):
    grouped = defaultdict(list)
    for entry in entries:
        date = entry.timestamp.strftime("%Y-%m-%d")
        grouped[date].append(entry)
    return dict(sorted(grouped.items(), reverse=True))

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        flash('Invalid username or password', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/balaa', methods=['GET', 'POST'])
@login_required
def balaa():
    result = None
    history = []

    if request.method == 'POST':
        try:
            fare = float(request.form['fare'])
            group_size = int(request.form['group_size'])
            amounts = request.form.getlist('amounts')
            amounts = [float(a) for a in amounts if a.strip()]
            total_expected = fare * group_size
            total_received = sum(amounts)
            change = total_received - total_expected
            timestamp = datetime.now().strftime("%H:%M:%S")

            new_entry = BalaaHistory(
                user_id=current_user.id,
                fare=fare,
                group_size=group_size,
                amounts=','.join(map(str, amounts)),
                expected=total_expected,
                received=total_received,
                change=change,
                time=timestamp
            )
            db.session.add(new_entry)
            db.session.commit()

            result = {
                'fare': fare,
                'group_size': group_size,
                'amounts': amounts,
                'expected': total_expected,
                'received': total_received,
                'change': change,
                'time': timestamp
            }

        except Exception as e:
            result = {'error': str(e)}

    history_rows = BalaaHistory.query.filter_by(user_id=current_user.id).order_by(BalaaHistory.created_at.desc()).all()
    for row in history_rows:
        history.append({
            'fare': row.fare,
            'group_size': row.group_size,
            'amounts': list(map(float, row.amounts.split(','))),
            'expected': row.expected,
            'received': row.received,
            'change': row.change,
            'time': row.time
        })

    return render_template('balaa.html', result=result, history=history)

@app.route('/diary', methods=['GET', 'POST'])
@login_required
def diary():
    if request.method == 'POST':
        entry_type = request.form.get('entry_type')
        content = request.form.get('content', '').strip()
        if not entry_type or not content:
            flash("Please select entry type and provide content.", "danger")
            return redirect(url_for('diary'))

        entry = DiaryEntry(
            entry_type=entry_type,
            content=content,
            user_id=current_user.id
        )
        db.session.add(entry)
        db.session.commit()

        flash("Diary entry saved.", "success")
        return redirect(url_for('diary'))

    entries = DiaryEntry.query.filter_by(user_id=current_user.id).order_by(DiaryEntry.timestamp.desc()).all()
    grouped_entries = group_entries_by_date(entries)
    return render_template('diary.html', entries=grouped_entries)

@app.route('/snapshot', methods=['GET', 'POST'])
@login_required
def snapshot():
    weather = None
    location = None

    if request.method == 'POST':
        location = request.form.get('location', '').strip()
        if location:
            weather = get_weather(location)
        else:
            flash("Please enter a location.", "danger")

    return render_template('snapshot.html', weather=weather, location=location)

@app.route('/local-update', methods=['GET', 'POST'])
@login_required
def local_update():
    weather = {}
    load_shedding = ""
    news = []
    city = ""

    if request.method == 'POST':
        city = request.form.get('location', '').strip()
        if not city:
            flash("Please enter a location.", "danger")
            return redirect(url_for('local_update'))

        weather = get_weather(city)
        load_shedding = get_loadshedding_status(city)
        news = get_news_headlines(city)

    quote = get_daily_quote()

    return render_template('local_update.html', weather=weather, load_shedding=load_shedding, news=news, quote=quote, city=city)



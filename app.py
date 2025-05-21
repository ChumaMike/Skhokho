from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'secret123'

# Setup database (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skhokho.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Setup Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def group_entries_by_date(entries):
    grouped = defaultdict(list)
    for entry in entries:
        date = entry.timestamp.strftime("%Y-%m-%d")
        grouped[date].append(entry)
    return dict(sorted(grouped.items(), reverse=True))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        if not username or not password:
            flash("Please fill both username and password")
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for('register'))

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/balaa', methods=['GET', 'POST'])
def balaa():
    # This remains public (no login needed)
    result = None

    if 'history' not in session:
        session['history'] = []

    if request.method == 'POST':
        try:
            fare = float(request.form['fare'])
            group_size = int(request.form['group_size'])
            amounts = request.form.getlist('amounts')
            amounts = [float(a) for a in amounts if a.strip()]
            total_expected = fare * group_size
            total_received = sum(amounts)
            change = total_received - total_expected

            result = {
                'fare': fare,
                'group_size': group_size,
                'amounts': amounts,
                'expected': total_expected,
                'received': total_received,
                'change': change,
                'time': datetime.now().strftime("%H:%M:%S")
            }

            history = session['history']
            history.append(result)
            session['history'] = history

        except Exception as e:
            result = {'error': str(e)}

    return render_template('balaa.html', result=result, history=session['history'])

@app.route('/diary', methods=['GET', 'POST'])
@login_required
def diary():
    if request.method == 'POST':
        entry_type = request.form.get('entry_type')
        content = request.form.get('content', '').strip()
        if not entry_type or not content:
            flash("Please select entry type and provide content.")
            return redirect(url_for('diary'))

        entry = DiaryEntry(
            entry_type=entry_type,
            content=content,
            user_id=current_user.id
        )
        db.session.add(entry)
        db.session.commit()

        flash("Diary entry saved.")
        return redirect(url_for('diary'))

    entries = DiaryEntry.query.filter_by(user_id=current_user.id).order_by(DiaryEntry.timestamp.desc()).all()
    grouped_entries = group_entries_by_date(entries)
    return render_template('diary.html', entries=grouped_entries)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)

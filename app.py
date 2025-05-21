from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'secret123'

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skhokho.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Login manager setup
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

class BalaaHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fare = db.Column(db.Float, nullable=False)
    group_size = db.Column(db.Integer, nullable=False)
    amounts = db.Column(db.String, nullable=False)  # comma-separated amounts
    expected = db.Column(db.Float, nullable=False)
    received = db.Column(db.Float, nullable=False)
    change = db.Column(db.Float, nullable=False)
    time = db.Column(db.String, nullable=False)  # store HH:MM:SS as string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect('/register')

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect('/login')

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
            return redirect('/')
        else:
            flash('Invalid username or password', 'danger')
            return redirect('/login')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect('/login')

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

            # Save to DB
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

    # Load history
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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)

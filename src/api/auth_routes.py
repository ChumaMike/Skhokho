from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from src.extensions import db
from src.models.user_model import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        user = User.query.filter_by(phone_number=phone).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            
            # 1. FIX REDIRECT (Add 'linkup.')
            if user.role == 'admin':
                return redirect(url_for('linkup.admin.admin_panel'))
            return redirect(url_for('linkup.web.dashboard')) 
        else:
            flash('Invalid phone number or password.', 'error')
            
    # 2. FIX TEMPLATE RENDER (If you moved templates, ensure path is correct)
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    # 3. FIX REDIRECT
    return redirect(url_for('linkup.auth.login'))

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        phone = request.form.get('phone')
        name = request.form.get('name')
        password = request.form.get('password')
        role = request.form.get('role')
        
        user = User.query.filter_by(phone_number=phone).first()
        if user:
            flash('Phone number already registered.', 'error')
            # 4. FIX REDIRECT
            return redirect(url_for('linkup.auth.signup'))
        
        new_user = User(
            phone_number=phone, 
            name=name, 
            role=role if role else 'customer'
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created! Please log in.', 'success')
        # 5. FIX REDIRECT
        return redirect(url_for('linkup.auth.login'))
        
    return render_template('auth/signup.html')
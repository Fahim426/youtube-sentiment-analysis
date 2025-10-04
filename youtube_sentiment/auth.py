"""
Authentication module for YouTube Sentiment Analysis application
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, LoginHistory, SearchHistory
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            
            # Record login history
            login_record = LoginHistory(
                user_id=user.id,
                ip_address=request.environ.get('HTTP_X_REAL_IP', request.remote_addr),
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(login_record)  # type: ignore[reportAttributeAccessIssue]
            db.session.commit()  # type: ignore[reportAttributeAccessIssue]
            
            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()  # type: ignore[reportAttributeAccessIssue]
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return redirect(url_for('auth.register'))
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new user
        new_user = User(
            username=username,  # type: ignore[reportAttributeAccessIssue]
            email=email,  # type: ignore[reportAttributeAccessIssue]
            password_hash=generate_password_hash(password)  # type: ignore[reportAttributeAccessIssue]
        )  # type: ignore[reportGeneralTypeIssues]
        
        db.session.add(new_user)  # type: ignore[reportAttributeAccessIssue]
        db.session.commit()  # type: ignore[reportAttributeAccessIssue]
        
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@auth.route('/history')
@login_required
def history():
    searches = SearchHistory.query.filter_by(user_id=current_user.id).order_by(
        SearchHistory.created_at.desc()).all()
    return render_template('history.html', searches=searches)
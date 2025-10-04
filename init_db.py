"""
Database initialization script for YouTube Sentiment Analysis application
"""
import os
import sys
from youtube_sentiment.models import db, User
from youtube_sentiment.app import create_app
from werkzeug.security import generate_password_hash

def init_db():
    """Initialize the database and create tables"""
    # Create the Flask app
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if admin user exists, create if not
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',  # type: ignore[reportCallIssue]
                email='admin@example.com',  # type: ignore[reportCallIssue]
                password_hash=generate_password_hash('admin123'),  # type: ignore[reportCallIssue]
                is_active=True  # type: ignore[reportCallIssue]
            )
            db.session.add(admin_user)  # type: ignore[reportAttributeAccessIssue]
            db.session.commit()  # type: ignore[reportAttributeAccessIssue]
            print("Admin user created successfully!")
            print("Username: admin")
            print("Password: admin123")
        else:
            print("Admin user already exists!")

if __name__ == '__main__':
    init_db()
"""
Database models for YouTube Sentiment Analysis application
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):  # type: ignore[reportGeneralTypeIssues]
    id = db.Column(db.Integer, primary_key=True)  # type: ignore[reportAttributeAccessIssue]
    username = db.Column(db.String(80), unique=True, nullable=False)  # type: ignore[reportAttributeAccessIssue]
    email = db.Column(db.String(120), unique=True, nullable=False)  # type: ignore[reportAttributeAccessIssue]
    password_hash = db.Column(db.String(120), nullable=False)  # type: ignore[reportAttributeAccessIssue]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # type: ignore[reportAttributeAccessIssue]
    last_login = db.Column(db.DateTime, nullable=True)  # type: ignore[reportAttributeAccessIssue]
    is_active = db.Column(db.Boolean, default=True)  # type: ignore[reportAttributeAccessIssue]
    
    # Relationships
    searches = db.relationship('SearchHistory', backref='user', lazy=True, cascade='all, delete-orphan')  # type: ignore[reportAttributeAccessIssue]
    login_history = db.relationship('LoginHistory', backref='user', lazy=True, cascade='all, delete-orphan')  # type: ignore[reportAttributeAccessIssue]

    def __repr__(self):
        return f'<User {self.username}>'

class SearchHistory(db.Model):  # type: ignore[reportGeneralTypeIssues]
    id = db.Column(db.Integer, primary_key=True)  # type: ignore[reportAttributeAccessIssue]
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # type: ignore[reportAttributeAccessIssue]
    youtube_url = db.Column(db.String(500), nullable=False)  # type: ignore[reportAttributeAccessIssue]
    video_id = db.Column(db.String(50), nullable=False)  # type: ignore[reportAttributeAccessIssue]
    title = db.Column(db.String(200), nullable=True)  # type: ignore[reportAttributeAccessIssue]
    total_comments = db.Column(db.Integer, nullable=False)  # type: ignore[reportAttributeAccessIssue]
    sentiment_distribution = db.Column(db.Text, nullable=False)  # type: ignore[reportAttributeAccessIssue]
    language_distribution = db.Column(db.Text, nullable=False)   # type: ignore[reportAttributeAccessIssue]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # type: ignore[reportAttributeAccessIssue]
    
    # Relationships
    comments = db.relationship('CommentAnalysis', backref='search', lazy=True, cascade='all, delete-orphan')  # type: ignore[reportAttributeAccessIssue]

    def __repr__(self):
        return f'<SearchHistory {self.video_id}>'

class CommentAnalysis(db.Model):  # type: ignore[reportGeneralTypeIssues]
    id = db.Column(db.Integer, primary_key=True)  # type: ignore[reportAttributeAccessIssue]
    search_id = db.Column(db.Integer, db.ForeignKey('search_history.id'), nullable=False)  # type: ignore[reportAttributeAccessIssue]
    comment_id = db.Column(db.String(100), nullable=False)  # type: ignore[reportAttributeAccessIssue]
    author = db.Column(db.String(100), nullable=False)  # type: ignore[reportAttributeAccessIssue]
    text = db.Column(db.Text, nullable=False)  # type: ignore[reportAttributeAccessIssue]
    original_language = db.Column(db.String(10), nullable=False)  # type: ignore[reportAttributeAccessIssue]
    sentiment = db.Column(db.String(20), nullable=False)  # type: ignore[reportAttributeAccessIssue]
    polarity = db.Column(db.Float, nullable=False)  # type: ignore[reportAttributeAccessIssue]
    is_toxic = db.Column(db.Boolean, default=False)  # type: ignore[reportAttributeAccessIssue]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # type: ignore[reportAttributeAccessIssue]

    def __repr__(self):
        return f'<CommentAnalysis {self.comment_id}>'

class LoginHistory(db.Model):  # type: ignore[reportGeneralTypeIssues]
    id = db.Column(db.Integer, primary_key=True)  # type: ignore[reportAttributeAccessIssue]
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # type: ignore[reportAttributeAccessIssue]
    login_time = db.Column(db.DateTime, default=datetime.utcnow)  # type: ignore[reportAttributeAccessIssue]
    ip_address = db.Column(db.String(45), nullable=True)  # type: ignore[reportAttributeAccessIssue]
    user_agent = db.Column(db.Text, nullable=True)  # type: ignore[reportAttributeAccessIssue]

    def __repr__(self):
        return f'<LoginHistory user_id={self.user_id} time={self.login_time}>'
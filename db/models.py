# models.py - должно быть так:
from . import db
from flask_login import UserMixin
from datetime import datetime

class users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(162), nullable=False)
    
    # Flask-Login методы
    @property
    def is_active(self):
        return True
    
    @property 
    def is_authenticated(self):
        return True if self.id else False
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

class articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(50), nullable=False)
    article_text = db.Column(db.Text, nullable=False)
    is_favorite = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=False)
    likes = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)  # ← Добавьте эту строку
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # ← И эту
from . import db
from flask_login import UserMixin

class users(db.Model, UserMixin):  # ← ВАЖНО: UserMixin добавляет is_active
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(162), nullable=False)
    
    # Flask-Login требует эти свойства
    @property
    def is_active(self):
        """Все пользователи активны по умолчанию"""
        return True
    
    @property 
    def is_authenticated(self):
        """Пользователь аутентифицирован"""
        return True if self.id else False
    
    @property
    def is_anonymous(self):
        """Это не анонимный пользователь"""
        return False
    
    def get_id(self):
        """Возвращает ID как строку"""
        return str(self.id)

class articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(50), nullable=False)
    article_text = db.Column(db.Text, nullable=False)
    is_favorite = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=False)
    likes = db.Column(db.Integer, default=0)
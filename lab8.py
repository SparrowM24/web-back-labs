from flask import Blueprint, render_template, request, redirect, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from db.models import users, articles
from sqlalchemy import or_

# ОШИБКА: Blueprint и функция имеют одинаковое имя 'lab8'
# Blueprint должен иметь другое имя
lab8_bp = Blueprint('lab8', __name__)  # ← ИЗМЕНИТЕ НА lab8_bp

# Главная страница лабораторной 8
@lab8_bp.route('/lab8/')  # ← ИСПОЛЬЗУЙТЕ lab8_bp
def lab8_index():  # ← ИЗМЕНИТЕ ИМЯ ФУНКЦИИ
    return render_template('lab8/lab8.html')

# Регистрация
@lab8_bp.route('/lab8/register/', methods=['GET', 'POST'])  # ← lab8_bp
def register():
    if request.method == 'GET':
        return render_template('lab8/register.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    
    # Проверка а): имя пользователя не должно быть пустым
    if not login_form or login_form.strip() == '':
        return render_template('lab8/register.html',
                            error='Имя пользователя не может быть пустым')
    
    # Проверка б): пароль не должен быть пустым
    if not password_form or password_form.strip() == '':
        return render_template('lab8/register.html',
                            error='Пароль не может быть пустым')
    
    # Проверка существования пользователя
    login_exists = users.query.filter_by(login=login_form).first()
    if login_exists:
        return render_template('lab8/register.html',
                            error='Такой пользователь уже существует')

    # Создание нового пользователя
    password_hash = generate_password_hash(password_form)
    new_user = users(login=login_form, password=password_hash)
    db.session.add(new_user)
    db.session.commit()
    
    # Автоматический логин после регистрации
    login_user(new_user, remember=False)
    session['login'] = login_form
    
    return redirect('/lab8/')

# Вход в систему
@lab8_bp.route('/lab8/login/', methods=['GET', 'POST'])  # ← lab8_bp
def login():
    if request.method == 'GET':
        return render_template('lab8/login.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    remember_me = request.form.get('remember') == 'on'
    
    # Проверка логина на непустое значение
    if not login_form or login_form.strip() == '':
        return render_template('lab8/login.html',
                            error='Логин не может быть пустым')
    
    # Проверка пароля на непустое значение
    if not password_form or password_form.strip() == '':
        return render_template('lab8/login.html',
                            error='Пароль не может быть пустым')
    
    # Поиск пользователя
    user = users.query.filter_by(login=login_form).first()

    if user:
        if check_password_hash(user.password, password_form):
            login_user(user, remember=remember_me)
            session['login'] = login_form
            return redirect('/lab8/')

    return render_template('lab8/login.html',
                        error='Ошибка входа: логин и/или пароль неверны')

# Выход из системы
@lab8_bp.route('/lab8/logout/')  # ← lab8_bp
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect('/lab8/')

# Список статей
@lab8_bp.route('/lab8/articles/')  # ← lab8_bp
@login_required
def article_list():
    # Статьи текущего пользователя
    user_articles = articles.query.filter_by(login_id=current_user.id).all()
    
    # Публичные статьи других пользователей
    public_articles = articles.query.filter(
        articles.is_public == True,
        articles.login_id != current_user.id
    ).all()
    
    return render_template('lab8/articles.html',
                          user_articles=user_articles,
                          public_articles=public_articles)

# Создание статьи
@lab8_bp.route('/lab8/create_article/', methods=['GET', 'POST'])  # ← lab8_bp
@login_required
def create_article():
    if request.method == 'GET':
        return render_template('lab8/create_article.html')
    
    title = request.form.get('title')
    article_text = request.form.get('article_text')
    is_public = request.form.get('is_public') == 'on'
    
    if not title or not article_text:
        return render_template('lab8/create_article.html',
                             error='Заполните все обязательные поля')
    
    new_article = articles(
        login_id=current_user.id,
        title=title,
        article_text=article_text,
        is_public=is_public,
        likes=0,
        is_favorite=False
    )
    
    db.session.add(new_article)
    db.session.commit()
    
    return redirect('/lab8/articles/')

# Редактирование статьи
@lab8_bp.route('/lab8/edit_article/<int:article_id>/', methods=['GET', 'POST'])  # ← lab8_bp
@login_required
def edit_article(article_id):
    article = articles.query.get_or_404(article_id)
    
    # Проверяем, принадлежит ли статья текущему пользователю
    if article.login_id != current_user.id:
        return redirect('/lab8/articles/')
    
    if request.method == 'GET':
        return render_template('lab8/edit_article.html', article=article)
    
    title = request.form.get('title')
    article_text = request.form.get('article_text')
    is_public = request.form.get('is_public') == 'on'
    
    if not title or not article_text:
        return render_template('lab8/edit_article.html',
                             article=article,
                             error='Заполните все обязательные поля')
    
    article.title = title
    article.article_text = article_text
    article.is_public = is_public
    
    db.session.commit()
    
    return redirect('/lab8/articles/')

# Удаление статьи
@lab8_bp.route('/lab8/delete_article/<int:article_id>/', methods=['POST'])  # ← lab8_bp
@login_required
def delete_article(article_id):
    article = articles.query.get_or_404(article_id)
    
    # Проверяем, принадлежит ли статья текущему пользователю
    if article.login_id != current_user.id:
        return redirect('/lab8/articles/')
    
    db.session.delete(article)
    db.session.commit()
    
    return redirect('/lab8/articles/')
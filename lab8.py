from flask import Blueprint, render_template, request, redirect, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from db.models import users, articles

# Blueprint с правильным именем
lab8_bp = Blueprint('lab8_bp', __name__)

# Главная страница лабораторной 8
@lab8_bp.route('/lab8/')
def lab8_index():
    return render_template('lab8/lab8.html')

# Регистрация
@lab8_bp.route('/lab8/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab8/register.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    
    if not login_form or login_form.strip() == '':
        return render_template('lab8/register.html',
                            error='Имя пользователя не может быть пустым')
    
    if not password_form or password_form.strip() == '':
        return render_template('lab8/register.html',
                            error='Пароль не может быть пустым')
    
    login_exists = users.query.filter_by(login=login_form).first()
    if login_exists:
        return render_template('lab8/register.html',
                            error='Такой пользователь уже существует')

    password_hash = generate_password_hash(password_form)
    new_user = users(login=login_form, password=password_hash)
    db.session.add(new_user)
    db.session.commit()
    
    login_user(new_user, remember=False)
    session['login'] = login_form
    
    return redirect('/lab8/')

# Вход в систему
@lab8_bp.route('/lab8/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab8/login.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    remember_me = request.form.get('remember') == 'on'
    
    if not login_form or login_form.strip() == '':
        return render_template('lab8/login.html',
                            error='Логин не может быть пустым')
    
    if not password_form or password_form.strip() == '':
        return render_template('lab8/login.html',
                            error='Пароль не может быть пустым')
    
    user = users.query.filter_by(login=login_form).first()

    if user:
        if check_password_hash(user.password, password_form):
            login_user(user, remember=remember_me)
            session['login'] = login_form
            return redirect('/lab8/')

    return render_template('lab8/login.html',
                        error='Ошибка входа: логин и/или пароль неверны')

# Выход из системы
@lab8_bp.route('/lab8/logout/')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect('/lab8/')

# Список статей с поиском - ПРОСТОЙ И РАБОЧИЙ ВАРИАНТ
@lab8_bp.route('/lab8/articles/')
def article_list():
    """Список статей с поиском - доступен всем пользователям"""
    
    search_query = request.args.get('search', '').strip()
    
    if current_user.is_authenticated:
        # Для авторизованных пользователей
        if search_query:
            search_lower = search_query.lower()
            
            # Получаем ВСЕ свои статьи и фильтруем вручную
            all_my_articles = articles.query.filter_by(login_id=current_user.id).all()
            user_articles = [
                article for article in all_my_articles
                if search_lower in article.title.lower() or search_lower in article.article_text.lower()
            ]
            
            # Получаем ВСЕ публичные статьи других и фильтруем вручную
            all_other_public = articles.query.filter(
                articles.is_public == True,
                articles.login_id != current_user.id
            ).all()
            public_articles = [
                article for article in all_other_public
                if search_lower in article.title.lower() or search_lower in article.article_text.lower()
            ]
            
            all_public_articles = []
            search_results_count = len(user_articles) + len(public_articles)
        else:
            # Без поиска - просто все статьи
            user_articles = articles.query.filter_by(login_id=current_user.id).all()
            public_articles = articles.query.filter(
                articles.is_public == True,
                articles.login_id != current_user.id
            ).all()
            all_public_articles = []
            search_results_count = 0
    else:
        # Для неавторизованных пользователей
        if search_query:
            search_lower = search_query.lower()
            
            # Получаем ВСЕ публичные статьи и фильтруем вручную
            all_public = articles.query.filter_by(is_public=True).all()
            all_public_articles = [
                article for article in all_public
                if search_lower in article.title.lower() or search_lower in article.article_text.lower()
            ]
            
            user_articles = []
            public_articles = []
            search_results_count = len(all_public_articles)
        else:
            # Без поиска - просто все публичные статьи
            all_public_articles = articles.query.filter_by(is_public=True).all()
            user_articles = []
            public_articles = []
            search_results_count = 0
    
    def get_author_name(article_id):
        author = users.query.get(article_id)
        return author.login if author else 'Неизвестно'
    
    return render_template('lab8/articles.html',
                          user_articles=user_articles,
                          public_articles=public_articles,
                          all_public_articles=all_public_articles,
                          search_query=search_query,
                          search_results_count=search_results_count,
                          get_author_name=get_author_name,
                          current_user=current_user)

# Просмотр отдельной статьи
@lab8_bp.route('/lab8/article/<int:article_id>/')
def view_article(article_id):
    article = articles.query.get_or_404(article_id)
    
    if not article.is_public:
        if not current_user.is_authenticated or article.login_id != current_user.id:
            return "Статья недоступна", 403
    
    author = users.query.get(article.login_id)
    
    return render_template('lab8/view_article.html',
                          article=article,
                          author=author)

# Создание статьи
@lab8_bp.route('/lab8/create_article/', methods=['GET', 'POST'])
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
        is_favorite=False
    )
    
    db.session.add(new_article)
    db.session.commit()
    
    return redirect('/lab8/articles/')

# Редактирование статьи
@lab8_bp.route('/lab8/edit_article/<int:article_id>/', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    article = articles.query.get_or_404(article_id)
    
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
@lab8_bp.route('/lab8/delete_article/<int:article_id>/', methods=['POST'])
@login_required
def delete_article(article_id):
    article = articles.query.get_or_404(article_id)
    
    if article.login_id != current_user.id:
        return redirect('/lab8/articles/')
    
    db.session.delete(article)
    db.session.commit()
    
    return redirect('/lab8/articles/')

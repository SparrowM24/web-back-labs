from flask import Blueprint, render_template, request, redirect, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from db.models import users, articles
from sqlalchemy import or_, func

# Blueprint с правильным именем
lab8_bp = Blueprint('lab8_bp', __name__)

# Вспомогательная функция для регистронезависимого поиска
def case_insensitive_like(column, pattern):
    """
    Универсальная функция для регистронезависимого поиска.
    Работает как с SQLite, так и с другими базами данных.
    """
    return func.lower(column).contains(func.lower(pattern))

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

# Список статей с поиском
@lab8_bp.route('/lab8/articles/')
def article_list():
    """Список статей с поиском - доступен всем пользователям"""
    
    search_query = request.args.get('search', '').strip()
    
    user_articles = []
    public_articles = []
    all_public_articles = []
    search_results_count = 0
    
    if current_user.is_authenticated:
        user_query = articles.query.filter_by(login_id=current_user.id)
        
        public_query = articles.query.filter(
            articles.is_public == True,
            articles.login_id != current_user.id
        )
        
        if search_query:
            user_query = user_query.filter(
                or_(
                    case_insensitive_like(articles.title, search_query),
                    case_insensitive_like(articles.article_text, search_query)
                )
            )
            
            public_query = public_query.filter(
                or_(
                    case_insensitive_like(articles.title, search_query),
                    case_insensitive_like(articles.article_text, search_query)
                )
            )
            
            search_results_count = user_query.count() + public_query.count()
        
        user_articles = user_query.all()
        public_articles = public_query.all()
        
    else:
        public_query = articles.query.filter_by(is_public=True)
        
        if search_query:
            public_query = public_query.filter(
                or_(
                    case_insensitive_like(articles.title, search_query),
                    case_insensitive_like(articles.article_text, search_query)
                )
            )
            search_results_count = public_query.count()
        
        all_public_articles = public_query.all()
    
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
    """Просмотр статьи - доступна публичная или своя"""
    article = articles.query.get_or_404(article_id)
    
    if not article.is_public:
        if not current_user.is_authenticated or article.login_id != current_user.id:
            return "Статья недоступна", 403
    
    author = users.query.get(article.login_id)
    
    # УБРАЛИ увеличение счетчика просмотров
    # article.views = (article.views or 0) + 1
    # db.session.commit()
    
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
        likes=0,
        is_favorite=False
        # УБРАЛИ views=0
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


# Быстрый поиск
@lab8_bp.route('/lab8/quick_search/', methods=['GET'])
def quick_search():
    """Быстрый поиск статей"""
    search_query = request.args.get('q', '').strip()
    
    if not search_query:
        return jsonify({'error': 'Введите поисковый запрос'}), 400
    
    results = []
    
    if current_user.is_authenticated:
        my_articles = articles.query.filter(
            articles.login_id == current_user.id,
            or_(
                case_insensitive_like(articles.title, search_query),
                case_insensitive_like(articles.article_text, search_query)
            )
        ).limit(5).all()
        
        other_articles = articles.query.filter(
            articles.is_public == True,
            articles.login_id != current_user.id,
            or_(
                case_insensitive_like(articles.title, search_query),
                case_insensitive_like(articles.article_text, search_query)
            )
        ).limit(5).all()
        
        for article in my_articles + other_articles:
            author = users.query.get(article.login_id)
            results.append({
                'id': article.id,
                'title': article.title,
                'preview': article.article_text[:100] + '...' if len(article.article_text) > 100 else article.article_text,
                'author': author.login if author else 'Неизвестно',
                'is_mine': article.login_id == current_user.id,
                'url': f'/lab8/article/{article.id}/'
            })
    
    else:
        public_articles = articles.query.filter(
            articles.is_public == True,
            or_(
                case_insensitive_like(articles.title, search_query),
                case_insensitive_like(articles.article_text, search_query)
            )
        ).limit(10).all()
        
        for article in public_articles:
            author = users.query.get(article.login_id)
            results.append({
                'id': article.id,
                'title': article.title,
                'preview': article.article_text[:100] + '...' if len(article.article_text) > 100 else article.article_text,
                'author': author.login if author else 'Неизвестно',
                'is_mine': False,
                'url': f'/lab8/article/{article.id}/'
            })
    
    return jsonify({
        'query': search_query,
        'count': len(results),
        'results': results
    })

# Статистика статей пользователя
@lab8_bp.route('/lab8/stats/')
@login_required
def stats():
    """Статистика пользователя"""
    user_stats = {
        'total_articles': articles.query.filter_by(login_id=current_user.id).count(),
        'public_articles': articles.query.filter_by(login_id=current_user.id, is_public=True).count(),
        'private_articles': articles.query.filter_by(login_id=current_user.id, is_public=False).count(),
        # УБРАЛИ total_likes и total_views
    }
    
    return render_template('lab8/stats.html', stats=user_stats)
from flask import Blueprint, render_template, request, make_response, redirect, session, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from os import path

lab5 = Blueprint('lab5', __name__)

@lab5.route('/lab5/')
def lab():
    user_login = session.get('login', "Anonymous")  # Используем другое имя
    return render_template('lab5/lab5.html', login=user_login)

def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        conn = psycopg2.connect(
                host = '127.0.0.1',
                database = 'alice_dyachkova_knowledge_base',
                user = 'alice_dyachkova_knowledge_base',
                password = '123456'
        )
        cur = conn.cursor(cursor_factory= RealDictCursor)
    else:
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

    return conn, cur


def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

@lab5.route('/lab5/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab5/register.html')
    login = request.form.get('login')
    password = request.form.get('password')
    full_name = request.form.get('full_name')
    if not login or not password or not full_name:
        return render_template('lab5/register.html', error='Заполните все поля')

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT login FROM users WHERE login=%s;", (login, ))
    else:
        cur.execute("SELECT login FROM users WHERE login=?;", (login, ))

    if cur.fetchone():
        db_close(conn, cur)
        return render_template('lab5/register.html', error='Такой пользователь уже существует!')
    password_hash = generate_password_hash(password)
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("INSERT INTO users (login, password, full_name) VALUES (%s, %s, %s);", (login, password_hash, full_name))
    else:
        cur.execute("INSERT INTO users (login, password, full_name) VALUES (?, ?, ?);", (login, password_hash, full_name))

    db_close(conn, cur)
    return render_template('lab5/success.html', login=login)


@lab5.route('/lab5/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('lab5/login.html')

    login = request.form.get('login')
    password = request.form.get('password')

    if not login or not password:
        return render_template('lab5/login.html', error='Заполните поля')

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute(f"SELECT * FROM users WHERE login=%s;",(login, ))
    else:
        cur.execute(f"SELECT * FROM users WHERE login=?;",(login, ))

    user = cur.fetchone()

    if not user:
        db_close(conn, cur)
        return render_template('/lab5/login.html', error='Логин и/или пароль неверны')
    if not check_password_hash(user['password'], password):
        db_close(conn, cur)
        return render_template('lab5/login.html', error='Логин и/или пароль неверны')

    session['login'] = login
    db_close(conn, cur)
    return render_template('lab5/success_login.html', login=login)


@lab5.route('/lab5/create', methods = ['GET', 'POST'])
def create():
    login=session.get('login')
    if not login:
        return redirect('/lab5/login')

    if request.method == 'GET':
        return render_template('lab5/create_article.html')

    title = request.form.get('title')
    article_text = request.form.get('article_text')

    is_public = request.form.get('is_public') == 'on'

    if not title or not article_text:
        return render_template('lab5/create_article.html', error='Заполните все поля!')

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM users WHERE login=%s;", (login, ))
    else:
        cur.execute("SELECT * FROM users WHERE login=?;", (login, ))

    login_id = cur.fetchone()['id']

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("INSERT INTO articles (login_id, title, article_text, is_public) VALUES (%s, %s, %s, %s);",
                    (login_id, title, article_text, is_public))
    else:
        cur.execute("INSERT INTO articles (login_id, title, article_text, is_public) VALUES (?, ?, ?, ?);",
                   (login_id, title, article_text, is_public))

    db_close(conn, cur)
    return redirect('/lab5/list')


@lab5.route('/lab5/list')
def list():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute(f"SELECT id FROM users WHERE login=%s;",(login, ))
    else:
        cur.execute(f"SELECT id FROM users WHERE login=?;",(login, ))

    login_id = cur.fetchone()["id"]

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute(f"SELECT * FROM articles WHERE login_id=%s ORDER BY is_favorite DESC, id;", (login_id, ))
    else:
        cur.execute(f"SELECT * FROM articles WHERE login_id=? ORDER BY is_favorite DESC, id;", (login_id, ))

    articles = cur.fetchall()

    db_close(conn, cur)
    return render_template('lab5/articles.html', articles=articles)


@lab5.route('/lab5/logout')
def logout():
    session.pop('login', None)
    return redirect('/lab5')

@lab5.route('/lab5/delete/<int:article_id>', methods=['POST'])
def delete(article_id):
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("DELETE FROM articles WHERE id=%s;", (article_id, ))
    else:
        cur.execute("DELETE FROM articles WHERE id=?;", (article_id, ))

    db_close(conn, cur)
    return redirect('/lab5/list')


@lab5.route('/lab5/edit/<int:article_id>', methods=['GET', 'POST'])
def edit(article_id):
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    if request.method == 'GET':
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT * FROM articles WHERE id=%s;", (article_id, ))
        else:
            cur.execute("SELECT * FROM articles WHERE id=?;", (article_id, ))

        article = cur.fetchone()
        db_close(conn, cur)
        return render_template('lab5/edit_article.html', article=article)

    else:
        title = request.form.get('title')
        article_text = request.form.get('article_text')

        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("UPDATE articles SET title=%s, article_text=%s WHERE id=%s;",
                       (title, article_text, article_id))
        else:
            cur.execute("UPDATE articles SET title=?, article_text=? WHERE id=?;",
                       (title, article_text, article_id))

        db_close(conn, cur)
        return redirect('/lab5/list')


@lab5.route('/lab5/users')
def users():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id, login, full_name FROM users ORDER BY id;")
    else:
        cur.execute("SELECT id, login, full_name FROM users ORDER BY id;")

    users = cur.fetchall()
    db_close(conn, cur)

    return render_template('lab5/users.html', users=users, login=login)


@lab5.route('/lab5/change')
def change():
    if not session.get('login'):
        return redirect('/lab5/login')

    return render_template('lab5/change.html')

@lab5.route('/lab5/update', methods=['POST'])
def update():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    new_name = request.form.get('name')
    password = request.form.get('password')
    confirm = request.form.get('confirm')

    if password != confirm:
        return render_template('lab5/change.html', error='Пароли не совпадают')

    conn, cur = db_connect()

    if password:
        password_hash = generate_password_hash(password)
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("UPDATE users SET full_name=%s, password=%s WHERE login=%s",
                       (new_name, password_hash, login))
        else:
            cur.execute("UPDATE users SET full_name=?, password=? WHERE login=?",
                       (new_name, password_hash, login))
    else:
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("UPDATE users SET full_name=%s WHERE login=%s", (new_name, login))
        else:
            cur.execute("UPDATE users SET full_name=? WHERE login=?", (new_name, login))

    db_close(conn, cur)
    return render_template('lab5/change.html', error='Данные изменены!')


@lab5.route('/lab5/favorite/<int:article_id>', methods=['POST'])
def favorite(article_id):
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT is_favorite FROM articles WHERE id=%s;", (article_id,))
    else:
        cur.execute("SELECT is_favorite FROM articles WHERE id=?;", (article_id,))

    article = cur.fetchone()
    if article:
        new_favorite = not article['is_favorite']

        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("UPDATE articles SET is_favorite=%s WHERE id=%s;", (new_favorite, article_id))
        else:
            cur.execute("UPDATE articles SET is_favorite=? WHERE id=?;", (new_favorite, article_id))

    db_close(conn, cur)
    return redirect('/lab5/list')

@lab5.route('/lab5/public')
def public_articles():
    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM articles WHERE is_public=true;")
    else:
        cur.execute("SELECT * FROM articles WHERE is_public=1;")

    articles = cur.fetchall()
    db_close(conn, cur)

    if not articles:
        return render_template('lab5/public.html', articles=[], error="Публичных статей нет")

    return render_template('lab5/public.html', articles=articles)
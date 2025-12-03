from flask import Blueprint, render_template, request, make_response, redirect, session, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from os import path

lab5 = Blueprint('lab5', __name__)

@lab5.route('/lab5/')
def main():
    return render_template('/lab5/lab5.html')

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
def list_articles():
    return "Список статей"
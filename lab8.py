from flask import Blueprint, render_template, redirect
from db import db
from db.models import users, articles

lab8 = Blueprint('lab8', __name__)

@lab8.route('/')
def main():
    username = 'anonymous'  # Пока фиксированное значение
    return render_template('lab8/lab8.html', username=username)


@lab8.route('/lab8/register/', methods=['GET', 'POST'])
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
    
    login_exists = users.query.filter_by(login=login_form).first()
    if login_exists:
        return render_template('lab8/register.html',
                            error='Такой пользователь уже существует')

    password_hash = generate_password_hash(password_form)
    new_user = users(login=login_form, password=password_hash)
    db.session.add(new_user)
    db.session.commit()
    return redirect('/lab8/')

@lab8.route('/login')
def login():
    return render_template('login.html')


@lab8.route('/articles')
def articles():
    return render_template('articles.html')


@lab8.route('/create')
def create():
    return render_template('create.html')
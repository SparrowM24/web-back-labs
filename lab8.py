from flask import Blueprint, render_template

lab8 = Blueprint('lab8', __name__)

@lab8.route('/')
def main():
    username = 'anonymous'  # Пока фиксированное значение
    return render_template('lab8/lab8.html', username=username)

@lab8.route('/login')
def login():
    return render_template('login.html')

@lab8.route('/register')
def register():
    return render_template('register.html')

@lab8.route('/articles')
def articles():
    return render_template('articles.html')

@lab8.route('/create')
def create():
    return render_template('create.html')
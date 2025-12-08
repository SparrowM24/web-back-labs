from flask import Flask, url_for, request
import datetime
import os
from os import path
from flask_sqlalchemy import SQLAlchemy
from db import db
from db.models import users
from flask_login import LoginManager


from lab1 import lab1
from lab2 import lab2
from lab3 import lab3
from lab4 import lab4
from lab5 import lab5
from lab6 import lab6
from lab7 import lab7
from lab8 import lab8_bp


app = Flask(__name__)


login_manager = LoginManager()
login_manager.login_view = 'lab8_bp.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_users(login_id):
    return users.query.get(int(login_id))

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'секретно секретный-секрет')
app.config['DB_TYPE'] = os.getenv('DB_TYPE', 'postgres')

if app.config['DB_TYPE'] == 'postgres':
    db_name = 'alice_dyachkova_orm'
    db_user = 'alice_dyachkova_orm'
    db_password = '123'
    host_ip = '127.0.0.1'
    host_port = 5433
    
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        f'postgresql://{db_user}:{db_password}@{host_ip}:{host_port}/{db_name}'

else:
    import os.path as path
    dir_path = path.dirname(path.realpath(__file__))
    db_path = path.join(dir_path, "alice_dyachkova_orm.db")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db.init_app(app)

app.register_blueprint(lab1)
app.register_blueprint(lab2)
app.register_blueprint(lab3)
app.register_blueprint(lab4)
app.register_blueprint(lab5)
app.register_blueprint(lab6)
app.register_blueprint(lab7)
app.register_blueprint(lab8_bp)

log = []
@app.errorhandler(404)
def not_found(err):
    global log
    ip = request.remote_addr
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    url = request.url
    log.append(f"[Время:{time}, пользователь-{ip}] зашел на адрес: {url}")
    path = url_for("static", filename="404.gif")
    style = url_for('static', filename="lab1.css")

    list_items = ""
    for i in log:
        list_items += f"<li>{i}</li>"
    
    return '''
<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="''' + style + '''">
    </head>
    <body>
        <h1>Страница пропала при загадочных обстоятельствах. Следствие ведётся...</h1>
        <img src="''' + path + '''">
        <div style="width: 700px; margin: 0 auto;">
            <h3>Журнал:</h3>
            <ul>
            ''' + list_items + '''
            </ul>
        </div>
    </body>
</html>
'''


@app.route("/")
@app.route("/index")
def index():
    return """
<!DOCTYPE html>
<html>
    <head>
        <title>НГТУ, ФБ, Лабораторные работы</title>
    </head>
    <body>
        <header> 
            НГТУ, ФБ, WEB-программирование, часть 2. Список лабораторных
        </header>
        <a href="/lab1">Первая лабораторная</a> <br>
        <a href="/lab2">Вторая лабораторная</a> <br>
        <a href="/lab3">Третья лабораторная</a> <br>
        <a href="/lab4">Четвертая лабораторная</a> <br>
        <a href="/lab5">Пятая лабораторная</a> <br>
        <a href="/lab6">Шестая лабораторная</a> <br>
        <a href="/lab7">Седьмая лабораторная</a> <br>
        <a href="/lab8">Восьмая лабораторная</a> <br>
        <footer>
            Дьячкова Алиса Дмитриевна ФБИ-32 3 Курс 2025
        </footer>
    </body>
</html>"""


@app.errorhandler(500)
def error_500(err):
    return '''
    <!DOCTYPE html>
    <html>
    <body>
        <h1>500 - Internal Server Error</h1>
        <p>Внутренняя ошибка сервера</p>
        <p>
        Произошла непредвиденная ошибка на сервере. 
        Пожалуйста, попробуйте обновить страницу или вернуться позже.
        Если проблема сохраняется, свяжитесь с администратором сайта.
        </p>
        <a href="/lab1">Вернуться на главную</a>
    </body>
    </html>
    ''', 500


from flask import Flask, url_for, request, redirect
import datetime
app = Flask(__name__)

@app.errorhandler(404)
def not_found(err):
    return "нет такой страницы", 404

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
        <a href="/lab1">Первая лабораторная</a>
        <footer>
            Дьячкова Алиса Дмитриевна ФБИ-32 3 Курс 2025
        </footer>
    </body>
</html>"""

@app.route("/lab1")
def lab_1():
    return """
<!DOCTYPE html>
<html>
    <head>
        <title>Лабораторная 1</title>
    </head>
    <body>
        <p>
        Flask — фреймворк для создания веб-приложений на языке программирования Python, использующий набор 
        инструментов Werkzeug, а также шаблонизатор Jinja2. Относится к категории так называемых микрофреймворков 
        — минималистичных каркасов веб-приложений, сознательно предоставляющих лишь самые базовые возможности.
        </p>
        <a href="/">Назад</a>
    </body>
</html>"""

@app.route("/lab1/web")
def web():
    return '''<!DOCTYPE html>
        <html lang="en">
        <body>
            <h1>web-сервер на flask</h1>
            <a href="/author">author</a>
        </body>
        </html>''', 200, {
            "X-Server": "sample",
            "Content-Type": "text/plain; charset=utf-8"
        }

@app.route("/lab1/author")
def author():
    name = "Дьячкова Алиса Дмитриевна"
    group = "ФБИ-32"
    faculty = "ФБ"

    return """<!DOCTYPE html>
        <html>
            <body>
                <p>Студент: """ + name + """</p>
                <p>Группа: """ + group + """</p>
                <p>Факультет: """ + faculty + """</p>
                <a href="/web">web</a>
            </body>
        </html>"""

@app.route("/lab1/image")
def image():
    path = url_for("static", filename="oak.jpg")
    style = url_for('static', filename="lab1.css")
    return '''
<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="''' + style + '''">
    </head>
    <body>
        <h1>Дуб</h1>
        <img src="''' + path + '''">
    </body>
</html>
'''
count = 0
@app.route("/lab1/counter")
def counter():
    global count
    count += 1
    time = datetime.datetime.today()
    url = request.url
    client_ip = request.remote_addr

    return '''
<!DOCTYPE html>
<html>
    <body>
        Сколько раз вы сюда заходили ''' + str(count) + '''
        <hr>
        Дата и время: ''' + str(time) + '''<br>
        Запрошеный адрес: ''' + url + '''<br>
        Ваш адрес: ''' + client_ip + '''<br>
        <a href="/counter_cleaner">counter_cleaner</a>
    </body>
</html>
'''
@app.route("/lab1/counter_cleaner")
def counter_cleaner():
    global count
    count = 0
    return '''
<!DOCTYPE html>
<html>
    <body>
        <a href="/counter">counter</a>
    </body>
</html>
'''

@app.route("/lab1/info")
def info():
    return redirect("/author")

@app.route("/lab1/created")
def created():
    return '''
<!doctype html>
<html>
    <body>
        <h1>Создано успешно</h1>
        <div><i>что-то создано…</i></div>
    </body>
</html>
''', 201
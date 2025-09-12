from flask import Flask, url_for, request, redirect
import datetime
app = Flask(__name__)

@app.errorhandler(404)
def not_found(err):
    return "нет такой страницы", 404

@app.route("/web")
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

@app.route("/author")
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

@app.route("/image")
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
@app.route("/counter")
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
@app.route("/counter_cleaner")
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

@app.route("/info")
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
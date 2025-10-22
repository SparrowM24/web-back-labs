from flask import Blueprint, url_for, request, redirect
import datetime
lab1 = Blueprint('lab1', __name__)


@lab1.route("/lab1")
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
        
        <h2>Список роутов</h2>
        <ul>
            <li><a href="/">Главная страница</a></li>
            <li><a href="/index">Index (альтернативная главная)</a></li>
            <li><a href="/lab1">Лабораторная 1</a></li>
            <li><a href="/lab1/web">Web сервер</a></li>
            <li><a href="/lab1/author">Информация об авторе</a></li>
            <li><a href="/lab1/image">Изображение дуба</a></li>
            <li><a href="/lab1/counter">Счетчик посещений</a></li>
            <li><a href="/lab1/counter_cleaner">Сброс счетчика</a></li>
            <li><a href="/lab1/info">Редирект на автора</a></li>
            <li><a href="/lab1/created">Создано успешно (201)</a></li>
            <li><a href="/400">Ошибка 400</a></li>
            <li><a href="/401">Ошибка 401</a></li>
            <li><a href="/402">Ошибка 402</a></li>
            <li><a href="/403">Ошибка 403</a></li>
            <li><a href="/405">Ошибка 405</a></li>
            <li><a href="/418">Ошибка 418 (Я чайник)</a></li>
            <li><a href="/cause_error">Вызвать ошибку 500</a></li>
        </ul>
    </body>
</html>"""


@lab1.route("/lab1/web")
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


@lab1.route("/lab1/author")
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


@lab1.route("/lab1/image")
def image():
    path = url_for("static", filename="lab1/oak.jpg")
    style = url_for('static', filename="lab1/lab1.css")
    html_content = '''
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
    return html_content, 200, {
        'Content-Language': 'ru',
        'X-Custom-Header': 'MyCustomValue',
        'X-Server-Info': 'Flask/2.3.3',
        'Content-Type': 'text/html; charset=utf-8'
    }


count = 0
@lab1.route("/lab1/counter")
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


@lab1.route("/lab1/counter_cleaner")
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


@lab1.route("/lab1/info")
def info():
    return redirect("/author")


@lab1.route("/lab1/created")
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


@lab1.route("/400")
def Eror_400():
    return '''
    <!DOCTYPE html>
    <html>
    <body>
        <h1>400 - Bad Request</h1>
        <p>Сервер не может обработать запрос из-за некорректного синтаксиса.</p>
    </body>
    </html>
    ''', 400


@lab1.route("/401")
def Eror_401():
    return '''
    <!DOCTYPE html>
    <html>
    <body>
        <h1>401 - Unauthorized</h1>
        <p>Требуется аутентификация для доступа к ресурсу.</p>
    </body>
    </html>
    ''', 401


@lab1.route("/402")
def Eror_402():
    return '''
    <!DOCTYPE html>
    <html>
    <body>
        <h1>402 - Payment Required</h1>
        <p>Требуется оплата для доступа к ресурсу.</p>
    </body>
    </html>
    ''', 402


@lab1.route("/403")
def Eror_403():
    return '''
    <!DOCTYPE html>
    <html>
    <body>
        <h1>403 - Forbidden</h1>
        <p>Доступ к ресурсу запрещен.</p>
    </body>
    </html>
    ''', 403


@lab1.route("/405")
def Eror_405():
    return '''
    <!DOCTYPE html>
    <html>
    <body>
        <h1>405 - Method Not Allowed</h1>
        <p>Метод запроса не поддерживается для данного ресурса.</p>
    </body>
    </html>
    ''', 405


@lab1.route("/418")
def Eror_418():
    return '''
    <!DOCTYPE html>
    <html>
    <body>
        <h1>418 - I'm a teapot</h1>
        <p>Я чайник и не могу заваривать кофе.</p>
        <p>
        Ошибка 418 (HTTP 418, I'm a teapot) — шутливый код ответа, который появился в 
        спецификации HTTP 1 апреля 1998 года.Происхождение: документ RFC 2324 
        описывал протокол HTCPCP (Hyper Text Coffee Pot Control Protocol) для управления 
        кофеварками через HTTP. Поскольку дата публикации совпадала с 1 апреля, протокол 
        являлся первоапрельской шуткой. Суть: если сервер (в образе кофеварки) получает 
        запрос на приготовление кофе, но при этом является чайником, он должен вернуть 
        код ответа 418, означающий: «Я – чайник и не могу заварить кофе».
        </p>
    </body>
    </html>
    ''', 418


@lab1.route("/cause_error")
def cause_error():
    # Вызываем ошибку
    result = 10 / 0
    return "Эта строка никогда не будет показана"
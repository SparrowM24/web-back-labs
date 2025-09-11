from flask import Flask
app = Flask(__name__)

@app.route("/web")
def web():
    return '''<!DOCTYPE html>
        <html lang="en">
        <body>
            <h1>web-сервер на flask</h1>
            <a href="/author">author</a>
        </body>
        </html>'''

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

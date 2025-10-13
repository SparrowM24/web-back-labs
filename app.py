from flask import Flask, url_for, request, redirect, abort, render_template
import datetime
from lab1 import lab1

app = Flask(__name__)
app.register_blueprint(lab1)

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
        <a href="/lab2">Вторая лабораторная</a>
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


@app.route("/cause_error")
def cause_error():
    # Вызываем ошибку разными способами:
    
    # 1. Деление на ноль
    result = 10 / 0
    
    # 2. Конкатенация числа и строки
    result = "текст" + 123
    
    return "Эта строка никогда не будет показана"

@app.route('/lab2/a')
def a():
    return 'без слэша'

@app.route('/lab2/a/')
def a2():
    return 'со слешем'

@app.route('/lab2/example')
def example():
    name ="Дьячкова Алиса"
    lab_num = 2
    group = 'ФБИ-32'
    course = 3
    fruits = [
        {'name': 'яблоки', 'price': 100},
        {'name': 'груши', 'price': 120},
        {'name': 'апельсины', 'price': 80},
        {'name': 'мандарины', 'price': 95},
        {'name': 'манго', 'price': 321}
    ]
    return render_template('example.html',
                            name=name, lab_num=lab_num, group=group, course=course, fruits=fruits)

@app.route('/lab2/')
def lab2():
    return render_template('lab2.html')

@app.route('/lab2/filters')
def filters():
    phrase = "О <b>сколько</b> <u>нам</u> <i>открытий</i> чудных..."
    return render_template('filter.html', phrase = phrase)

flower_list = [
    {'name': 'роза', 'price': 150},
    {'name': 'тюльпан', 'price': 80},
    {'name': 'незабудка', 'price': 60},
    {'name': 'ромашка', 'price': 50}
]

@app.route('/lab2/flowers/<int:flower_id>')
def flowers(flower_id):
    if flower_id >= len(flower_list) or flower_id < 0:
        abort(404)
    else:
        flower = flower_list[flower_id]
        return f'''
<!DOCTYPE html>
<html>
<body>
    <h1>Информация о цветке</h1>
    <p>ID: {flower_id}</p>
    <p>Название: {flower['name']}</p>
    <p>Цена: {flower['price']} руб.</p>
    <a href="/lab2/flowers">Посмотреть все цветы</a>
</body>
</html>
'''
    
@app.route('/lab2/flowers')
def show_all_flowers():
    flowers_html = ""
    for i, flower in enumerate(flower_list):
        flowers_html += f'''
        <li>
            {flower['name']} - {flower['price']} руб.
            <form action="/lab2/delete_flower/{i}" method="POST" style="display: inline;">
                <button type="submit">Удалить</button>
            </form>
        </li>
        '''
    
    return f'''
<!DOCTYPE html>
<html>
<body>
    <h1>Все цветы</h1>
    <p>Общее количество цветов: {len(flower_list)}</p>
    <h2>Добавить новый цветок</h2>
    <form action="/lab2/add_flower" method="GET">
        <input type="text" name="name" placeholder="Название цветка" required>
        <input type="number" name="price" placeholder="Цена" min="1" required>
        <button type="submit">Добавить цветок</button>
    </form>
    <h2>Список цветов:</h2>
    <ul>
        {flowers_html if flower_list else "<li>Список цветов пуст</li>"}
    </ul>
    <form action="/lab2/clear_flowers" method="POST">
        <button type="submit">Очистить весь список цветов</button>
    </form>
</body>
</html>
'''

@app.route('/lab2/add_flower', methods=['GET'])
def add_flower():
    name = request.args.get('name')
    price = request.args.get('price', 100)
    if name:
        new_flower = {'name': name, 'price': int(price)}
        flower_list.append(new_flower)
        return f'''
<!DOCTYPE html>
<html>
<body>
    <h1>Новый цветок добавлен</h1>
    <p>Название: {name}</p>
    <p>Цена: {price} руб.</p>
    <p>Всего цветов: {len(flower_list)}</p>
    <a href="/lab2/flowers">Посмотреть все цветы</a>
</body>
</html>
'''
    else:
        abort(404)

@app.route('/lab2/delete_flower/<int:flower_id>', methods=['POST'])
def delete_flower(flower_id):
    if 0 <= flower_id < len(flower_list):
        flower_list.pop(flower_id)
    return redirect(url_for('show_all_flowers'))

@app.route('/lab2/clear_flowers', methods=['POST'])
def clear_flowers():
    flower_list.clear()
    return redirect(url_for('show_all_flowers'))

@app.route("/lab2/calc/<int:a>/<int:b>")
def calculator(a, b):
    return f'''
<!DOCTYPE html>
<html>
<body>
    {a} + {b} = {a+b} <br>
    {a} - {b} = {a-b} <br>
    {a} x {b} = {a*b} <br>
    {a}<sup>{b}</sup> = {a**b}
</body>
</html>
'''
@app.route('/lab2/calc/')
def calc_default():
    return redirect(url_for('calculator', a=1, b=1))

@app.route('/lab2/calc/<int:a>')
def calc_single(a):
    return redirect(url_for('calculator', a=a, b=1))

books = [
    {
        'author': 'В. Олифер, Н. Олифер',
        'title': 'Компьютерные сети. Принципы, технологии, протоколы. Учебник',
        'genre': 'Компьютерные сети',
        'pages': 2024
    },
    {
        'author': 'Э. Таненбаум, Д. Уэзеролл',
        'title': 'Компьютерные сети',
        'genre': 'Компьютерные сети',
        'pages': 960
    },
    {
        'author': 'Кристофер Дейт',
        'title': 'Введение в системы баз данных',
        'genre': 'Базы данных',
        'pages': 770
    },
    {
        'author': 'Владимир Комаров',
        'title': 'Путеводитель по базам данных',
        'genre': 'Базы данных',
        'pages': 350
    },
    {
        'author': 'Роберт Мартин',
        'title': 'Чистый код: создание, анализ и рефакторинг',
        'genre': 'Программирование',
        'pages': 464
    },
    {
        'author': 'Стив Макконнелл',
        'title': 'Совершенный код',
        'genre': 'Программирование',
        'pages': 896
    },
    {
        'author': 'Адитья Бхаргава',
        'title': 'Грокаем алгоритмы',
        'genre': 'Алгоритмы',
        'pages': 288
    },
    {
        'author': 'Томас Кормен',
        'title': 'Алгоритмы: построение и анализ',
        'genre': 'Алгоритмы',
        'pages': 1328
    },
    {
        'author': 'Эрик Фримен',
        'title': 'Паттерны проектирования',
        'genre': 'Программирование',
        'pages': 656
    },
    {
        'author': 'Эндрю Хант',
        'title': 'Программист-прагматик',
        'genre': 'Программирование',
        'pages': 352
    },
    {
        'author': 'Мартин Фаулер',
        'title': 'Рефакторинг: улучшение существующего кода',
        'genre': 'Программирование',
        'pages': 448
    },
    {
        'author': 'Дональд Кнут',
        'title': 'Искусство программирования',
        'genre': 'Программирование',
        'pages': 700
    }
]
@app.route('/lab2/books')
def show_books():
    return render_template('books.html', books=books)

berries = [
    {
        'name': 'Клубника',
        'description': 'Сладкая и сочная красная ягода, богатая витамином C.',
        'image': 'images/strawberry.jpg'
    },
    {
        'name': 'Малина',
        'description': 'Нежная ароматная ягода, часто используемая в десертах.',
        'image': 'images/raspberry.jpg'
    },
    {
        'name': 'Черника',
        'description': 'Маленькая тёмная ягода, полезна для зрения.',
        'image': 'images/blueberry.jpg'
    },
    {
        'name': 'Ежевика',
        'description': 'Близкая родственница малины с терпким вкусом.',
        'image': 'images/blackberry.jpg'
    },
    {
        'name': 'Голубика',
        'description': 'Крупная синяя ягода, растущая на кустарниках.',
        'image': 'images/bilberry.jpg'
    },
    {
        'name': 'Смородина',
        'description': 'Бывает красной, чёрной и белой, очень богата витаминами.',
        'image': 'images/currant.jpg'
    },
    {
        'name': 'Крыжовник',
        'description': 'Зелёная или розовая ягода с освежающим вкусом.',
        'image': 'images/gooseberry.jpg'
    },
    {
        'name': 'Клюква',
        'description': 'Кислая красная ягода, растущая на болотах.',
        'image': 'images/cranberry.jpg'
    },
    {
        'name': 'Брусника',
        'description': 'Мелкая красная ягода с характерной горчинкой.',
        'image': 'images/lingonberry.jpg'
    },
    {
        'name': 'Облепиха',
        'description': 'Оранжевые ягоды, густо облепляющие ветки.',
        'image': 'images/sea_buckthorn.jpg'
    },
    {
        'name': 'Шелковица',
        'description': 'Сладкие ягоды белого, красного или чёрного цвета.',
        'image': 'images/mulberry.jpg'
    },
    {
        'name': 'Жимолость',
        'description': 'Синие продолговатые ягоды, созревающие ранней весной.',
        'image': 'images/honeysuckle.jpg'
    },
    {
        'name': 'Ирга',
        'description': 'Сине-чёрные сладкие ягоды, богатые антиоксидантами.',
        'image': 'images/serviceberry.jpg'
    },
    {
        'name': 'Арония',
        'description': 'Чёрноплодная рябина с терпким вкусом.',
        'image': 'images/chokeberry.jpg'
    },
    {
        'name': 'Боярышник',
        'description': 'Мелкие красные ягоды с мучнистой мякотью.',
        'image': 'images/hawthorn.jpg'
    },
    {
        'name': 'Калина',
        'description': 'Ярко-красные ягоды с горьковатым вкусом.',
        'image': 'images/viburnum.jpg'
    },
    {
        'name': 'Рябина',
        'description': 'Оранжево-красные ягоды, собранные в крупные гроздья.',
        'image': 'images/rowan.jpg'
    },
    {
        'name': 'Морошка',
        'description': 'Желто-оранжевая ягода, растущая в северных регионах.',
        'image': 'images/cloudberry.jpg'
    },
    {
        'name': 'Черёмуха',
        'description': 'Мелкие чёрные ягоды с вяжущим вкусом.',
        'image': 'images/bird_cherry.jpg'
    },
    {
        'name': 'Кизил',
        'description': 'Красные продолговатые ягоды с кисло-сладким вкусом.',
        'image': 'images/dogwood.jpg'
    }
]

@app.route('/lab2/berries')
def show_berries():
    return render_template('berries.html', berries=berries)

from flask import Blueprint, render_template, request, redirect, session
lab4 = Blueprint('lab4', __name__)

@lab4.route('/lab4/')
def lab():
    return render_template('lab4/lab4.html')


@lab4.route('/lab4/div-form')
def div_form():
    return render_template('lab4/div-form.html')


@lab4.route('/lab4/div', methods = ['POST'])
def div():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '' or x2 == '':
        return render_template('lab4/div.html', error='Оба поля должны быль заполнены!')
    x1 = int(x1)
    x2 = int(x2)
    if x2 == 0:
        return render_template('lab4/div.html', error='Нельзя делитьна 0!')
    else:
        result = x1 / x2
        return render_template('lab4/div.html', x1=x1, x2=x2, result=result)


@lab4.route('/lab4/add', methods = ['POST'])
def add():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    x1 = int(x1) if x1 != '' else 0
    x2 = int(x2) if x2 != '' else 0
    result = x1 + x2
    return render_template('lab4/add.html', x1=x1, x2=x2, result=result)


@lab4.route('/lab4/mul', methods = ['POST'])
def mul():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    x1 = int(x1) if x1 != '' else 1
    x2 = int(x2) if x2 != '' else 1
    result = x1 * x2
    return render_template('lab4/mul.html', x1=x1, x2=x2, result=result)


@lab4.route('/lab4/sub', methods = ['POST'])
def sub():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '' or x2 == '':
        return render_template('lab4/sub.html', error='Оба поля должны быль заполнены!')
    x1 = int(x1)
    x2 = int(x2)
    result = x1 - x2
    return render_template('lab4/sub.html', x1=x1, x2=x2, result=result)


@lab4.route('/lab4/expo', methods = ['POST'])
def expo():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '' or x2 == '':
        return render_template('lab4/expo.html', error='Оба поля должны быль заполнены!')
    x1 = int(x1)
    x2 = int(x2)
    if x1 == 0 and x2 == 0:
        return render_template('lab4/expo.html', error='Оба должны быль отличны от нуля!')
    else:
        result = x1 ** x2
        return render_template('lab4/expo.html', x1=x1, x2=x2, result=result)
    

tree_count = 0
MAX_TREES = 10 

@lab4.route('/lab4/tree', methods=['GET', 'POST'])
def tree():
    global tree_count
    if request.method == 'GET':
        return render_template('lab4/tree.html', tree_count=tree_count, max_trees=MAX_TREES)
    
    operation = request.form.get('operation')

    if operation == 'cut' and tree_count > 0:
        tree_count -= 1
    elif operation == 'plant' and tree_count < MAX_TREES:
        tree_count += 1

    return redirect('/lab4/tree')


users = [
    {'login': 'alex', 'password': '123', 'name': 'Александр', 'gender': 'male'},
    {'login': 'bob', 'password': '555', 'name': 'Роберт', 'gender': 'male'},
    {'login': 'alice', 'password': '789', 'name': 'Алиса', 'gender': 'female'},
    {'login': 'mike', 'password': '111', 'name': 'Михаил', 'gender': 'male'},
    {'login': 'sara', 'password': '222', 'name': 'Сара', 'gender': 'female'}
]

@lab4.route('/lab4/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'login' in session:
            authorised = True
            login = session['login']
            user_name = ''
            for user in users:
                if user['login'] == login:
                    user_name = user['name']
                    break
            return render_template('lab4/login.html', authorized=authorised, login=login, name=user_name)
        else:
            authorised = False
            login = ''
            return render_template('lab4/login.html', authorized=authorised, login=login)
    
    login_input = request.form.get('login')
    password = request.form.get('password')

    if not login_input:
        error = "Не введён логин"
        return render_template('lab4/login.html', error=error, authorized=False, login=login_input)
    if not password:
        error = "Не введён пароль"
        return render_template('lab4/login.html', error=error, authorized=False, login=login_input)
    for user in users:
        if login_input == user['login'] and password == user['password']:
            session['login'] = login_input
            return redirect('/lab4/login')
    error = "Неверные логин и/или пароль"
    return render_template('lab4/login.html', error=error, authorized=False, login=login_input)

@lab4.route('/lab4/logout', methods=['POST'])
def logout():
    session.pop('login', None)
    return redirect('/lab4/login')
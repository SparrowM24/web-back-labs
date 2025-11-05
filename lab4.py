from flask import Blueprint, render_template, request, redirect, session, url_for
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


@lab4.route('/lab4/fridge', methods=['GET', 'POST'])
def fridge():
    if request.method == 'GET':
        return render_template('lab4/fridge.html')
    
    temperature = request.form.get('temperature')
    
    if not temperature:
        return render_template('lab4/fridge.html', 
                             error="Ошибка: не задана температура")
    try:
        temp = int(temperature)
    except ValueError:
        return render_template('lab4/fridge.html', 
                             error="Ошибка: температура должна быть числом")
    if temp < -12:
        return render_template('lab4/fridge.html', 
                             error="Не удалось установить температуру — слишком низкое значение",
                             temperature=temperature)
    elif temp > -1:
        return render_template('lab4/fridge.html', 
                             error="Не удалось установить температуру — слишком высокое значение",
                             temperature=temperature)
    elif -12 <= temp <= -9:
        snowflakes = 3
        message = f"Установлена температура: {temp}°C"
    elif -8 <= temp <= -5:
        snowflakes = 2
        message = f"Установлена температура: {temp}°C"
    elif -4 <= temp <= -1:
        snowflakes = 1
        message = f"Установлена температура: {temp}°C"
    else:
        snowflakes = 0
        message = f"Установлена температура: {temp}°C"
    
    return render_template('lab4/fridge.html', 
                         message=message, 
                         snowflakes=snowflakes,
                         temperature=temperature)


@lab4.route('/lab4/grain_order', methods=['GET', 'POST'])
def grain_order():
    if request.method == 'GET':
        return render_template('lab4/grain_order.html')
    grain_type = request.form.get('grain_type')
    weight = request.form.get('weight')
    if not grain_type:
        return render_template('lab4/grain_order.html', 
                             error="Выберите тип зерна")
    if not weight:
        return render_template('lab4/grain_order.html', 
                             error="Введите вес заказа",
                             grain_type=grain_type)
    try:
        weight_float = float(weight)
    except ValueError:
        return render_template('lab4/grain_order.html', 
                             error="Вес должен быть числом",
                             grain_type=grain_type)
    if weight_float <= 0:
        return render_template('lab4/grain_order.html', 
                             error="Вес должен быть положительным числом",
                             grain_type=grain_type)
    if weight_float > 100:
        return render_template('lab4/grain_order.html', 
                             error="Извините, такого объёма сейчас нет в наличии",
                             grain_type=grain_type)
    prices = {
        'barley': 12000,  # ячмень
        'oats': 8500,     # овёс
        'wheat': 9000,    # пшеница
        'rye': 15000      # рожь
    }
    grain_names = {
        'barley': 'ячмень',
        'oats': 'овёс', 
        'wheat': 'пшеница',
        'rye': 'рожь'
    }
    price_per_ton = prices[grain_type]
    total_cost = weight_float * price_per_ton
    discount = 0
    if weight_float > 10:
        discount = total_cost * 0.10
        total_cost -= discount
    grain_name = grain_names[grain_type]
    return render_template('lab4/grain_order.html', 
                         success=True,
                         grain_name=grain_name,
                         weight=weight_float,
                         total_cost=total_cost,
                         discount=discount,
                         grain_type=grain_type)


@lab4.route('/lab4/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab4/register.html')
    
    login = request.form.get('login')
    password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')
    name = request.form.get('name')
    gender = request.form.get('gender')

    if not login:
        return render_template('lab4/register.html', error="Не введён логин", login=login, name=name, gender=gender)
    
    if not name:
        return render_template('lab4/register.html', error="Не введено имя", login=login, name=name, gender=gender)
    
    if not password:
        return render_template('lab4/register.html', error="Не введён пароль", login=login, name=name, gender=gender)
    
    if password != password_confirm:
        return render_template('lab4/register.html', error="Пароли не совпадают", login=login, name=name, gender=gender)

    for user in users:
        if user['login'] == login:
            return render_template('lab4/register.html', error="Пользователь с таким логином уже существует", login=login, name=name, gender=gender)
    
    new_user = {
        'login': login,
        'password': password,
        'name': name,
        'gender': gender
    }
    users.append(new_user)
    session['login'] = login
    return redirect('/lab4/login')

@lab4.route('/lab4/users')
def users_list():
    if 'login' not in session:
        return redirect('/lab4/login')
    
    return render_template('lab4/users.html', users=users, current_user=session['login'])

@lab4.route('/lab4/delete_user', methods=['POST'])
def delete_user():
    if 'login' not in session:
        return redirect('/lab4/login')
    login_to_delete = session['login']
    global users
    users = [user for user in users if user['login'] != login_to_delete]
    session.pop('login', None)
    return redirect('/lab4/login')


@lab4.route('/lab4/edit_user', methods=['GET', 'POST'])
def edit_user():
    if 'login' not in session:
        return redirect('/lab4/login')
    current_login = session['login']
    current_user = None
    for user in users:
        if user['login'] == current_login:
            current_user = user
            break
    if request.method == 'GET':
        return render_template('lab4/edit_user.html', user=current_user)
    new_login = request.form.get('login')
    new_name = request.form.get('name')
    new_gender = request.form.get('gender')
    new_password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')
    
    if not new_login:
        return render_template('lab4/edit_user.html', user=current_user, error="Не введён логин")
    
    if not new_name:
        return render_template('lab4/edit_user.html', user=current_user, error="Не введено имя")

    if new_login != current_login:
        for user in users:
            if user['login'] == new_login:
                return render_template('lab4/edit_user.html', user=current_user, error="Пользователь с таким логином уже существует")
    
    if new_password:
        if new_password != password_confirm:
            return render_template('lab4/edit_user.html', user=current_user, error="Пароли не совпадают")
    else:
        new_password = current_user['password']
    
    current_user['login'] = new_login
    current_user['name'] = new_name
    current_user['gender'] = new_gender
    current_user['password'] = new_password
    session['login'] = new_login
    return redirect('/lab4/users')
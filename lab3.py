from flask import Blueprint, render_template, request, make_response, redirect
lab3 = Blueprint('lab3', __name__)


@lab3.route('/lab3/')
def lab():
    name = request.cookies.get('name')
    name_color = request.cookies.get('name_color')
    return render_template('lab3/lab3.html', name=name, name_color=name_color)


@lab3.route('/lab3/cookie')
def cookie():
    resp = make_response(redirect('/lab3/'))
    resp.set_cookie('name', 'Alex', max_age=5)
    resp.set_cookie('age', '20')
    resp.set_cookie('name_color', 'magenta')
    return resp

@lab3.route('/lab3/del_cookie')
def del_cookie():
    resp = make_response(redirect('/lab3/'))
    resp.delete_cookie('name')
    resp.delete_cookie('age')
    resp.delete_cookie('name_color')
    return resp

@lab3.route('/lab3/form1')
def form1():
    errors = {}
    user = request.args.get('user', '')
    age = request.args.get('age', '')
    
    if request.args:
        if not user:  
            errors['user'] = 'Заполните поле!'
        
        if not age:
            errors['age'] = 'Заполните поле!'
    sex = request.args.get('sex')
    return render_template('lab3/form1.html', user=user, age=age, sex=sex, errors=errors)

@lab3.route('/lab3/order')
def order():
    return render_template('lab3/order.html')

@lab3.route('/lab3/pay')
def pay():
    price = 0
    drink = request.args.get('drink')
    
    # Сохраняем выбранные опции для отображения
    drink = drink
    milk = request.args.get('milk') == 'on'
    sugar = request.args.get('sugar') == 'on'
    
    # Пусть кофе стоит 120 рублей, чёрный чай - 80 рублей, зелёный - 70 рублей.
    if drink == 'coffee':  
        price = 120
    elif drink == 'black-tea':
        price = 80
    else:
        price = 70 
    
    # Добавка молока удорожает напиток на 30 рублей, а сахара - на 10.
    if milk:
        price += 30
    if sugar:
        price += 10
    
    return render_template('lab3/pay.html', price=price, drink=drink, 
                         milk=milk, sugar=sugar)

@lab3.route('/lab3/success')
def success():
    price = request.args.get('price', 0)
    return render_template('lab3/success.html', price=price)
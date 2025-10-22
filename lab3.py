from flask import Blueprint, render_template, request, make_response, redirect
lab3 = Blueprint('lab3', __name__)


@lab3.route('/lab3/')
def lab3_index():
    # Получаем данные из формы form1 через куки
    name = request.cookies.get('user_name', 'Аноним')
    age = request.cookies.get('user_age', 'неизвестно')
    sex = request.cookies.get('user_sex', 'не указан')
    
    return render_template('lab3/lab3.html', 
                         name=name, 
                         age=age, 
                         sex=sex)


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
    sex = request.args.get('sex', '')
    
    if request.args:
        if not user:  
            errors['user'] = 'Заполните поле!'
        
        if not age:
            errors['age'] = 'Заполните поле!'
        
        if user and age:
            resp = make_response(render_template('lab3/form1.html', user=user, age=age, sex=sex, errors=errors))
            resp.set_cookie('user_name', user)
            resp.set_cookie('user_age', age)
            resp.set_cookie('user_sex', sex)
            return resp
    
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


@lab3.route('/lab3/settings')
def settings():
    color = request.args.get('color')
    bg_color = request.args.get('bg_color')
    font_size = request.args.get('font_size')
    font_family = request.args.get('font_family')
    
    if color or bg_color or font_size or font_family:
        resp = make_response(redirect('/lab3/settings'))
        if color:
            resp.set_cookie('color', color)
        if bg_color:
            resp.set_cookie('bg_color', bg_color)
        if font_size:
            resp.set_cookie('font_size', font_size)
        if font_family:
            resp.set_cookie('font_family', font_family)
        return resp
    
    color = request.cookies.get('color')
    bg_color = request.cookies.get('bg_color')
    font_size = request.cookies.get('font_size')
    font_family = request.cookies.get('font_family')
    
    return render_template('lab3/settings.html', 
                         color=color, 
                         bg_color=bg_color, 
                         font_size=font_size, 
                         font_family=font_family)

@lab3.route('/lab3/reset-settings')
def reset_settings():
    resp = make_response(redirect('/lab3/settings'))
    resp.set_cookie('color', '', expires=0)
    resp.set_cookie('bg_color', '', expires=0)
    resp.set_cookie('font_size', '', expires=0)
    resp.set_cookie('font_family', '', expires=0)
    return resp


@lab3.route('/lab3/ticket')
def ticket():
    errors = {}
    ticket_data = {}
    if request.args:
        fio = request.args.get('fio')
        shelf = request.args.get('shelf')
        linen = request.args.get('linen')
        baggage = request.args.get('baggage')
        age = request.args.get('age')
        departure = request.args.get('departure')
        destination = request.args.get('destination')
        date = request.args.get('date')
        insurance = request.args.get('insurance')
        if not fio:
            errors['fio'] = 'Заполните ФИО пассажира'
        if not shelf:
            errors['shelf'] = 'Выберите полку'
        if not linen:
            errors['linen'] = 'Укажите наличие белья'
        if not baggage:
            errors['baggage'] = 'Укажите наличие багажа'
        if not age:
            errors['age'] = 'Заполните возраст'
        elif not age.isdigit() or not (1 <= int(age) <= 120):
            errors['age'] = 'Возраст должен быть от 1 до 120 лет'
        if not departure:
            errors['departure'] = 'Заполните пункт выезда'
        if not destination:
            errors['destination'] = 'Заполните пункт назначения'
        if not date:
            errors['date'] = 'Выберите дату поездки'
        if not insurance:
            errors['insurance'] = 'Укажите наличие страховки'
        if not errors:
            ticket_data = {
                'fio': fio,
                'shelf': shelf,
                'linen': linen == 'yes',
                'baggage': baggage == 'yes',
                'age': int(age),
                'departure': departure,
                'destination': destination,
                'date': date,
                'insurance': insurance == 'yes'
            }
            return render_template('lab3/ticket_result.html', **ticket_data)

    return render_template('lab3/ticket_form.html', errors=errors)



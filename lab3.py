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

@lab3.route('/lab3/clear_settings')
def clear_settings():
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


# Доп задание
# Список товаров
products = [
    {'name': 'iPhone 15', 'price': 89990, 'brand': 'Apple', 'color': 'черный'},
    {'name': 'Samsung Galaxy S24', 'price': 79990, 'brand': 'Samsung', 'color': 'белый'},
    {'name': 'Xiaomi Redmi Note 13', 'price': 24990, 'brand': 'Xiaomi', 'color': 'синий'},
    {'name': 'Google Pixel 8', 'price': 69990, 'brand': 'Google', 'color': 'серый'},
    {'name': 'OnePlus 11', 'price': 54990, 'brand': 'OnePlus', 'color': 'зеленый'},
    {'name': 'Realme GT 3', 'price': 42990, 'brand': 'Realme', 'color': 'желтый'},
    {'name': 'HONOR Magic5', 'price': 59990, 'brand': 'HONOR', 'color': 'фиолетовый'},
    {'name': 'OPPO Find X6', 'price': 74990, 'brand': 'OPPO', 'color': 'черный'},
    {'name': 'Vivo X100', 'price': 67990, 'brand': 'Vivo', 'color': 'синий'},
    {'name': 'Nokia G42', 'price': 18990, 'brand': 'Nokia', 'color': 'серый'},
    {'name': 'Motorola Edge 40', 'price': 39990, 'brand': 'Motorola', 'color': 'зеленый'},
    {'name': 'Sony Xperia 5', 'price': 89990, 'brand': 'Sony', 'color': 'черный'},
    {'name': 'ASUS Zenfone 10', 'price': 59990, 'brand': 'ASUS', 'color': 'белый'},
    {'name': 'Nothing Phone 2', 'price': 45990, 'brand': 'Nothing', 'color': 'белый'},
    {'name': 'Huawei P60', 'price': 79990, 'brand': 'Huawei', 'color': 'золотой'},
    {'name': 'ZTE Nubia Z50', 'price': 34990, 'brand': 'ZTE', 'color': 'красный'},
    {'name': 'Tecno Phantom V', 'price': 29990, 'brand': 'Tecno', 'color': 'синий'},
    {'name': 'Infinix Zero 30', 'price': 22990, 'brand': 'Infinix', 'color': 'оранжевый'},
    {'name': 'Poco X6 Pro', 'price': 32990, 'brand': 'Poco', 'color': 'желтый'},
    {'name': 'iPhone 14', 'price': 69990, 'brand': 'Apple', 'color': 'красный'}
]

@lab3.route('/lab3/products')
def products_search():
    min_price_cookie = request.cookies.get('min_price')
    max_price_cookie = request.cookies.get('max_price')
    
    min_price = request.args.get('min_price', min_price_cookie)
    max_price = request.args.get('max_price', max_price_cookie)

    if 'reset' in request.args:
        min_price = None
        max_price = None
    min_price = int(min_price) if min_price and min_price.isdigit() else None
    max_price = int(max_price) if max_price and max_price.isdigit() else None
    if min_price and max_price and min_price > max_price:
        min_price, max_price = max_price, min_price
    filtered_products = products
    if min_price is not None or max_price is not None:
        filtered_products = []
        for product in products:
            price = product['price']
            if (min_price is None or price >= min_price) and (max_price is None or price <= max_price):
                filtered_products.append(product)
    resp = make_response(render_template(
        'lab3/products.html',
        products=filtered_products,
        min_price=min_price,
        max_price=max_price,
        total_found=len(filtered_products),
        min_possible_price=min(p['price'] for p in products),
        max_possible_price=max(p['price'] for p in products)
    ))
    if min_price is not None:
        resp.set_cookie('min_price', str(min_price))
    if max_price is not None:
        resp.set_cookie('max_price', str(max_price))
    if 'reset' in request.args:
        resp.set_cookie('min_price', '', expires=0)
        resp.set_cookie('max_price', '', expires=0)
    
    return resp
from flask import Blueprint, render_template, jsonify, session, request, redirect
import random
import os
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from os import path

lab9 = Blueprint('lab9', __name__)

# Подключение к базе данных (используем ту же, что в lab5)
def db_connect():
    dir_path = path.dirname(path.realpath(__file__))
    db_path = path.join(dir_path, "lab5_database.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Проверка авторизации
def is_authenticated():
    return 'login' in session

# Список поздравлений
congratulations = [
    "С Новым годом! Пусть сбудутся все мечты!",
    "Желаю здоровья, счастья и удачи в новом году!",
    "Пусть новый год принесет много радости и улыбок!",
    "Счастья, любви и процветания в новом году!",
    "Пусть каждый день нового года будет наполнен волшебством!",
    "Желаю успехов во всех начинаниях!",
    "Пусть ангел-хранитель всегда будет рядом!",
    "Мира, добра и взаимопонимания в семье!",
    "Финансового благополучия и стабильности!",
    "Крепкого здоровья и бодрости духа!"
]

# Список путей к изображениям подарков
gift_images = [
    "/static/lab9/gift1.png",
    "/static/lab9/gift2.png",
    "/static/lab9/gift3.png",
    "/static/lab9/gift4.png",
    "/static/lab9/gift5.png",
    "/static/lab9/gift6.png",
    "/static/lab9/gift7.png",
    "/static/lab9/gift8.png",
    "/static/lab9/gift9.png",
    "/static/lab9/gift10.png"
]

# Определяем, какие подарки доступны только авторизованным
# Пусть подарки 6-10 доступны только авторизованным (индексы 5-9)
PREMIUM_GIFT_START = 5  # Начиная с gift6.png

# Генерируем случайные позиции для коробок
def generate_box_positions():
    positions = []
    for i in range(10):
        positions.append({
            'id': i,
            'top': random.randint(10, 70),
            'left': random.randint(5, 85),
            'congrat': congratulations[i],
            'gift_image': gift_images[i],
            'is_premium': i >= PREMIUM_GIFT_START  # Подарки 6-10 премиальные
        })
    return positions

# Инициализируем позиции (они будут одинаковыми для всех пользователей)
box_positions = generate_box_positions()

@lab9.route('/lab9/')
def lab9_index():
    # Инициализируем сессию
    if 'opened_count' not in session:
        session['opened_count'] = 0
        session['user_opened_boxes'] = []
    
    user_login = session.get('login', "Anonymous")
    is_auth = is_authenticated()
    
    return render_template('lab9/index.html', 
                         login=user_login, 
                         is_authenticated=is_auth)

@lab9.route('/lab9/get_boxes')
def get_boxes():
    user_opened = session.get('user_opened_boxes', [])
    is_auth = is_authenticated()
    boxes_info = []
    
    for box in box_positions:
        # Проверяем доступность коробки
        is_available = True
        is_locked = False
        message = ""
        
        # Если коробка премиальная и пользователь не авторизован
        if box['is_premium'] and not is_auth:
            is_available = False
            is_locked = True
            message = "Требуется авторизация"
        
        boxes_info.append({
            'id': box['id'],
            'top': box['top'],
            'left': box['left'],
            'congrat': box['congrat'],
            'gift_image': box['gift_image'],
            'opened': box['id'] in user_opened,
            'is_premium': box['is_premium'],
            'is_available': is_available,
            'is_locked': is_locked,
            'message': message
        })
    
    return jsonify({
        'boxes': boxes_info,
        'opened_count': session.get('opened_count', 0),
        'total_boxes': 10,
        'remaining': 10 - len(user_opened),
        'is_authenticated': is_auth,
        'premium_count': len([b for b in box_positions if b['is_premium']])
    })

@lab9.route('/lab9/open_box/<int:box_id>', methods=['POST'])
def open_box(box_id):
    # Проверяем, что коробка существует
    if box_id < 0 or box_id >= 10:
        return jsonify({'error': 'Некорректный номер коробки'}), 400
    
    # Проверяем доступность премиальных коробок
    if box_positions[box_id]['is_premium'] and not is_authenticated():
        return jsonify({
            'error': 'Эта коробка доступна только авторизованным пользователям',
            'requires_auth': True
        }), 403
    
    # Проверяем, не открыта ли уже эта коробка
    user_opened = session.get('user_opened_boxes', [])
    if box_id in user_opened:
        return jsonify({'error': 'Эта коробка уже открыта'}), 400
    
    # Проверяем лимит в 3 коробки
    if session.get('opened_count', 0) >= 3:
        return jsonify({'error': 'Вы уже открыли максимальное количество коробок (3)'}), 400
    
    # Добавляем коробку в открытые
    user_opened.append(box_id)
    session['user_opened_boxes'] = user_opened
    session['opened_count'] = len(user_opened)
    
    return jsonify({
        'success': True,
        'opened_count': session['opened_count'],
        'remaining': 10 - len(user_opened)
    })

@lab9.route('/lab9/reset', methods=['POST'])
def reset_boxes():
    # Сбрасываем сессию пользователя
    session['opened_count'] = 0
    session['user_opened_boxes'] = []
    return jsonify({'success': True})

@lab9.route('/lab9/refill', methods=['POST'])
def refill_boxes():
    # Только для авторизованных пользователей
    if not is_authenticated():
        return jsonify({'error': 'Требуется авторизация'}), 403
    
    # Перегенерируем позиции коробок
    global box_positions
    box_positions = generate_box_positions()
    
    # Сбрасываем открытые коробки для всех пользователей
    # В реальном приложении нужно делать это аккуратно,
    # но для учебного проекта сойдет
    if 'opened_count' in session:
        session['opened_count'] = 0
    if 'user_opened_boxes' in session:
        session['user_opened_boxes'] = []
    
    return jsonify({'success': True, 'message': 'Коробки наполнены заново!'})

@lab9.route('/lab9/logout')
def logout():
    session.pop('login', None)
    return redirect('/lab9/')

from flask import Blueprint, render_template, jsonify, session
import random
import os

# Создаем Blueprint В САМОМ НАЧАЛЕ файла
lab9 = Blueprint('lab9', __name__)

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

# Генерируем случайные позиции для коробок
def generate_box_positions():
    positions = []
    for i in range(10):
        positions.append({
            'id': i,
            'top': random.randint(10, 70),
            'left': random.randint(5, 85),
            'congrat': congratulations[i],
            'gift_image': gift_images[i]
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
    
    return render_template('lab9/index.html')

@lab9.route('/lab9/get_boxes')
def get_boxes():
    user_opened = session.get('user_opened_boxes', [])
    boxes_info = []
    
    for box in box_positions:
        boxes_info.append({
            'id': box['id'],
            'top': box['top'],
            'left': box['left'],
            'congrat': box['congrat'],
            'gift_image': box['gift_image'],
            'opened': box['id'] in user_opened
        })
    
    return jsonify({
        'boxes': boxes_info,
        'opened_count': session.get('opened_count', 0),
        'total_boxes': 10,
        'remaining': 10 - len(user_opened)
    })

@lab9.route('/lab9/open_box/<int:box_id>', methods=['POST'])
def open_box(box_id):
    # Проверяем, что коробка существует
    if box_id < 0 or box_id >= 10:
        return jsonify({'error': 'Некорректный номер коробки'}), 400
    
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
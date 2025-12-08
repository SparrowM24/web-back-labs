from flask import Blueprint, render_template, request, session, jsonify
import sqlite3
from os import path
import numpy as np

# ИЗМЕНЯЕМ ИМЯ Blueprint
lab6_bp = Blueprint('lab6_bp', __name__)

# Используем отдельную БД для lab6 чтобы избежать конфликтов
def get_lab6_db_path():
    dir_path = path.dirname(path.realpath(__file__))
    return path.join(dir_path, "lab6_database.db")

def init_lab6_offices():
    """Инициализация офисов в отдельной БД"""
    db_path = get_lab6_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    try:
        # Создаем таблицу офисов
        cur.execute("""
            CREATE TABLE IF NOT EXISTS offices (
                number INTEGER PRIMARY KEY,
                tenant TEXT DEFAULT '',
                price INTEGER
            )
        """)
        
        # Проверяем, есть ли данные
        cur.execute("SELECT COUNT(*) as count FROM offices")
        count = cur.fetchone()[0]
        
        if count == 0:
            # Добавляем 10 офисов
            for i in range(1, 11):
                price = round(np.random.rand() * 1000)
                cur.execute(
                    "INSERT INTO offices (number, price) VALUES (?, ?)",
                    (i, price)
                )
        
        # Создаем таблицу lab6_users для хранения пользователей lab5
        cur.execute("""
            CREATE TABLE IF NOT EXISTS lab6_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT UNIQUE,
                password TEXT
            )
        """)
        
        conn.commit()
        print(f"База данных lab6 инициализирована: {db_path}")
    except Exception as e:
        print(f"Ошибка инициализации БД lab6: {e}")
        conn.rollback()
    finally:
        conn.close()

@lab6_bp.route('/lab6/')
def lab():
    # Проверяем авторизацию через сессию
    login = session.get('login')
    
    # Инициализируем базу lab6
    init_lab6_offices()
    
    # Если пользователь авторизован, добавляем/обновляем его в lab6_users
    if login:
        db_path = get_lab6_db_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        try:
            # Проверяем, есть ли пользователь
            cur.execute("SELECT id FROM lab6_users WHERE login = ?", (login,))
            user = cur.fetchone()
            
            if not user:
                # Добавляем пользователя с пустым паролем (только для совместимости)
                cur.execute(
                    "INSERT INTO lab6_users (login, password) VALUES (?, ?)",
                    (login, '')
                )
                conn.commit()
                print(f"Пользователь {login} добавлен в lab6")
        except Exception as e:
            print(f"Ошибка добавления пользователя в lab6: {e}")
        finally:
            conn.close()
    
    return render_template('lab6/lab6.html', login=login)

@lab6_bp.route('/lab6/json-rpc-api/', methods=['POST'])
def api():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32700, 'message': 'Parse error'},
                'id': None
            }), 400
        
        request_id = data.get('id')
        method = data.get('method')
        
        # Метод info доступен всем
        if method == 'info':
            db_path = get_lab6_db_path()
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            cur.execute("SELECT * FROM offices ORDER BY number")
            offices = cur.fetchall()
            
            # Конвертируем в список словарей
            offices_list = []
            for row in offices:
                offices_list.append({
                    'number': row['number'],
                    'tenant': row['tenant'],
                    'price': row['price']
                })
            
            conn.close()
            
            return jsonify({
                'jsonrpc': '2.0',
                'result': offices_list,
                'id': request_id
            })

        # Проверка авторизации для других методов
        login = session.get('login')
        if not login:
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': 1, 'message': 'Unauthorized - требуется вход в систему'},
                'id': request_id
            }), 401
        
        # Для lab6 проверяем в своей БД
        db_path = get_lab6_db_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM lab6_users WHERE login = ?", (login,))
        user = cur.fetchone()
        
        if not user:
            conn.close()
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': 1, 'message': 'Пользователь не найден в системе lab6'},
                'id': request_id
            }), 401
        
        if method == 'booking':
            params = data.get('params', {})
            office_number = params.get('office_number') if isinstance(params, dict) else params
            
            if not office_number:
                conn.close()
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': -32602, 'message': 'Invalid params'},
                    'id': request_id
                }), 400
            
            # Проверяем офис
            cur.execute("SELECT * FROM offices WHERE number = ?", (office_number,))
            office = cur.fetchone()
            
            if not office:
                conn.close()
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': 6, 'message': 'Office not found'},
                    'id': request_id
                }), 404
            
            if office['tenant']:
                conn.close()
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': 2, 'message': 'Already booked'},
                    'id': request_id
                }), 400
            
            # Бронируем офис
            cur.execute(
                "UPDATE offices SET tenant = ? WHERE number = ?",
                (login, office_number)
            )
            conn.commit()
            conn.close()
            
            return jsonify({
                'jsonrpc': '2.0',
                'result': 'success',
                'id': request_id
            })
        
        if method == 'cancellation':
            params = data.get('params', {})
            office_number = params.get('office_number') if isinstance(params, dict) else params
            
            if not office_number:
                conn.close()
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': -32602, 'message': 'Invalid params'},
                    'id': request_id
                }), 400
            
            # Проверяем офис
            cur.execute("SELECT * FROM offices WHERE number = ?", (office_number,))
            office = cur.fetchone()
            
            if not office:
                conn.close()
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': 6, 'message': 'Office not found'},
                    'id': request_id
                }), 404
            
            if not office['tenant']:
                conn.close()
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': 5, 'message': 'Not booked'},
                    'id': request_id
                }), 400
            
            if office['tenant'] != login:
                conn.close()
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': 4, 'message': 'Booked by another user'},
                    'id': request_id
                }), 403
            
            # Отменяем бронь
            cur.execute(
                "UPDATE offices SET tenant = '' WHERE number = ?",
                (office_number,)
            )
            conn.commit()
            conn.close()
            
            return jsonify({
                'jsonrpc': '2.0',
                'result': 'Booking canceled successfully',
                'id': request_id
            })
        
        conn.close()
        return jsonify({
            'jsonrpc': '2.0',
            'error': {'code': -32601, 'message': 'Method not found'},
            'id': request_id
        }), 404
        
    except Exception as e:
        print(f"Ошибка в API lab6: {e}")
        return jsonify({
            'jsonrpc': '2.0',
            'error': {'code': -32603, 'message': f'Internal error: {str(e)}'},
            'id': data.get('id') if data else None
        }), 500
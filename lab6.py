from flask import Blueprint, render_template, request, session, jsonify, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path
import numpy as np

lab6 = Blueprint('lab6', __name__)

# Инициализация офисов (если нужно создать в БД)
def init_offices():
    conn, cur = db_connect()
    try:
        # Проверяем, существует ли таблица
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("""
                CREATE TABLE IF NOT EXISTS offices (
                    number INTEGER PRIMARY KEY,
                    tenant TEXT DEFAULT '',
                    price INTEGER
                )
            """)
            
            # Проверяем, есть ли данные
            cur.execute("SELECT COUNT(*) as count FROM offices")
            count = cur.fetchone()['count']
            
            if count == 0:
                # Добавляем 10 офисов
                for i in range(1, 11):
                    price = round(np.random.rand() * 1000)
                    cur.execute(
                        "INSERT INTO offices (number, price) VALUES (%s, %s)",
                        (i, price)
                    )
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS offices (
                    number INTEGER PRIMARY KEY,
                    tenant TEXT DEFAULT '',
                    price INTEGER
                )
            """)
            
            cur.execute("SELECT COUNT(*) as count FROM offices")
            count = cur.fetchone()[0]
            
            if count == 0:
                for i in range(1, 11):
                    price = round(np.random.rand() * 1000)
                    cur.execute(
                        "INSERT INTO offices (number, price) VALUES (?, ?)",
                        (i, price)
                    )
        
        conn.commit()
    except Exception as e:
        print(f"Ошибка инициализации БД: {e}")
        conn.rollback()
    finally:
        db_close(conn, cur)

def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='alice_dyachkova_knowledge_base',
            user='alice_dyachkova_knowledge_base',
            password='123'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
    return conn, cur

def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

@lab6.route('/lab6/')
def lab():
    # Инициализируем офисы при первом заходе
    init_offices()
    return render_template('lab6/lab6.html')

@lab6.route('/lab6/json-rpc-api/', methods=['POST'])
def api():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32700, 'message': 'Parse error'},
                'id': None
            }), 400
        
        id = data.get('id')
        method = data.get('method')
        
        if method == 'info':
            conn, cur = db_connect()
            
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute("SELECT * FROM offices ORDER BY number")
                offices = cur.fetchall()
                offices_list = [dict(office) for office in offices]
            else:
                cur.execute("SELECT * FROM offices ORDER BY number")
                offices = cur.fetchall()
                # Конвертируем sqlite3.Row в dict
                offices_list = []
                for row in offices:
                    offices_list.append({
                        'number': row['number'],
                        'tenant': row['tenant'],
                        'price': row['price']
                    })
            
            db_close(conn, cur)
            
            return jsonify({
                'jsonrpc': '2.0',
                'result': offices_list,
                'id': id
            })

        # Проверка авторизации для других методов
        login = session.get('login')
        if not login:
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': 1, 'message': 'Unauthorized'},
                'id': id
            }), 401
        
        if method == 'booking':
            office_number = data.get('params')
            if not office_number:
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': -32602, 'message': 'Invalid params'},
                    'id': id
                }), 400
            
            conn, cur = db_connect()
            
            # Проверяем, существует ли офис и свободен ли он
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute("SELECT * FROM offices WHERE number = %s", (office_number,))
            else:
                cur.execute("SELECT * FROM offices WHERE number = ?", (office_number,))
            
            office = cur.fetchone()
            
            if not office:
                db_close(conn, cur)
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': 6, 'message': 'Office not found'},
                    'id': id
                }), 404
            
            # Конвертируем в dict для проверки
            if current_app.config['DB_TYPE'] == 'postgres':
                office_dict = dict(office)
            else:
                office_dict = {
                    'number': office['number'],
                    'tenant': office['tenant'],
                    'price': office['price']
                }
            
            if office_dict['tenant']:
                db_close(conn, cur)
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': 2, 'message': 'Already booked'},
                    'id': id
                }), 400
            
            # Бронируем офис
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute(
                    "UPDATE offices SET tenant = %s WHERE number = %s",
                    (login, office_number)
                )
            else:
                cur.execute(
                    "UPDATE offices SET tenant = ? WHERE number = ?",
                    (login, office_number)
                )
            
            db_close(conn, cur)
            
            return jsonify({
                'jsonrpc': '2.0',
                'result': 'success',
                'id': id
            })
        
        if method == 'cancellation':
            office_number = data.get('params')
            if not office_number:
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': -32602, 'message': 'Invalid params'},
                    'id': id
                }), 400
            
            conn, cur = db_connect()
            
            # Проверяем офис
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute("SELECT * FROM offices WHERE number = %s", (office_number,))
            else:
                cur.execute("SELECT * FROM offices WHERE number = ?", (office_number,))
            
            office = cur.fetchone()
            
            if not office:
                db_close(conn, cur)
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': 6, 'message': 'Office not found'},
                    'id': id
                }), 404
            
            # Конвертируем в dict
            if current_app.config['DB_TYPE'] == 'postgres':
                office_dict = dict(office)
            else:
                office_dict = {
                    'number': office['number'],
                    'tenant': office['tenant'],
                    'price': office['price']
                }
            
            if not office_dict['tenant']:
                db_close(conn, cur)
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': 5, 'message': 'Not booked'},
                    'id': id
                }), 400
            
            if office_dict['tenant'] != login:
                db_close(conn, cur)
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': 4, 'message': 'Booked by another user'},
                    'id': id
                }), 403
            
            # Отменяем бронь
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute(
                    "UPDATE offices SET tenant = '' WHERE number = %s",
                    (office_number,)
                )
            else:
                cur.execute(
                    "UPDATE offices SET tenant = '' WHERE number = ?",
                    (office_number,)
                )
            
            db_close(conn, cur)
            
            return jsonify({
                'jsonrpc': '2.0',
                'result': 'Booking canceled successfully',
                'id': id
            })
        
        return jsonify({
            'jsonrpc': '2.0',
            'error': {'code': -32601, 'message': 'Method not found'},
            'id': id
        }), 404
        
    except Exception as e:
        print(f"Ошибка в API: {e}")
        return jsonify({
            'jsonrpc': '2.0',
            'error': {'code': -32603, 'message': 'Internal error'},
            'id': data.get('id') if data else None
        }), 500
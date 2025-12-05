from flask import Blueprint, render_template, request, session, jsonify, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path
import numpy as np
import logging

lab6 = Blueprint('lab6', __name__)

# Включаем логирование
logging.basicConfig(level=logging.DEBUG)

# Инициализация офисов 
def init_offices():
    conn, cur = None, None
    try:
        conn, cur = db_connect()
        logging.info(f"DB_TYPE: {current_app.config.get('DB_TYPE')}")
        
        # Создаем таблицу если не существует
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("""
                CREATE TABLE IF NOT EXISTS offices (
                    number INTEGER PRIMARY KEY,
                    tenant TEXT DEFAULT '',
                    price INTEGER DEFAULT 1000
                )
            """)
            
            cur.execute("SELECT COUNT(*) as count FROM offices")
            count = cur.fetchone()['count']
            logging.info(f"Количество офисов в БД: {count}")
            
            if count == 0:
                for i in range(1, 11):
                    price = round(np.random.rand() * 1000)
                    cur.execute(
                        "INSERT INTO offices (number, price) VALUES (%s, %s)",
                        (i, price)
                    )
                logging.info("Добавлено 10 офисов в БД")
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS offices (
                    number INTEGER PRIMARY KEY,
                    tenant TEXT DEFAULT '',
                    price INTEGER DEFAULT 1000
                )
            """)
            
            cur.execute("SELECT COUNT(*) as count FROM offices")
            count = cur.fetchone()[0]
            logging.info(f"Количество офисов в SQLite: {count}")
            
            if count == 0:
                for i in range(1, 11):
                    price = round(np.random.rand() * 1000)
                    cur.execute(
                        "INSERT INTO offices (number, price) VALUES (?, ?)",
                        (i, price)
                    )
                logging.info("Добавлено 10 офисов в SQLite")
        
        conn.commit()
        
    except Exception as e:
        logging.error(f"Ошибка инициализации БД: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if conn and cur:
            db_close(conn, cur)

def db_connect():
    try:
        db_type = current_app.config.get('DB_TYPE', 'postgres')
        logging.info(f"Подключаемся к БД типа: {db_type}")
        
        if db_type == 'postgres':
            # Для pythonanywhere используем другую конфигурацию
            conn = psycopg2.connect(
                host='localhost',  # или '127.0.0.1'
                database='alice_dyachkova_knowledge_base',
                user='alice_dyachkova_knowledge_base',
                password='123',
                connect_timeout=10
            )
            cur = conn.cursor(cursor_factory=RealDictCursor)
            logging.info("Успешное подключение к PostgreSQL")
        else:
            dir_path = path.dirname(path.realpath(__file__))
            db_path = path.join(dir_path, "database.db")
            logging.info(f"Подключаемся к SQLite: {db_path}")
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            logging.info("Успешное подключение к SQLite")
        
        return conn, cur
    except Exception as e:
        logging.error(f"Ошибка подключения к БД: {e}")
        raise

def db_close(conn, cur):
    try:
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logging.error(f"Ошибка при закрытии соединения: {e}")

@lab6.route('/lab6/')
def lab():
    try:
        # Инициализируем офисы при первом заходе
        init_offices()
        return render_template('lab6/lab6.html')
    except Exception as e:
        logging.error(f"Ошибка в роуте /lab6/: {e}", exc_info=True)
        return f"Ошибка при загрузке страницы: {str(e)}", 500

@lab6.route('/lab6/json-rpc-api/', methods=['POST'])
def api():
    try:
        data = request.get_json()
        logging.debug(f"Получен запрос: {data}")
        
        if not data:
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32700, 'message': 'Parse error'},
                'id': None
            }), 400
        
        id_value = data.get('id')
        method = data.get('method')
        
        if method == 'info':
            try:
                conn, cur = db_connect()
                
                if current_app.config.get('DB_TYPE') == 'postgres':
                    cur.execute("SELECT * FROM offices ORDER BY number")
                    offices = cur.fetchall()
                    offices_list = [dict(office) for office in offices]
                else:
                    cur.execute("SELECT * FROM offices ORDER BY number")
                    offices = cur.fetchall()
                    offices_list = []
                    for row in offices:
                        offices_list.append({
                            'number': row['number'],
                            'tenant': row['tenant'],
                            'price': row['price']
                        })
                
                db_close(conn, cur)
                logging.debug(f"Возвращаем {len(offices_list)} офисов")
                
                return jsonify({
                    'jsonrpc': '2.0',
                    'result': offices_list,
                    'id': id_value
                })
                
            except Exception as e:
                logging.error(f"Ошибка при получении информации об офисах: {e}")
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': -32603, 'message': f'Database error: {str(e)}'},
                    'id': id_value
                }), 500

        # Проверка авторизации для других методов
        login = session.get('login')
        if not login:
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': 1, 'message': 'Unauthorized'},
                'id': id_value
            }), 401
        
        if method == 'booking':
            office_number = data.get('params')
            if not office_number:
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': -32602, 'message': 'Invalid params'},
                    'id': id_value
                }), 400
            
            try:
                conn, cur = db_connect()
                
                # Проверяем, существует ли офис и свободен ли он
                if current_app.config.get('DB_TYPE') == 'postgres':
                    cur.execute("SELECT * FROM offices WHERE number = %s", (office_number,))
                else:
                    cur.execute("SELECT * FROM offices WHERE number = ?", (office_number,))
                
                office = cur.fetchone()
                
                if not office:
                    db_close(conn, cur)
                    return jsonify({
                        'jsonrpc': '2.0',
                        'error': {'code': 6, 'message': 'Office not found'},
                        'id': id_value
                    }), 404
                
                # Конвертируем в dict для проверки
                if current_app.config.get('DB_TYPE') == 'postgres':
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
                        'id': id_value
                    }), 400
                
                # Бронируем офис
                if current_app.config.get('DB_TYPE') == 'postgres':
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
                logging.info(f"Пользователь {login} забронировал офис {office_number}")
                
                return jsonify({
                    'jsonrpc': '2.0',
                    'result': 'success',
                    'id': id_value
                })
                
            except Exception as e:
                logging.error(f"Ошибка при бронировании: {e}")
                db_close(conn, cur)
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': -32603, 'message': f'Database error: {str(e)}'},
                    'id': id_value
                }), 500
        
        if method == 'cancellation':
            office_number = data.get('params')
            if not office_number:
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': -32602, 'message': 'Invalid params'},
                    'id': id_value
                }), 400
            
            try:
                conn, cur = db_connect()
                
                # Проверяем офис
                if current_app.config.get('DB_TYPE') == 'postgres':
                    cur.execute("SELECT * FROM offices WHERE number = %s", (office_number,))
                else:
                    cur.execute("SELECT * FROM offices WHERE number = ?", (office_number,))
                
                office = cur.fetchone()
                
                if not office:
                    db_close(conn, cur)
                    return jsonify({
                        'jsonrpc': '2.0',
                        'error': {'code': 6, 'message': 'Office not found'},
                        'id': id_value
                    }), 404
                
                # Конвертируем в dict
                if current_app.config.get('DB_TYPE') == 'postgres':
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
                        'id': id_value
                    }), 400
                
                if office_dict['tenant'] != login:
                    db_close(conn, cur)
                    return jsonify({
                        'jsonrpc': '2.0',
                        'error': {'code': 4, 'message': 'Booked by another user'},
                        'id': id_value
                    }), 403
                
                # Отменяем бронь
                if current_app.config.get('DB_TYPE') == 'postgres':
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
                logging.info(f"Пользователь {login} отменил бронь офиса {office_number}")
                
                return jsonify({
                    'jsonrpc': '2.0',
                    'result': 'Booking canceled successfully',
                    'id': id_value
                })
                
            except Exception as e:
                logging.error(f"Ошибка при отмене брони: {e}")
                db_close(conn, cur)
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': -32603, 'message': f'Database error: {str(e)}'},
                    'id': id_value
                }), 500
        
        return jsonify({
            'jsonrpc': '2.0',
            'error': {'code': -32601, 'message': f'Method not found: {method}'},
            'id': id_value
        }), 404
        
    except Exception as e:
        logging.error(f"Ошибка в API: {e}", exc_info=True)
        return jsonify({
            'jsonrpc': '2.0',
            'error': {'code': -32603, 'message': f'Internal error: {str(e)}'},
            'id': data.get('id') if data else None
        }), 500
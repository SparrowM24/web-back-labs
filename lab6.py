from flask import Blueprint, render_template, request, session, redirect, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from os import path
import numpy as np


lab6 = Blueprint('lab6', __name__)

offices = []
for i in range (1, 11):
    offices.append({'number': i, 'tenant': '', "price": round(np.random.rand() * 1000)})

@lab6.route('/lab6/')
def lab():
    return render_template('lab6/lab6.html')

def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        conn = psycopg2.connect(
            host = '127.0.0.1',
            database = 'alice_dyachkova_knowledge_base',
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

@lab6.route('/lab6/json-rpc-api/', methods=['POST'])
def api():
    data=request.json
    id = data['id']
    if data['method'] == 'info':
        conn, cur = db_connect()
        cur.execute("SELECT * FROM offices ORDER BY number")
        offices = cur.fetchall()

        offices_list = [dict(office) for office in offices]

        db_close(conn, cur)

        return {
            'jsonrpc': '2.0',
            'result': offices_list,
            'id': id
        }

    login = session.get('login')
    if not login:
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': 1,
                'message': 'Unauthorized'
            },
            'id': id
        }
    
    if data['method'] == 'booking':
        office_number = data['params']

        conn, cur = db_connect()
        cur.execute("SELECT * FROM offices ORDER BY number")
        offices = cur.fetchall()

        offices_list = [dict(office) for office in offices]

        db_close(conn, cur)

        for office in offices_list:
            if office['number'] == office_number:
                if office['tenant'] != '':
                    return {
                        'jsonrpc': '2.0',
                        'error': {
                            'code': 2,
                            'message': 'Already booked'
                        },
                        'id': id
                    }
                    
                conn, cur = db_connect()
                if current_app.config['DB_TYPE'] == 'postgres':
                    cur.execute("UPDATE offices SET tenant = %s WHERE number = %s", (login, office_number))
                else:
                    cur.execute("UPDATE offices SET tenant = ? WHERE number = ?", (login, office_number))
                conn.commit()
                db_close(conn, cur)

                return {
                    'jsonrpc': '2.0',
                    'result': 'success',
                    'id': id
                }

    if data['method'] == 'cancellation':
        office_number = data['params']

        conn, cur = db_connect()
        cur.execute("SELECT * FROM offices ORDER BY number")
        offices = cur.fetchall()

        db_close(conn, cur)

        offices_list = [dict(office) for office in offices]

        for office in offices_list:
            if office['number'] == office_number:
                if office['tenant'] == login:

                    conn, cur = db_connect()
                    if current_app.config['DB_TYPE'] == 'postgres':
                        cur.execute("UPDATE offices SET tenant = '' WHERE number = %s", (office_number, ))
                    else:
                        cur.execute("UPDATE offices SET tenant = '' WHERE number = ?", (office_number, ))
                    conn.commit()
                    db_close(conn, cur)

                    return {
                        'jsonrpc': '2.0',
                        'result': 'Booking canceled successfully',
                        'id': id
                    }
                elif office['tenant'] != '':
                    return {
                        'jsonrpc': '2.0',
                        'error': {
                            'code': 4,
                            'message': 'Booked by another user'
                        },
                        'id': id
                    }
                else:
                    return {
                        'jsonrpc': '2.0',
                        'error': {
                            'code': 5,
                            'message': 'Not booked'
                        },
                        'id': id
                    }

    return {
            'jsonrpc': '2.0',
            'error': {
                'code': -32601,
                'message': 'Method not found'
            },
            'id': id
        }
from flask import Blueprint, render_template, request, abort, jsonify, current_app
from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor
import sqlite3
from os import path

lab7 = Blueprint('lab7', __name__)

# ========== УНИВЕРСАЛЬНОЕ ПОДКЛЮЧЕНИЕ К БАЗЕ ==========

def db_connect():
    """Универсальное подключение к базе данных"""
    if current_app.config.get('DB_TYPE', 'postgres') == 'postgres':
        # PostgreSQL (для локальной разработки с KOMPAS-3D)
        try:
            conn = psycopg2.connect(
                host='127.0.0.1',
                port=5433,
                database='alice_dyachkova_knowledge_base2',
                user='alice_dyachkova_knowledge_base',
                password='123456',
                cursor_factory=DictCursor
            )
            cur = conn.cursor()
            return conn, cur
        except Exception as e:
            print(f"Ошибка подключения к PostgreSQL: {e}")
            # Fallback на SQLite если PostgreSQL не доступен
            print("Используем SQLite как fallback...")
            current_app.config['DB_TYPE'] = 'sqlite'
    
    # SQLite (для PythonAnywhere или как fallback)
    dir_path = path.dirname(path.realpath(__file__))
    db_path = path.join(dir_path, "films.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    return conn, cur

def db_close(conn, cur):
    """Закрытие соединения с БД"""
    conn.commit()
    cur.close()
    conn.close()

# ========== ИНИЦИАЛИЗАЦИЯ БАЗЫ ==========

def init_database():
    """Создание таблицы если её нет"""
    conn, cur = db_connect()
    
    try:
        if current_app.config.get('DB_TYPE', 'postgres') == 'postgres':
            cur.execute("""
                CREATE TABLE IF NOT EXISTS films (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255),
                    title_ru VARCHAR(255) NOT NULL,
                    year INTEGER NOT NULL,
                    description TEXT NOT NULL
                )
            """)
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS films (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    title_ru TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    description TEXT NOT NULL
                )
            """)
        
        # Проверяем есть ли данные
        cur.execute("SELECT COUNT(*) FROM films")
        count = cur.fetchone()[0]
        
        if count == 0:
            if current_app.config.get('DB_TYPE', 'postgres') == 'postgres':
                cur.execute("""
                    INSERT INTO films (title, title_ru, year, description) 
                    VALUES (%s, %s, %s, %s),
                           (%s, %s, %s, %s),
                           (%s, %s, %s, %s)
                """, (
                    'The Matrix', 'Матрица', 1999, 'Хакер Нео узнает, что его мир — виртуальная реальность.',
                    'Inception', 'Начало', 2010, 'Вор идей пытается внедрить мысль в подсознание.',
                    'Interstellar', 'Интерстеллар', 2014, 'Путешествие через червоточину.'
                ))
            else:
                cur.executemany("""
                    INSERT INTO films (title, title_ru, year, description) 
                    VALUES (?, ?, ?, ?)
                """, [
                    ('The Matrix', 'Матрица', 1999, 'Хакер Нео узнает, что его мир — виртуальная реальность.'),
                    ('Inception', 'Начало', 2010, 'Вор идей пытается внедрить мысль в подсознание.'),
                    ('Interstellar', 'Интерстеллар', 2014, 'Путешествие через червоточину.')
                ])
    finally:
        db_close(conn, cur)

# ========== ВАЛИДАЦИЯ ==========

def validate_film(film):
    """Валидация данных фильма"""
    errors = {}
    
    # Русское название
    title_ru = film.get('title_ru', '').strip()
    if not title_ru:
        errors['title_ru'] = 'Русское название обязательно'
    
    # Оригинальное название
    title = film.get('title', '').strip()
    if not title_ru and not title:
        errors['title'] = 'Хотя бы одно название должно быть заполнено'
    
    # Год
    try:
        year = int(film.get('year', 0))
        current_year = datetime.now().year
        if year < 1895 or year > current_year:
            errors['year'] = f'Год должен быть от 1895 до {current_year}'
    except (ValueError, TypeError):
        errors['year'] = 'Год должен быть числом'
    
    # Описание
    description = film.get('description', '').strip()
    if not description:
        errors['description'] = 'Описание обязательно'
    elif len(description) > 2000:
        errors['description'] = 'Описание не должно превышать 2000 символов'
    
    return errors

# ========== API МАРШРУТЫ ==========

@lab7.route('/lab7/')
def main():
    """Главная страница"""
    # Инициализируем базу при первом заходе
    try:
        init_database()
    except:
        pass
    return render_template('lab7/lab7.html')

@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    """Получить все фильмы"""
    try:
        conn, cur = db_connect()
        
        cur.execute("SELECT id, title, title_ru, year, description FROM films ORDER BY id")
        
        films = []
        for row in cur.fetchall():
            films.append({
                'id': row['id'] - 1,  # Преобразуем ID для фронтенда
                'title': row['title'],
                'title_ru': row['title_ru'],
                'year': row['year'],
                'description': row['description']
            })
        
        db_close(conn, cur)
        return jsonify(films)
        
    except Exception as e:
        print(f"Ошибка при загрузке фильмов: {e}")
        # Попробуем инициализировать базу если её нет
        try:
            init_database()
            return jsonify([])
        except:
            return jsonify({'error': 'Ошибка сервера'}), 500

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    """Получить один фильм по ID"""
    try:
        conn, cur = db_connect()
        
        db_id = id + 1  # Преобразуем ID
        
        if current_app.config.get('DB_TYPE', 'postgres') == 'postgres':
            cur.execute("SELECT id, title, title_ru, year, description FROM films WHERE id = %s", (db_id,))
        else:
            cur.execute("SELECT id, title, title_ru, year, description FROM films WHERE id = ?", (db_id,))
        
        row = cur.fetchone()
        
        db_close(conn, cur)
        
        if not row:
            abort(404)
        
        return jsonify({
            'id': id,
            'title': row['title'],
            'title_ru': row['title_ru'],
            'year': row['year'],
            'description': row['description']
        })
        
    except Exception as e:
        print(f"Ошибка при получении фильма: {e}")
        return jsonify({'error': 'Ошибка сервера'}), 500

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    """Удалить фильм"""
    try:
        conn, cur = db_connect()
        
        db_id = id + 1
        
        if current_app.config.get('DB_TYPE', 'postgres') == 'postgres':
            cur.execute("SELECT id FROM films WHERE id = %s", (db_id,))
        else:
            cur.execute("SELECT id FROM films WHERE id = ?", (db_id,))
        
        if not cur.fetchone():
            db_close(conn, cur)
            abort(404)
        
        if current_app.config.get('DB_TYPE', 'postgres') == 'postgres':
            cur.execute("DELETE FROM films WHERE id = %s", (db_id,))
        else:
            cur.execute("DELETE FROM films WHERE id = ?", (db_id,))
        
        db_close(conn, cur)
        
        return '', 204
        
    except Exception as e:
        print(f"Ошибка при удалении фильма: {e}")
        return jsonify({'error': 'Ошибка сервера'}), 500

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT'])
def put_film(id):
    """Обновить фильм"""
    try:
        film = request.get_json()
        
        # Валидация
        errors = validate_film(film)
        if errors:
            return jsonify(errors), 400
        
        # Подготовка данных
        title_ru = film.get('title_ru', '').strip()
        title = film.get('title', '').strip()
        
        if title_ru and not title:
            title = title_ru
        
        description = film.get('description', '').strip()
        year = int(film.get('year', 0))
        
        conn, cur = db_connect()
        
        db_id = id + 1
        
        if current_app.config.get('DB_TYPE', 'postgres') == 'postgres':
            cur.execute("SELECT id FROM films WHERE id = %s", (db_id,))
        else:
            cur.execute("SELECT id FROM films WHERE id = ?", (db_id,))
        
        if not cur.fetchone():
            db_close(conn, cur)
            abort(404)
        
        if current_app.config.get('DB_TYPE', 'postgres') == 'postgres':
            cur.execute("""
                UPDATE films 
                SET title = %s, title_ru = %s, year = %s, description = %s 
                WHERE id = %s 
                RETURNING id, title, title_ru, year, description
            """, (title, title_ru, year, description, db_id))
            
            updated_row = cur.fetchone()
        else:
            cur.execute("""
                UPDATE films 
                SET title = ?, title_ru = ?, year = ?, description = ? 
                WHERE id = ?
            """, (title, title_ru, year, description, db_id))
            
            # Получаем обновленную запись
            cur.execute("SELECT id, title, title_ru, year, description FROM films WHERE id = ?", (db_id,))
            updated_row = cur.fetchone()
        
        db_close(conn, cur)
        
        return jsonify({
            'id': id,
            'title': updated_row['title'],
            'title_ru': updated_row['title_ru'],
            'year': updated_row['year'],
            'description': updated_row['description']
        })
        
    except Exception as e:
        print(f"Ошибка при обновлении фильма: {e}")
        return jsonify({'error': 'Ошибка сервера'}), 500

@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    """Добавить новый фильм"""
    try:
        film = request.get_json()
        
        # Валидация
        errors = validate_film(film)
        if errors:
            return jsonify(errors), 400
        
        # Подготовка данных
        title_ru = film.get('title_ru', '').strip()
        title = film.get('title', '').strip()
        
        if title_ru and not title:
            title = title_ru
        
        description = film.get('description', '').strip()
        year = int(film.get('year', 0))
        
        conn, cur = db_connect()
        
        if current_app.config.get('DB_TYPE', 'postgres') == 'postgres':
            cur.execute("""
                INSERT INTO films (title, title_ru, year, description) 
                VALUES (%s, %s, %s, %s) 
                RETURNING id
            """, (title, title_ru, year, description))
            
            new_id = cur.fetchone()[0]
        else:
            cur.execute("""
                INSERT INTO films (title, title_ru, year, description) 
                VALUES (?, ?, ?, ?)
            """, (title, title_ru, year, description))
            
            new_id = cur.lastrowid
        
        db_close(conn, cur)
        
        return jsonify({"id": new_id - 1}), 201
        
    except Exception as e:
        print(f"Ошибка при добавлении фильма: {e}")
        return jsonify({'error': 'Ошибка сервера'}), 500

@lab7.route('/lab7/db-check/')
def db_check():
    """Проверка подключения к БД"""
    try:
        conn, cur = db_connect()
        
        cur.execute("SELECT COUNT(*) FROM films")
        count = cur.fetchone()[0]
        
        if current_app.config.get('DB_TYPE', 'postgres') == 'postgres':
            cur.execute("SELECT version()")
            version = cur.fetchone()[0]
            db_type = 'PostgreSQL'
        else:
            cur.execute("SELECT sqlite_version()")
            version = cur.fetchone()[0]
            db_type = 'SQLite'
        
        db_close(conn, cur)
        
        return jsonify({
            'status': 'ok',
            'film_count': count,
            'database_type': db_type,
            'version': version,
            'message': f'База данных ({db_type}) подключена, фильмов: {count}'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
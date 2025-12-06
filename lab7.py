from flask import Blueprint, render_template, request, abort, jsonify
from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor

lab7 = Blueprint('lab7', __name__)

# ========== ПОДКЛЮЧЕНИЕ К БАЗЕ ДАННЫХ ==========

def get_db_connection():
    """Подключение к PostgreSQL на порту 5433"""
    conn = psycopg2.connect(
        host='127.0.0.1',
        port=5433,  # ПОРТ 5433 для KOMPAS-3D
        database='alice_dyachkova_knowledge_base2',
        user='alice_dyachkova_knowledge_base',
        password='123456',
        cursor_factory=DictCursor
    )
    return conn

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
    return render_template('lab7/lab7.html')

@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    """Получить все фильмы"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, title, title_ru, year, description FROM films ORDER BY id")
        
        films = []
        for row in cursor.fetchall():
            films.append({
                'id': row['id'] - 1,  # Преобразуем ID для фронтенда
                'title': row['title'],
                'title_ru': row['title_ru'],
                'year': row['year'],
                'description': row['description']
            })
        
        cursor.close()
        conn.close()
        
        return jsonify(films)
        
    except Exception as e:
        print(f"Ошибка при загрузке фильмов: {e}")
        return jsonify({'error': 'Ошибка сервера'}), 500

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    """Получить один фильм по ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        db_id = id + 1  # Преобразуем ID
        
        cursor.execute("SELECT id, title, title_ru, year, description FROM films WHERE id = %s", (db_id,))
        row = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
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
        conn = get_db_connection()
        cursor = conn.cursor()
        
        db_id = id + 1
        
        cursor.execute("SELECT id FROM films WHERE id = %s", (db_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            abort(404)
        
        cursor.execute("DELETE FROM films WHERE id = %s", (db_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
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
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        db_id = id + 1
        
        # Проверяем существование
        cursor.execute("SELECT id FROM films WHERE id = %s", (db_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            abort(404)
        
        # Обновляем
        cursor.execute("""
            UPDATE films 
            SET title = %s, title_ru = %s, year = %s, description = %s 
            WHERE id = %s 
            RETURNING id, title, title_ru, year, description
        """, (title, title_ru, year, description, db_id))
        
        updated_row = cursor.fetchone()
        conn.commit()
        
        cursor.close()
        conn.close()
        
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
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Добавляем
        cursor.execute("""
            INSERT INTO films (title, title_ru, year, description) 
            VALUES (%s, %s, %s, %s) 
            RETURNING id
        """, (title, title_ru, year, description))
        
        new_id = cursor.fetchone()[0]
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"id": new_id - 1}), 201
        
    except Exception as e:
        print(f"Ошибка при добавлении фильма: {e}")
        return jsonify({'error': 'Ошибка сервера'}), 500

@lab7.route('/lab7/db-check/')
def db_check():
    """Проверка подключения к БД"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM films")
        count = cursor.fetchone()[0]
        
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'ok',
            'film_count': count,
            'postgres_version': version,
            'message': f'База данных подключена, фильмов: {count}'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
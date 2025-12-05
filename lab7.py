from flask import Blueprint, render_template, request, abort, jsonify
from datetime import datetime

lab7 = Blueprint('lab7', __name__)

@lab7.route('/lab7/')
def main():
    return render_template('lab7/lab7.html')

# Начальный список фильмов (5 штук как в задании)
films = [
    {
        "title": "The Shawshank Redemption",
        "title_ru": "Побег из Шоушенка",
        "year": 1994,
        "description": "Два заключенных создают крепкую дружбу, чтобы выжить в тюрьме, обретая искупление через действия простой доброты."
    },
    {
        "title": "The Godfather",
        "title_ru": "Крестный отец",
        "year": 1972,
        "description": "Стареющий патриарх организованной преступной династии передает контроль над своей подпольной империей своему неохотному сыну."
    },
    {
        "title": "The Dark Knight",
        "title_ru": "Темный рыцарь",
        "year": 2008,
        "description": "Когда в Готэм-Сити появляется угроза, известная как Джокер, Бэтмен должен противостоять хаосу, который тот сеет."
    },
    {
        "title": "Pulp Fiction",
        "title_ru": "Криминальное чтиво",
        "year": 1994,
        "description": "Жизни двух киллеров, боксера, гангстера и его жены переплетаются в четырех историях о насилии и искуплении."
    },
    {
        "title": "Forrest Gump",
        "title_ru": "Форрест Гамп",
        "year": 1994,
        "description": "История жизни Форреста Гампа, человека с низким IQ, который невольно становится свидетелем и участником ключевых исторических событий США."
    }
]

def validate_film(film):
    """Валидация данных фильма"""
    errors = {}
    
    # 1. Русское название — должно быть непустым
    title_ru = film.get('title_ru', '').strip()
    if not title_ru:
        errors['title_ru'] = 'Русское название обязательно'
    
    # 2. Оригинальное название — должно быть непустым, если русское пустое
    # (но мы уже проверили что русское не пустое, так что эта проверка вторична)
    title = film.get('title', '').strip()
    if not title_ru and not title:
        errors['title'] = 'Хотя бы одно название должно быть заполнено'
    
    # 3. Год — должен быть от 1895 до текущего
    try:
        year = int(film.get('year', 0))
        current_year = datetime.now().year
        if year < 1895 or year > current_year:
            errors['year'] = f'Год должен быть от 1895 до {current_year}'
    except (ValueError, TypeError):
        errors['year'] = 'Год должен быть числом'
    
    # 4. Описание — должно быть непустым, но не более 2000 символов
    description = film.get('description', '').strip()
    if not description:
        errors['description'] = 'Описание обязательно'
    elif len(description) > 2000:
        errors['description'] = 'Описание не должно превышать 2000 символов'
    
    return errors

@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    return jsonify(films)

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    if id < 0 or id >= len(films):
        abort(404)
    return jsonify(films[id])

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    if id < 0 or id >= len(films):
        abort(404)
    del films[id]
    return '', 204

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT'])
def put_film(id):
    if id < 0 or id >= len(films):
        abort(404)
    
    film = request.get_json()
    
    # Валидация данных
    errors = validate_film(film)
    if errors:
        return jsonify(errors), 400
    
    # Если русское название есть, а оригинальное пустое - копируем русское в оригинальное
    title_ru = film.get('title_ru', '').strip()
    title = film.get('title', '').strip()
    
    if title_ru and (not title or title.strip() == ''):
        film['title'] = title_ru
    
    films[id] = film
    return jsonify(films[id])

@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    film = request.get_json()
    
    # Валидация данных
    errors = validate_film(film)
    if errors:
        return jsonify(errors), 400
    
    # Если русское название есть, а оригинальное пустое - копируем русское в оригинальное
    title_ru = film.get('title_ru', '').strip()
    title = film.get('title', '').strip()
    
    if title_ru and (not title or title.strip() == ''):
        film['title'] = title_ru
    
    films.append(film)
    return jsonify({"id": len(films) - 1}), 201
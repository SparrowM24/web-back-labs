from flask import Blueprint, render_template, request, abort, jsonify

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

# 1. Получение всех фильмов
@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    return jsonify(films)

# 2. Получение одного фильма
@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    if id < 0 or id >= len(films):
        abort(404, description="Фильм с таким индексом не найден")
    return jsonify(films[id])

# 3. Удаление фильма
@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    if id < 0 or id >= len(films):
        abort(404, description=f"Фильм с индексом {id} не найден. Невозможно удалить.")
    del films[id]
    return '', 204

# 4. Редактирование фильма
@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT'])
def put_film(id):
    if id < 0 or id >= len(films):
        abort(404, description=f"Фильм с индексом {id} не найден. Невозможно внести изменения.")
    
    film = request.get_json()
    films[id] = film
    return jsonify(films[id])

# 5. Добавление нового фильма
@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    film = request.get_json()
    films.append(film)
    return jsonify({"id": len(films) - 1}), 201

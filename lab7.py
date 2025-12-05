from flask import Blueprint, render_template, request, make_response, redirect, abort
lab7 = Blueprint('lab7', __name__)


@lab7.route('/lab7/')
def main():
    return render_template('lab7/lab7.html')

films = [
    {
        "title": "Spirited Away",
        "title_ru": "Унесённые призраками",
        "year": 2001,
        "description": "Десятилетняя Тихиро вместе с родителями попадает в странный мир духов. Чтобы спасти маму и папу, превращённых в свиней, ей предстоит работать в таинственных банях и встретиться с могущественным колдуном."
    },
    {
        "title": "Stalker",
        "title_ru": "Сталкер",
        "year": 1979,
        "description": "Проводник (Сталкер) ведёт двух своих клиентов — Писателя и Профессора — через опасную «Зону», где, по слухам, существует комната, исполняющая самые заветные желания."
    },
    {
        "title": "The Grand Budapest Hotel",
        "title_ru": "Отель «Гранд Будапешт»",
        "year": 2014,
        "description": "Невероятные приключения легендарного консьержа отеля и его юного помощника, ставших обладателями бесценного произведения искусства и втянутых в семейную вражду из-за огромного состояния."
    }
]


@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    return films


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    if id < 0 or id >= len(films):
        abort(404, description="Фильм с таким индексом не найден")
    
    return films[id]


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    if id < 0 or id >= len(films):
        abort(404, description=f"Фильм с индексом {id} не найден. Невозможно удалить.")
    del films[id]
    return '', 204


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT'])
def put_film(id):
    if id < 0 or id >= len(films):
        abort(404), description=f"Фильм с индексом {id} не найден. Невозможно внести изменения."
    
    film = request.get_json()
    films[id] = film
    return films[id]


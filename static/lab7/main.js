let currentFilmId = null; // Для отслеживания редактируемого фильма

// Функция для заполнения таблицы фильмами
function fillFilmList() {
    fetch('/lab7/rest-api/films/')
        .then(function(response) {
            return response.json();
        })
        .then(function(films) {
            let tbody = document.getElementById('film-list');
            tbody.innerHTML = '';
            
            for(let i = 0; i < films.length; i++) {
                let tr = document.createElement('tr');
                
                let tdTitle = document.createElement('td');
                let tdTitleRu = document.createElement('td');
                let tdYear = document.createElement('td');
                let tdDescription = document.createElement('td');
                let tdActions = document.createElement('td');
                
                // Оригинальное название (только если отличается от русского)
                tdTitle.innerText = films[i].title === films[i].title_ru ? '' : films[i].title;
                
                // Русское название
                tdTitleRu.innerText = films[i].title_ru;
                
                // Год выпуска
                tdYear.innerText = films[i].year;
                
                // Описание (сокращаем если слишком длинное)
                let description = films[i].description;
                if (description.length > 100) {
                    description = description.substring(0, 100) + '...';
                }
                tdDescription.innerText = description;
                
                // Кнопки действий
                let editButton = document.createElement('button');
                editButton.innerText = 'редактировать';
                editButton.onclick = function() {
                    editFilm(i, films[i]);
                };

                let delButton = document.createElement('button');
                delButton.innerText = 'удалить';
                delButton.onclick = function() {
                    let filmTitle = films[i].title_ru || films[i].title || 'фильм';
                    deleteFilm(i, filmTitle);
                };

                tdActions.append(editButton);
                tdActions.append(delButton);

                // Добавляем ячейки в строку
                tr.append(tdTitle);
                tr.append(tdTitleRu);
                tr.append(tdYear);
                tr.append(tdDescription);
                tr.append(tdActions);
                
                // Добавляем строку в таблицу
                tbody.append(tr);
            }
        })
        .catch(function(error) {
            console.error('Ошибка при загрузке фильмов:', error);
            document.getElementById('film-list').innerHTML = 
                '<tr><td colspan="5">Ошибка загрузки данных</td></tr>';
        });
}

// Функция удаления фильма
function deleteFilm(id, title) {
    if(! confirm('Вы точно хотите удалить фильм "' + title + '"?'))
        return;

    fetch('/lab7/rest-api/films/' + id, {method: 'DELETE'})
    .then(function(response) {
        if (response.ok) {
            fillFilmList();
        }
    });
}

// Показать модальное окно
function showModal() {
    document.getElementById('filmModal').style.display = 'block';
}

// Скрыть модальное окно
function hideModal() {
    document.getElementById('filmModal').style.display = 'none';
    clearForm();
}

// Очистить форму
function clearForm() {
    document.getElementById('filmId').value = '';
    document.getElementById('title_ru').value = '';
    document.getElementById('title').value = '';
    document.getElementById('year').value = '';
    document.getElementById('description').value = '';
    document.getElementById('modalTitle').innerText = 'Добавить фильм';
    currentFilmId = null;
}

// Отмена
function cancel() {
    hideModal();
}

// Добавить фильм
function addFilm() {
    clearForm();
    document.getElementById('modalTitle').innerText = 'Добавить фильм';
    showModal();
}

// Редактировать фильм
function editFilm(id, film) {
    currentFilmId = id;
    
    // Заполняем форму данными фильма
    document.getElementById('filmId').value = id;
    document.getElementById('title_ru').value = film.title_ru || '';
    document.getElementById('title').value = film.title || '';
    document.getElementById('year').value = film.year || '';
    document.getElementById('description').value = film.description || '';
    
    document.getElementById('modalTitle').innerText = 'Редактировать фильм';
    showModal();
}

// Сохранить фильм (добавить или обновить)
function saveFilm() {
    const filmData = {
        title_ru: document.getElementById('title_ru').value,
        title: document.getElementById('title').value,
        year: parseInt(document.getElementById('year').value),
        description: document.getElementById('description').value
    };
    
    // Проверка обязательных полей
    if (!filmData.title_ru.trim()) {
        alert('Пожалуйста, введите название на русском');
        return;
    }
    
    if (currentFilmId === null) {
        // Добавление нового фильма
        fetch('/lab7/rest-api/films/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(filmData)
        })
        .then(response => {
            if (response.ok) {
                hideModal();
                fillFilmList();
            }
        });
    } else {
        // Редактирование существующего фильма
        fetch(`/lab7/rest-api/films/${currentFilmId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(filmData)
        })
        .then(response => {
            if (response.ok) {
                hideModal();
                fillFilmList();
            }
        });
    }
}

// Загружаем фильмы при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    fillFilmList();
    
    // Закрыть модальное окно при клике вне его
    window.onclick = function(event) {
        const modal = document.getElementById('filmModal');
        if (event.target == modal) {
            hideModal();
        }
    }
});
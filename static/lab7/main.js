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
                if (description && description.length > 100) {
                    description = description.substring(0, 100) + '...';
                }
                tdDescription.innerText = description || '';
                
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

// Очистить сообщение об ошибке
function clearError() {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.innerText = '';
        errorDiv.style.display = 'none';
    }
}

// Показать сообщение об ошибке
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.innerText = message;
        errorDiv.style.display = 'block';
    } else {
        // Если блока ошибок нет, показываем alert
        alert(message);
    }
}

// Показать модальное окно
function showModal() {
    document.getElementById('filmModal').style.display = 'block';
    clearError(); // Очищаем ошибки при открытии модального окна
}

// Скрыть модальное окно
function hideModal() {
    document.getElementById('filmModal').style.display = 'none';
    clearForm();
    clearError();
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
    clearError();
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
    
    clearError(); // Очищаем ошибки при открытии
    document.getElementById('modalTitle').innerText = 'Редактировать фильм';
    showModal();
}

// Сохранить фильм (добавить или обновить)
function saveFilm() {
    const filmData = {
        title_ru: document.getElementById('title_ru').value,
        title: document.getElementById('title').value,
        year: parseInt(document.getElementById('year').value) || 0,
        description: document.getElementById('description').value
    };
    
    // Проверка обязательных полей на фронтенде
    if (!filmData.title_ru.trim()) {
        showError('Пожалуйста, введите название на русском');
        return;
    }
    
    clearError(); // Очищаем предыдущие ошибки
    
    let url, method;
    
    if (currentFilmId === null) {
        // Добавление нового фильма
        url = '/lab7/rest-api/films/';
        method = 'POST';
    } else {
        // Редактирование существующего фильма
        url = '/lab7/rest-api/films/' + currentFilmId;
        method = 'PUT';
    }
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(filmData)
    })
    .then(function(response) {
        if (response.ok) {
            // Если успешно, возвращаем пустой объект
            return {};
        } else {
            // Если ошибка, парсим JSON с ошибкой
            return response.json();
        }
    })
    .then(function(data) {
        if (data.description) {
            // Показать ошибку с сервера
            showError(data.description);
        } else {
            // Успешно - скрываем модальное окно и обновляем список
            hideModal();
            fillFilmList();
        }
    })
    .catch(function(error) {
        console.error('Ошибка:', error);
        showError('Произошла ошибка при сохранении');
    });
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
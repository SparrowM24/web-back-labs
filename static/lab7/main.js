let currentFilmId = null;

// Функция для заполнения таблицы фильмами
function fillFilmList() {
    fetch('/lab7/rest-api/films/')
        .then(function(response) {
            return response.json();
        })
        .then(function(films) {
            console.log('Получены фильмы:', films);
            
            let tbody = document.getElementById('film-list');
            if (!tbody) {
                console.error('Не найден элемент #film-list');
                return;
            }
            
            tbody.innerHTML = '';
            
            for(let i = 0; i < films.length; i++) {
                let film = films[i];
                
                let tr = document.createElement('tr');
                
                // 1. РУССКОЕ НАЗВАНИЕ
                let tdTitleRu = document.createElement('td');
                tdTitleRu.textContent = film.title_ru || '';
                
                // 2. ОРИГИНАЛЬНОЕ НАЗВАНИЕ
                let tdTitle = document.createElement('td');
                let originalTitle = film.title || '';
                
                if (originalTitle) {
                    if (originalTitle === film.title_ru) {
                        tdTitle.innerHTML = '<span class="original-title">(то же)</span>';
                    } else {
                        tdTitle.innerHTML = '<span class="original-title">' + originalTitle + '</span>';
                    }
                } else {
                    tdTitle.innerHTML = '<span class="original-title">—</span>';
                }
                
                // 3. Год
                let tdYear = document.createElement('td');
                tdYear.textContent = film.year || '';
                
                // 4. Описание
                let tdDescription = document.createElement('td');
                let description = film.description || '';
                if (description.length > 100) {
                    description = description.substring(0, 100) + '...';
                }
                tdDescription.textContent = description;
                
                // 5. Кнопки
                let tdActions = document.createElement('td');
                
                let editButton = document.createElement('button');
                editButton.textContent = 'редактировать';
                editButton.onclick = function() {
                    editFilm(i, film);
                };

                let delButton = document.createElement('button');
                delButton.textContent = 'удалить';
                delButton.onclick = function() {
                    deleteFilm(i, film.title_ru || film.title || 'фильм');
                };

                tdActions.appendChild(editButton);
                tdActions.appendChild(delButton);

                tr.appendChild(tdTitleRu);
                tr.appendChild(tdTitle);
                tr.appendChild(tdYear);
                tr.appendChild(tdDescription);
                tr.appendChild(tdActions);
                
                tbody.appendChild(tr);
            }
        })
        .catch(function(error) {
            console.error('Ошибка при загрузке фильмов:', error);
            let tbody = document.getElementById('film-list');
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="5">Ошибка загрузки данных</td></tr>';
            }
        });
}

// Функция удаления фильма
function deleteFilm(id, title) {
    if(! confirm('Вы точно хотите удалить фильм "' + title + '"?'))
        return;

    fetch('/lab7/rest-api/films/' + id, {method: 'DELETE'})
    .then(function() {
        fillFilmList();
    });
}

// Очистить сообщение об ошибке
function clearError() {
    let errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = '';
        errorDiv.style.display = 'none';
    }
}

// Показать сообщение об ошибке
function showError(message) {
    let errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.innerHTML = message;
        errorDiv.style.display = 'block';
    }
}

// Показать модальное окно
function showModal() {
    document.getElementById('filmModal').style.display = 'block';
    clearError();
}

// Скрыть модальное окно
function hideModal() {
    document.getElementById('filmModal').style.display = 'none';
    clearForm();
    clearError();
}

// Очистить форму
function clearForm() {
    document.getElementById('title_ru').value = '';
    document.getElementById('title').value = '';
    document.getElementById('year').value = '';
    document.getElementById('description').value = '';
    document.getElementById('modalTitle').textContent = 'Добавить фильм';
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
    document.getElementById('modalTitle').textContent = 'Добавить фильм';
    showModal();
}

// Редактировать фильм
function editFilm(id, film) {
    currentFilmId = id;
    
    document.getElementById('title_ru').value = film.title_ru || '';
    document.getElementById('title').value = film.title || '';
    document.getElementById('year').value = film.year || '';
    document.getElementById('description').value = film.description || '';
    
    clearError();
    document.getElementById('modalTitle').textContent = 'Редактировать фильм';
    showModal();
}

// Сохранить фильм
function saveFilm() {
    let filmData = {
        title_ru: document.getElementById('title_ru').value.trim(),
        title: document.getElementById('title').value.trim(),
        year: parseInt(document.getElementById('year').value) || 0,
        description: document.getElementById('description').value.trim()
    };
    
    clearError();
    
    let url, method;
    
    if (currentFilmId === null) {
        url = '/lab7/rest-api/films/';
        method = 'POST';
    } else {
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
            return {};
        } else {
            return response.json();
        }
    })
    .then(function(data) {
        if (Object.keys(data).length > 0) {
            // Показываем все ошибки
            let errorMessages = [];
            if (data.title_ru) errorMessages.push(data.title_ru);
            if (data.title) errorMessages.push(data.title);
            if (data.year) errorMessages.push(data.year);
            if (data.description) errorMessages.push(data.description);
            
            showError(errorMessages.join('<br>'));
        } else {
            hideModal();
            fillFilmList();
        }
    })
    .catch(function(error) {
        console.error('Ошибка:', error);
        showError('Ошибка при сохранении');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    fillFilmList();
    
    window.onclick = function(event) {
        let modal = document.getElementById('filmModal');
        if (event.target === modal) {
            hideModal();
        }
    };
});
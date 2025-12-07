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
                
                console.log(`Фильм ${i}: ID=${film.id}, Название="${film.title_ru}"`);
                
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
                
                // 5. Кнопки - ИСПРАВЛЕНО: используем film.id вместо i
                let tdActions = document.createElement('td');
                
                let editButton = document.createElement('button');
                editButton.textContent = 'редактировать';
                editButton.onclick = function() {
                    console.log(`Редактировать фильм с ID=${film.id}`);
                    editFilm(film.id, film);  // <- ИСПРАВЛЕНО: film.id
                };

                let delButton = document.createElement('button');
                delButton.textContent = 'удалить';
                delButton.onclick = function() {
                    console.log(`Удалить фильм с ID=${film.id}`);
                    deleteFilm(film.id, film.title_ru || film.title || 'фильм');  // <- ИСПРАВЛЕНО: film.id
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

// Функция удаления фильма - добавьте логирование
function deleteFilm(id, title) {
    console.log(`Попытка удаления: ID=${id}, Название="${title}"`);
    
    if(! confirm('Вы точно хотите удалить фильм "' + title + '"?'))
        return;

    fetch('/lab7/rest-api/films/' + id, {method: 'DELETE'})
    .then(function(response) {
        console.log(`Статус ответа: ${response.status}`);
        if (response.status === 204) {
            console.log('Фильм успешно удален');
            fillFilmList();
        } else if (response.status === 404) {
            alert('Фильм не найден! Возможно он уже был удален.');
            fillFilmList(); // Обновляем список
        } else {
            console.error('Ошибка при удалении:', response.status);
            alert('Ошибка при удалении фильма');
        }
    })
    .catch(function(error) {
        console.error('Ошибка при удалении:', error);
        alert('Ошибка при удалении фильма: ' + error);
    });
}

// Функция редактирования фильма - тоже исправляем
function editFilm(id, film) {
    console.log(`Редактирование фильма с ID=${id}`);
    currentFilmId = id;  // Используем реальный ID
    
    document.getElementById('title_ru').value = film.title_ru || '';
    document.getElementById('title').value = film.title || '';
    document.getElementById('year').value = film.year || '';
    document.getElementById('description').value = film.description || '';
    
    clearError();
    document.getElementById('modalTitle').textContent = 'Редактировать фильм';
    showModal();
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

// Сохранить фильм
function saveFilm() {
    let filmData = {
        title_ru: document.getElementById('title_ru').value.trim(),
        title: document.getElementById('title').value.trim(),
        year: parseInt(document.getElementById('year').value) || 0,
        description: document.getElementById('description').value.trim()
    };
    
    console.log('Сохранение фильма:', filmData);
    console.log('Текущий ID:', currentFilmId);
    
    clearError();
    
    let url, method;
    
    if (currentFilmId === null) {
        url = '/lab7/rest-api/films/';
        method = 'POST';
    } else {
        url = '/lab7/rest-api/films/' + currentFilmId;
        method = 'PUT';
    }
    
    console.log(`Отправка запроса: ${method} ${url}`);
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(filmData)
    })
    .then(function(response) {
        console.log('Ответ сервера:', response.status);
        if (response.ok) {
            return {};
        } else {
            return response.json();
        }
    })
    .then(function(data) {
        if (Object.keys(data).length > 0) {
            console.log('Ошибки валидации:', data);
            // Показываем все ошибки
            let errorMessages = [];
            if (data.title_ru) errorMessages.push(data.title_ru);
            if (data.title) errorMessages.push(data.title);
            if (data.year) errorMessages.push(data.year);
            if (data.description) errorMessages.push(data.description);
            
            showError(errorMessages.join('<br>'));
        } else {
            console.log('Сохранение успешно');
            hideModal();
            fillFilmList();
        }
    })
    .catch(function(error) {
        console.error('Ошибка:', error);
        showError('Ошибка при сохранении');
    });
}

// Добавьте функцию для проверки базы данных
function checkDatabase() {
    fetch('/lab7/rest-api/films/')
        .then(response => response.json())
        .then(films => {
            console.log('Проверка базы:', films);
            alert(`В базе ${films.length} фильмов:\n${films.map(f => `ID=${f.id}: ${f.title_ru}`).join('\n')}`);
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Ошибка при проверке базы');
        });
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('Страница загружена');
    fillFilmList();
    
    window.onclick = function(event) {
        let modal = document.getElementById('filmModal');
        if (event.target === modal) {
            hideModal();
        }
    };
});
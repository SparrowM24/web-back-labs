// Меняем порядок: сначала русское, потом оригинальноеlet currentFilmId = null;

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
                
                // 1. РУССКОЕ НАЗВАНИЕ (теперь первый столбец)
                let tdTitleRu = document.createElement('td');
                tdTitleRu.textContent = film.title_ru || '';
                
                // 2. ОРИГИНАЛЬНОЕ НАЗВАНИЕ (теперь второй столбец, оформляем курсивом)
                let tdTitle = document.createElement('td');
                let originalTitle = film.title || '';
                
                if (originalTitle) {
                    // Если оригинальное название есть, показываем его курсивом
                    if (originalTitle === film.title_ru) {
                        // Если названия одинаковые, показываем "то же"
                        tdTitle.innerHTML = '<span class="original-title">(то же)</span>';
                    } else {
                        // Если разные, показываем оригинальное название курсивом
                        tdTitle.innerHTML = '<span class="original-title">' + originalTitle + '</span>';
                    }
                } else {
                    // Если оригинального названия нет
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

                // Меняем порядок: сначала русское, потом оригинальное
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

// Остальные функции остаются БЕЗ изменений:
function deleteFilm(id, title) {
    if(! confirm('Вы точно хотите удалить фильм "' + title + '"?'))
        return;

    fetch('/lab7/rest-api/films/' + id, {method: 'DELETE'})
    .then(function() {
        fillFilmList();
    });
}

function clearError() {
    let errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = '';
        errorDiv.style.display = 'none';
    }
}

function showError(message) {
    let errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
}

function showModal() {
    document.getElementById('filmModal').style.display = 'block';
    clearError();
}

function hideModal() {
    document.getElementById('filmModal').style.display = 'none';
    clearForm();
    clearError();
}

function clearForm() {
    document.getElementById('title_ru').value = '';
    document.getElementById('title').value = '';
    document.getElementById('year').value = '';
    document.getElementById('description').value = '';
    document.getElementById('modalTitle').textContent = 'Добавить фильм';
    currentFilmId = null;
}

function cancel() {
    hideModal();
}

function addFilm() {
    clearForm();
    clearError();
    document.getElementById('modalTitle').textContent = 'Добавить фильм';
    showModal();
}

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

function saveFilm() {
    let filmData = {
        title_ru: document.getElementById('title_ru').value,
        title: document.getElementById('title').value,
        year: parseInt(document.getElementById('year').value) || 0,
        description: document.getElementById('description').value
    };
    
    if (!filmData.title_ru.trim()) {
        showError('Введите название на русском');
        return;
    }
    
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
        if (data.description) {
            showError(data.description);
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
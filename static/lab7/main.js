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
                
                // Описание
                tdDescription.innerText = films[i].description;
                
                // Кнопки действий
                let editButton = document.createElement('button');
                editButton.innerText = 'редактировать';
                editButton.onclick = function() {
                    editFilm(i);
                };

                let delButton = document.createElement('button');
                delButton.innerText = 'удалить';
                delButton.onclick = function() {
                    deleteFilm(i);
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
async function deleteFilm(id) {
    if (!confirm('Вы уверены, что хотите удалить фильм?')) {
        return;
    }
    
    try {
        const response = await fetch(`/lab7/rest-api/films/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            fillFilmList(); // Обновляем список
        }
    } catch (error) {
        console.error('Ошибка при удалении:', error);
        alert('Ошибка при удалении фильма');
    }
}

// Функция редактирования фильма (заглушка)
function editFilm(id) {
    alert(`Редактирование фильма с ID: ${id}\n(функция будет реализована позже)`);
}

// Функция добавления фильма (заглушка)
function addFilm() {
    alert('Добавление нового фильма\n(функция будет реализована позже)');
}

// Загружаем фильмы при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    fillFilmList();
});
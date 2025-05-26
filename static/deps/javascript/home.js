document.addEventListener('DOMContentLoaded', function() {
    // Основные элементы
    const searchForm = document.getElementById('searchForm');
    const toggleBtn = document.getElementById('toggleAdvanced');
    const advancedFields = document.getElementById('advancedFields');
    const addAuthorBtn = document.getElementById('addAuthorBtn'); // Кнопка "Добавить автора"
    const authorsContainer = document.getElementById('authorsContainer'); // Контейнер для авторов

    // Функция для добавления нового поля автора
    function addAuthorField() {
        const newAuthorInput = document.createElement('input');
        newAuthorInput.type = 'text';
        newAuthorInput.name = 'authors[]';
        newAuthorInput.placeholder = 'Фамилия автора';
        newAuthorInput.classList.add('author-input'); // Добавляем класс для стилизации

        const removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.classList.add('remove-author-button');
        removeButton.textContent = 'Удалить автора'; // Текст кнопки
        removeButton.addEventListener('click', function(event) {
            event.preventDefault();
            newFormGroup.remove();
            updateRemoveButtonsVisibility(); // Обновляем видимость кнопок после удаления
        });

        const newFormGroup = document.createElement('div');
        newFormGroup.classList.add('author-field-container'); // Для стилизации
        newFormGroup.appendChild(newAuthorInput);
        newFormGroup.appendChild(removeButton);

        authorsContainer.appendChild(newFormGroup);

        updateRemoveButtonsVisibility(); // Обновляем видимость кнопок после добавления
    }

    // Функция для обновления видимости кнопок "Удалить автора"
    function updateRemoveButtonsVisibility() {
        const authorFieldContainers = document.querySelectorAll('.author-field-container');
        authorFieldContainers.forEach((container, index) => {
            const removeButton = container.querySelector('.remove-author-button');
            if (removeButton) {
                removeButton.style.display = index === 0 && authorFieldContainers.length <= 1 ? 'none' : 'inline-block';
            }
        });
    }

    // Добавляем обработчик события на кнопку "Добавить автора"
    addAuthorBtn.addEventListener('click', addAuthorField);

    // Функция для сбора авторов из полей ввода
    function getAuthors() {
        const authorInputs = document.querySelectorAll('input[name="authors[]"]');
        const authors = Array.from(authorInputs).map(input => input.value).filter(value => value !== '');
        return authors;
    }

    // Остальной код (без изменений)
    // Поля формы
    const searchInput = document.querySelector('input[name="q"]');
    const keywordsInput = document.querySelector('input[name="keywords"]');
    const abstractInput = document.querySelector('input[name="abstract"]');
    const dateRangeInput = document.querySelector('input[name="dateRange"]');
    const pageInput = document.querySelector('input[name="page"]');

    // Проверяем наличие параметров в URL
    const urlParams = new URLSearchParams(window.location.search);
    const hasAdvancedParams = urlParams.has('authors') ||
        urlParams.has('keywords') ||
        urlParams.has('abstract') ||
        urlParams.has('dateRange');

    // Функция переключения расширенных полей
    function toggleAdvancedFields(show) {
        if (show === undefined) {
            show = advancedFields.style.display !== 'block';
        }
        advancedFields.style.display = show ? 'block' : 'none';
        toggleBtn.textContent = show ? 'Расширенный поиск ▲' : 'Расширенный поиск ▼';
        localStorage.setItem('advancedSearchVisible', show.toString());
    }

    // Заполняем поля формы из URL параметров
    function fillFormFromUrl() {
        if (urlParams.has('q')) {
            const query = urlParams.get('q');
            searchInput.value = query || '';
        }
        if (urlParams.has('authors')) {
            const authors = urlParams.getAll('authors');

            // Очищаем существующие поля авторов
            while (authorsContainer.firstChild) {
                authorsContainer.removeChild(authorsContainer.firstChild);
            }

            // Добавляем поля авторов из URL
            authors.forEach(author => {
                addAuthorField();
                const authorInputs = document.querySelectorAll('input[name="authors[]"]');
                authorInputs[authorInputs.length - 1].value = author;
            });

            // Если авторов в URL нет, добавляем одно пустое поле
            if (authors.length === 0) {
                addAuthorField();
            }
        }
        // Заполняем остальные поля, если они есть в URL
        if (urlParams.has('keywords')) keywordsInput.value = urlParams.get('keywords') || '';
        if (urlParams.has('abstract')) abstractInput.value = urlParams.get('abstract') || '';
        if (urlParams.has('dateRange')) dateRangeInput.value = urlParams.get('dateRange') || '';

        // Скрываем кнопку "Удалить автора" для первого поля
        updateRemoveButtonsVisibility();

        // Добавляем кнопку "Добавить автора" в контейнер
        authorsContainer.appendChild(addAuthorBtn);
    }

    // Очистка кавычек в полях ввода
    function sanitizeInputs() {
        const inputs = [searchInput, keywordsInput, abstractInput, dateRangeInput];
        inputs.forEach(input => {
            if (input.value) {
                input.value = input.value.replace(/"/g, '');
            }
        });
    }

    // Обработчик отправки формы
    function handleFormSubmit(e, pageNumber = null) {
        e.preventDefault();
        sanitizeInputs();

        const authors = getAuthors(); // Получаем список авторов

        // Формируем URL в стиле CORE
        let url = window.location.pathname + '?';
        const title = searchInput.value;
        const page = pageNumber !== null ? pageNumber : 1; // Используем переданный номер страницы или 1

        if (title) {
            url += 'q=' + encodeURIComponent(title);
        }

        if (authors.length > 0) {
            authors.forEach(author => {
                url += '&authors=' + encodeURIComponent(author);
            });
        }

        url += '&page=' + encodeURIComponent(page);

        window.location.href = url;
    }

    // Инициализация
    function init() {
        // Восстанавливаем состояние расширенного поиска
        const savedState = localStorage.getItem('advancedSearchVisible');
        toggleAdvancedFields(hasAdvancedParams || savedState === 'true');

        // Заполняем поля из URL
        fillFormFromUrl();

        // Назначаем обработчики событий
        toggleBtn.addEventListener('click', () => toggleAdvancedFields());
        searchForm.addEventListener('submit', (e) => handleFormSubmit(e));

        // Закрытие расширенных полей при клике вне формы
        document.addEventListener('click', (e) => {
            if (!searchForm.contains(e.target)) {
                toggleAdvancedFields(false);
            }
        });

        // Предотвращаем закрытие при клике внутри расширенных полей
        advancedFields.addEventListener('click', (e) => e.stopPropagation());

        // Обработчик для кнопок пагинации
        const paginationLinks = document.querySelectorAll('.pagination a');
        paginationLinks.forEach(link => {
            link.addEventListener('click', function(event) {
                event.preventDefault();
                // Получаем номер страницы из ссылки
                const pageNumber = this.getAttribute('href').split('page=')[1];
                handleFormSubmit(event, pageNumber); // Вызываем handleFormSubmit с номером страницы
            });
        });
    }

    init();
});
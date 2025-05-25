document.addEventListener('DOMContentLoaded', function() {
    // Основные элементы
    const searchForm = document.getElementById('searchForm');
    const toggleBtn = document.getElementById('toggleAdvanced');
    const advancedFields = document.getElementById('advancedFields');
    // Поля формы
    const searchInput = document.querySelector('input[name="q"]');
    const authorsInput = document.querySelector('input[name="authors"]');
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
            // Разделяем название статьи и автора из строки запроса
            const parts = query.split(' AND authors:');
            // Заполняем поле названия статьи, если значение найдено
            searchInput.value = parts[0] || '';
            // Заполняем поле автора, если значение найдено
            if (parts.length > 1) {
                authorsInput.value = parts[1].replace(/"/g, '') || ''; // Удаляем все кавычки
            }
        }
        // Заполняем остальные поля, если они есть в URL
        if (urlParams.has('keywords')) keywordsInput.value = urlParams.get('keywords') || '';
        if (urlParams.has('abstract')) abstractInput.value = urlParams.get('abstract') || '';
        if (urlParams.has('dateRange')) dateRangeInput.value = urlParams.get('dateRange') || '';
    }
    // Очистка кавычек в полях ввода
    function sanitizeInputs() {
        const inputs = [searchInput, authorsInput, keywordsInput, abstractInput, dateRangeInput];
        inputs.forEach(input => {
            if (input.value) {
                input.value = input.value.replace(/"/g, '');
            }
        });
    }
    // Обработчик отправки формы
    function handleFormSubmit(e) {
        e.preventDefault();
        sanitizeInputs();
        pageInput.value = 1;
        const formData = new FormData(searchForm);
        const searchParams = new URLSearchParams();
        const title = formData.get('q');
        const author = formData.get('authors');
        const page = formData.get('page');
        if (title) {
            let query = title;
            if (author) {
                query += ' AND authors:"' + author + '"';
            }
            searchParams.append('q', query);
        }
        if (page) {
            searchParams.append('page', page);
        }
        const url = window.location.pathname + '?' + searchParams.toString();
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
        searchForm.addEventListener('submit', handleFormSubmit);
        // Закрытие расширенных полей при клике вне формы
        document.addEventListener('click', (e) => {
            if (!searchForm.contains(e.target)) {
                toggleAdvancedFields(false);
            }
        });
        // Предотвращаем закрытие при клике внутри расширенных полей
        advancedFields.addEventListener('click', (e) => e.stopPropagation());
    }
    init();
});
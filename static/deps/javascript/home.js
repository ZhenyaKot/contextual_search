// Сохраняем поисковый запрос в поле формы
        document.addEventListener('DOMContentLoaded', function() {
            const urlParams = new URLSearchParams(window.location.search);
            const searchQuery = urlParams.get('q');
            if (searchQuery) {
                const searchInput = document.querySelector('input[name="search_request"]');
                if (searchInput) {
                    searchInput.value = decodeURIComponent(searchQuery);
                }
            }
        });


document.querySelector('form').addEventListener('submit', function() {
    const titleInput = document.querySelector('[name="search_request"]');
    titleInput.value = titleInput.value.replace(/"/g, '');

    const authorsInput = document.querySelector('[name="authors"]');
    authorsInput.value = authorsInput.value.replace(/"/g, '');
});
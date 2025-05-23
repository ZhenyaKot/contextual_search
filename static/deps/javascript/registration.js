document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('register-form');
            const apiErrors = document.getElementById('api-errors');

            // Валидация пароля в реальном времени
            document.getElementById('id_password1').addEventListener('input', function() {
                validatePassword(this.value);
            });

            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                clearErrors();

                const submitBtn = document.getElementById('submit-btn');
                const btnText = document.getElementById('btn-text');
                const spinner = document.getElementById('spinner');

                // Показываем спиннер
                submitBtn.disabled = true;
                btnText.textContent = 'Регистрация...';
                spinner.style.display = 'block';

                try {
                    const formData = new FormData(form);
                    const response = await fetch(form.action, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                            'Accept': 'application/json'
                        }
                    });

                    const data = await response.json();

                    if (response.ok) {
                        // Успешная регистрация
                        if (data.access && data.refresh) {
                            // Сохраняем токены
                            localStorage.setItem('access_token', data.access);
                            localStorage.setItem('refresh_token', data.refresh);
                        }
                        window.location.href = "{% url 'home:search_view' %}";
                    } else {
                        // Обработка ошибок
                        if (data.errors) {
                            displayApiErrors(data.errors);
                        } else if (data.detail) {
                            showApiError(data.detail);
                        } else {
                            showApiError('Произошла неизвестная ошибка');
                        }
                    }
                } catch (error) {
                    showApiError('Ошибка соединения с сервером');
                    console.error('Error:', error);
                } finally {
                    submitBtn.disabled = false;
                    btnText.textContent = 'Зарегистрироваться';
                    spinner.style.display = 'none';
                }
            });

            function clearErrors() {
                // Очищаем все ошибки
                document.querySelectorAll('.field-errors').forEach(el => {
                    el.innerHTML = '';
                    el.style.display = 'none';
                });
                apiErrors.innerHTML = '';
                apiErrors.style.display = 'none';
            }

            function displayApiErrors(errors) {
                // Показываем ошибки для полей
                for (const field in errors) {
                    const errorElement = document.getElementById(`${field}-errors`);
                    if (errorElement) {
                        errorElement.innerHTML = errors[field].join('<br>');
                        errorElement.style.display = 'block';
                    } else {
                        // Общие ошибки
                        showApiError(errors[field].join('<br>'));
                    }
                }
            }

            function showApiError(message) {
                apiErrors.innerHTML = `<p>${message}</p>`;
                apiErrors.style.display = 'block';
            }

            function validatePassword(password) {
                // Валидация пароля в реальном времени
                const lengthHint = document.getElementById('length-hint');
                const numHint = document.getElementById('num-hint');
                const specialHint = document.getElementById('special-hint');

                // Проверка длины
                if (password.length >= 8) {
                    lengthHint.style.color = '#2ecc71';
                } else {
                    lengthHint.style.color = '#e74c3c';
                }

                // Проверка цифр
                if (/\d/.test(password)) {
                    numHint.style.color = '#2ecc71';
                } else {
                    numHint.style.color = '#e74c3c';
                }

                // Проверка спецсимволов
                if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
                    specialHint.style.color = '#2ecc71';
                } else {
                    specialHint.style.color = '#e74c3c';
                }
            }
        });
document.addEventListener('DOMContentLoaded', () => {
    const loginButton = document.getElementById('loginButton');
    const loginInput = document.getElementById('loginInput');
    const passwordInput = document.getElementById('passwordInput');

    loginButton.addEventListener('click', async () => {
        try {
            const response = await fetch('http://localhost:5000/auth', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    login: loginInput.value,
                    password: passwordInput.value
                })
            });

            if (!response.ok) throw new Error('Ошибка авторизации');

            const data = await response.json();

            if(data.user_id) {
                window.location.href = `index.html?user_id=${data.user_id}`;
            } else {
                throw new Error('Пользователь не найден');
            }
        } catch (error) {
            console.error(error);
            alert('Неверные данные для входа! Попробуйте снова.');
        }
    });
});
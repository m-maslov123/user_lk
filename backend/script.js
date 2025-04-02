document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get('user_id');

    if(!userId) {
        window.location.href = 'login.html';
        return;
    }
    let currentAvailableAmount = 0;

    // Элементы модального окна
    const modalOverlay = document.getElementById('modalOverlay');
    const closeModal = document.getElementById('closeModal');
    const transferButton = document.getElementById('transferButton');
    const amountInput = document.getElementById('amountInput');

    // Обработчики открытия/закрытия модалки
    document.querySelector('.action-button').addEventListener('click', () => {
        modalOverlay.style.display = 'block';
    });

    closeModal.addEventListener('click', () => closeModalWindow());
    modalOverlay.addEventListener('click', (e) => {
        if(e.target === modalOverlay) closeModalWindow();
    });

    // Инициализация данных
    fetch(`http://localhost:5000/get_user_data?user_id=${userId}`)
        .then(response => response.json())
        .then(data => {
            const userData = data[0];
            currentAvailableAmount = userData.available;
            updateUI(userData);
        })
        .catch(error => handleError(error));

    // Обработка перевода
    transferButton.addEventListener('click', () => {
        const amount = parseInt(amountInput.value);

        if(!amount || amount <= 0) {
            alert('Введите корректную сумму');
            return;
        }

        fetch(`http://localhost:5000/transaction?user_id=${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ amount: amount })
        })
        .then(response => response.json())
        .then(data => {
            currentAvailableAmount = data.data.available;
            updateAvailableAmount(currentAvailableAmount);
            document.querySelector('.card-balance').textContent =
                `${new Intl.NumberFormat('ru-RU').format(data.data.cash)} ₽`;
            closeModalWindow();
        })
        .catch(error => handleError(error));
    });

    function updateUI(userData) {
        updateAvailableAmount(userData.available);
        document.querySelector('.menu-title').textContent = `Здравствуйте, ${userData.name}!`;
        document.querySelector('.card-balance').textContent =
            `${new Intl.NumberFormat('ru-RU').format(userData.cash)} ₽`;
    }

    function closeModalWindow() {
        modalOverlay.style.display = 'none';
        amountInput.value = '';
    }

    function handleError(error) {
        console.error('Error:', error);
        document.querySelector('.available-amount').textContent = 'Ошибка иди нахуй';
        alert('Произошла ошибка, попробуйте позже');
    }
});

function updateAvailableAmount(newAmount) {
    const formattedAmount = new Intl.NumberFormat('ru-RU').format(newAmount);
    document.querySelector('.available-amount').textContent = `${formattedAmount} ₽`;
}
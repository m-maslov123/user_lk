document.querySelector('.menu-item').addEventListener('click', function() {
    this.textContent = this.textContent === 'Закрыть лимит' 
        ? 'Открыть лимит' 
        : 'Закрыть лимит';
});



document.querySelector('.disabled .available-amount').addEventListener('click', function() {
        const menuItem = document.getElementById('limitToggle');
        const mainContent = document.querySelector('.main-content');
        const availableAmount = document.querySelector('.available-amount');
        let originalAmount = availableAmount.textContent; // Сохраняем исходную сумму

        // Единый обработчик клика
        menuItem.addEventListener('click', function() {
            const isActive = this.classList.toggle('active');
            
            // Меняем текст кнопки
            this.textContent = isActive ? 'Открыть лимит' : 'Закрыть лимит';
            
            // Меняем фон и сумму
            if(isActive) {
                mainContent.classList.add('disabled');
                availableAmount.textContent = 'недоступно';
            } else {
                mainContent.classList.remove('disabled');
                availableAmount.textContent = originalAmount;
            }
        });
});
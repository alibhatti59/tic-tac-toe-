const cells = document.querySelectorAll('.cell');
let currentPlayer = 'X';

cells.forEach((cell) => {
    cell.addEventListener('click', () => {
        if (cell.textContent !== '') {
            return;
        }

        cell.textContent = currentPlayer;
        cell.setAttribute('aria-label', `${currentPlayer} mark`);
        currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
    });
});

const cells = document.querySelectorAll('.cell');
const status = document.querySelector('.status');
const newGameButton = document.querySelector('.new-game');
const cellLabels = [...cells].map((cell) => cell.getAttribute('aria-label'));
let currentPlayer = 'X';
let gameOver = false;

function getWinner() {
    return getWinningLine([...cells].map((cell) => cell.textContent));
}

cells.forEach((cell) => {
    cell.addEventListener('click', () => {
        if (gameOver || cell.textContent !== '') {
            return;
        }

        cell.textContent = currentPlayer;
        cell.setAttribute('aria-label', `${currentPlayer} mark`);

        if (getWinner()) {
            status.textContent = `${currentPlayer} wins!`;
            gameOver = true;
            return;
        }

        if ([...cells].every((boardCell) => boardCell.textContent !== '')) {
            status.textContent = "It's a draw!";
            gameOver = true;
            return;
        }

        currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
        status.textContent = `${currentPlayer}'s turn`;
    });
});

newGameButton.addEventListener('click', () => {
    cells.forEach((cell, index) => {
        cell.textContent = '';
        cell.setAttribute('aria-label', cellLabels[index]);
    });

    currentPlayer = 'X';
    gameOver = false;
    status.textContent = "X's turn";
});

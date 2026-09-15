const cells = document.querySelectorAll('.cell');
const status = document.querySelector('.status');
let currentPlayer = 'X';
let gameOver = false;

const winningLines = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
];

function getWinner() {
    return winningLines.find(([first, second, third]) => {
        const mark = cells[first].textContent;
        return mark !== '' && mark === cells[second].textContent && mark === cells[third].textContent;
    });
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

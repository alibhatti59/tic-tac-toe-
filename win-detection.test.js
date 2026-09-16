const test = require('node:test');
const assert = require('node:assert/strict');
const { getWinningLine } = require('./win-detection.js');

test('detects a winning row', () => {
    assert.deepEqual(getWinningLine(['X', 'X', 'X', '', '', '', '', '', '']), [0, 1, 2]);
});

test('detects a winning column', () => {
    assert.deepEqual(getWinningLine(['O', '', '', 'O', '', '', 'O', '', '']), [0, 3, 6]);
});

test('detects a winning diagonal', () => {
    assert.deepEqual(getWinningLine(['', 'X', '', '', 'X', '', '', 'X', '']), [1, 4, 7]);
});

test('returns undefined when there is no winner', () => {
    assert.equal(getWinningLine(['X', 'O', 'X', 'X', 'O', 'O', 'O', 'X', 'X']), undefined);
});
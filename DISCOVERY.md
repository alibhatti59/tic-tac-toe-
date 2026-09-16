# Discovery

Review date: 2026-09-16

## Findings

### High: Played cells lose their board position in the accessible name

- Evidence: [script.js](script.js#L19-L21) replaces the initial location label with only `X mark` or `O mark`.
- Impact: A screen-reader user can no longer distinguish the nine cell buttons after they are played. The board remains visually understandable, but its interactive controls lose the row/column context supplied by [index.html](index.html#L16-L24).
- Recommendation: Preserve the original location in the label, for example `Top-left cell: X`, and add an accessibility-focused regression test.
- Linear: [ALI-14](https://linear.app/ali-hassnain-bhatti/issue/ALI-14/preserve-cell-position-in-played-cell-accessible-labels)

### Medium: Browser game behavior has no automated coverage

- Evidence: [win-detection.test.js](win-detection.test.js#L1-L20) covers four pure-function cases only. [script.js](script.js#L1-L43) contains the untested click, turn, occupied-cell, win, draw, status, reset, and ARIA behavior.
- Impact: Regressions in the user-facing game flow can pass CI because the current tests do not load a DOM or exercise any event handler.
- Recommendation: Add DOM-level tests for a normal turn sequence, occupied cells, win and draw termination, reset, status text, and accessible labels. A lightweight DOM test dependency or a small browser test harness would be appropriate.
- Linear: [ALI-15](https://linear.app/ali-hassnain-bhatti/issue/ALI-15/add-dom-coverage-for-the-tic-tac-toe-game-flow)

### Medium: `getWinningLine` has an implicit input contract

- Evidence: [win-detection.js](win-detection.js#L12-L18) indexes the supplied value without checking that it is a nine-cell board. Passing `undefined` or `null` throws, while short or non-string boards are silently accepted and extra cells are ignored.
- Impact: The helper is exported for CommonJS consumers, so callers outside the current UI can receive inconsistent behavior rather than a defined result or validation error. The current tests exercise only valid nine-cell arrays.
- Recommendation: Define and enforce the board contract, or document that the helper is internal. Add tests for invalid length and invalid values, including the chosen error behavior.
- Linear: [ALI-13](https://linear.app/ali-hassnain-bhatti/issue/ALI-13/define-and-validate-getwinningline-board-input)

## Dead-code scan

No confidently dead production code was found. `cellLabels`, `getWinner`, `getWinningLine`, and the reset handler all have active call sites. The winning-line indices are currently used only as a truthy result; that is an opportunity for future highlighting, not dead code by itself.

## Validation

- `node --test`: 4 passing tests.
- `node --check script.js`: passed.
- `node --check win-detection.js`: passed.
- `npm test` and the npm syntax scripts were blocked in this Windows session because PowerShell execution policy prevents loading `npm.ps1`; the underlying Node commands passed.
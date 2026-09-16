"""Read-only MCP introspection server for the Tic Tac Toe repository."""

from __future__ import annotations

import ast
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_SUFFIXES = {".css", ".html", ".js", ".py"}
IGNORED_DIRECTORIES = {".git", "node_modules", "__pycache__", ".pytest_cache"}

mcp = FastMCP("tic-tac-toe-introspection")


class FileRequest(BaseModel):
    """Validated repository-relative source file path."""

    file: str = Field(min_length=1, description="Repository-relative source file path")


class FunctionRequest(FileRequest):
    """Validated source file and function or variable name."""

    name: str = Field(min_length=1, description="Function, class, or variable name")


class EmptyRequest(BaseModel):
    """Empty input model used to make the tool input schema explicit."""

    pass


def _source_files() -> list[Path]:
    """Return supported source files while skipping generated and dependency trees."""
    return sorted(
        path
        for path in REPOSITORY_ROOT.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SOURCE_SUFFIXES
        and not any(part in IGNORED_DIRECTORIES for part in path.relative_to(REPOSITORY_ROOT).parts)
    )


def _resolve_source_file(relative_file: str) -> Path:
    """Resolve a repository-relative source path and reject traversal."""
    candidate = (REPOSITORY_ROOT / relative_file).resolve()
    try:
        candidate.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise ValueError("file must stay inside the repository") from error
    if not candidate.is_file() or candidate.suffix.lower() not in SOURCE_SUFFIXES:
        raise ValueError("file must be an existing .css, .html, .js, or .py source file")
    return candidate


def _relative_path(path: Path) -> str:
    """Format a path with forward slashes for MCP clients."""
    return path.relative_to(REPOSITORY_ROOT).as_posix()


def _description(path: Path) -> str:
    descriptions = {
        "index.html": "Game page markup and the nine board cell buttons.",
        "script.js": "Browser game flow, DOM-backed state, turns, reset, and status updates.",
        "styles.css": "Visual styling for the Tic Tac Toe board and controls.",
        "win-detection.js": "Pure winning-line detection helper shared by the browser and tests.",
        "win-detection.test.js": "Node test suite covering rows, columns, diagonals, and no-winner boards.",
        "mcp-server/server.py": "Read-only FastMCP tools for inspecting this repository and running its tests.",
    }
    relative = _relative_path(path)
    return descriptions.get(relative, f"Source file: {relative}")


def _matching_delimiter(source: str, opening_index: int) -> int:
    """Find the closing delimiter while ignoring strings and JavaScript comments."""
    pairs = {"{": "}", "[": "]", "(": ")"}
    opening = source[opening_index]
    stack = [opening]
    index = opening_index + 1
    quote: str | None = None
    escaped = False
    in_line_comment = False
    in_block_comment = False

    while index < len(source):
        character = source[index]
        next_character = source[index + 1] if index + 1 < len(source) else ""
        if in_line_comment:
            if character == "\n":
                in_line_comment = False
            index += 1
            continue
        if in_block_comment:
            if character == "*" and next_character == "/":
                in_block_comment = False
                index += 2
            else:
                index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            index += 1
            continue
        if character in {"'", '"', "`"}:
            quote = character
        elif character == "/" and next_character == "/":
            in_line_comment = True
            index += 2
            continue
        elif character == "/" and next_character == "*":
            in_block_comment = True
            index += 2
            continue
        elif character in pairs:
            stack.append(character)
        elif character in pairs.values():
            if not stack or pairs[stack[-1]] != character:
                raise ValueError("unbalanced JavaScript delimiters")
            stack.pop()
            if not stack:
                return index
        index += 1
    raise ValueError("unclosed JavaScript declaration")


def _extract_javascript_symbol(source: str, name: str) -> str | None:
    function_match = re.search(
        rf"(?:async\s+)?function\s+{re.escape(name)}\s*\([^)]*\)\s*\{{", source
    )
    if function_match:
        opening_index = source.find("{", function_match.start(), function_match.end())
        closing_index = _matching_delimiter(source, opening_index)
        return source[function_match.start() : closing_index + 1].strip()

    variable_match = re.search(
        rf"\b(?:const|let|var)\s+{re.escape(name)}\s*=", source
    )
    if not variable_match:
        return None

    start = variable_match.start()
    index = variable_match.end()
    stack: list[str] = []
    quote: str | None = None
    escaped = False
    while index < len(source):
        character = source[index]
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
        elif character in {"'", '"', "`"}:
            quote = character
        elif character in "[{(":
            stack.append(character)
        elif character in "]})":
            if stack:
                stack.pop()
        elif character == ";" and not stack:
            return source[start : index + 1].strip()
        index += 1
    return source[start:].strip()


def _extract_python_symbol(source: str, name: str) -> str | None:
    tree = ast.parse(source)
    candidates: list[ast.AST] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name:
            candidates.append(node)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id == name for target in targets):
                candidates.append(node)
    if not candidates:
        return None
    return ast.get_source_segment(source, candidates[0])


@mcp.tool(annotations={"readOnlyHint": True})
def list_files(request: EmptyRequest) -> str:
    """List every supported source file with a brief description."""
    del request
    files = [
        {"file": _relative_path(path), "description": _description(path)}
        for path in _source_files()
    ]
    return json.dumps(files, indent=2)


@mcp.tool(annotations={"readOnlyHint": True})
def read_function(request: FunctionRequest) -> str:
    """Return the source for a named function, class, or variable in one source file."""
    path = _resolve_source_file(request.file)
    source = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".py":
        result = _extract_python_symbol(source, request.name)
    elif path.suffix.lower() == ".js":
        result = _extract_javascript_symbol(source, request.name)
    else:
        result = None
    if result is None:
        raise ValueError(f"could not find {request.name!r} in {request.file!r}")
    return result


@mcp.tool(annotations={"readOnlyHint": True})
def describe_state(request: EmptyRequest) -> str:
    """Explain where the board, current player, and game-over state are managed."""
    del request
    return (
        "Game state is managed in script.js. The board is not a separate JavaScript array: "
        "the nine .cell buttons in index.html store each mark in their textContent, and "
        "getWinner() maps those values into getWinningLine() from win-detection.js. "
        "The current player is held in the module-level currentPlayer variable and switches "
        "between X and O after each valid move. The module-level gameOver boolean ends input "
        "after a win or draw. The click handler writes the winner/draw/next-turn message to "
        "the .status element, while the New Game handler clears every cell and resets both "
        "variables and the status to X's turn."
    )


@mcp.tool(annotations={"readOnlyHint": True})
def run_tests(request: EmptyRequest) -> str:
    """Run the repository's existing Node test suite and return its pass/fail output."""
    del request
    try:
        completed = subprocess.run(
            ["node", "--test"],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return f"Test run could not be completed: {error}"

    result = "PASS" if completed.returncode == 0 else "FAIL"
    output = "\n".join(part for part in (completed.stdout, completed.stderr) if part).strip()
    return f"{result} (exit code {completed.returncode})\n{output}"


if __name__ == "__main__":
    mcp.run()

# Tic Tac Toe introspection MCP server

This read-only FastMCP server exposes the Tic Tac Toe source for repository-aware clients. It provides `list_files`, `read_function`, `describe_state`, and `run_tests`.

## Run locally

From the `mcp-server` directory:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python server.py
```

The server uses stdio transport. Register `server.py` as the command for an MCP client, with the repository's `mcp-server` directory as its working directory. The tools only read source files or execute the existing `node --test` suite; they do not modify the repository.

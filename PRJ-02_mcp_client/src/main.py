"""Entrypoint do cliente MCP. Delega para client.run() (REPL ou one-shot).

    uv run python src/client.py            # REPL
    uv run python src/client.py "ping"     # one-shot
"""
import asyncio
from client import run

if __name__ == "__main__":
    asyncio.run(run())

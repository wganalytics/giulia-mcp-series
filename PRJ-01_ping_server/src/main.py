"""Entrypoint: sobe o servidor MCP ping_server (transporte stdio)."""
from ping_server import mcp

if __name__ == "__main__":
    mcp.run(transport="stdio")

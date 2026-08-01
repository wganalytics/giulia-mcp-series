"""Entrypoint: sobe o servidor MCP de Resources (transporte stdio)."""
from resources_server import mcp

if __name__ == "__main__":
    mcp.run(transport="stdio")

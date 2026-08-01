import socket
import time
from mcp.server.fastmcp import FastMCP

# Inicializa o servidor FastMCP com nome "ping_server"
mcp = FastMCP("ping_server")

@mcp.tool(name="ping")
def ping() -> str:
    """Health-check do próprio servidor MCP. Retorna 'pong' se estiver vivo."""
    return "pong"

@mcp.tool(name="echo")
def echo(mensagem: str) -> str:
    """Devolve exatamente a mensagem recebida (útil para testar o transporte)."""
    return mensagem

@mcp.tool(name="check_host")
def check_host(host: str, port: int = 443, timeout: float = 3.0) -> str:
    """Faz um health-check TCP REAL de um host:porta e mede a latência.

    Abre uma conexão TCP de verdade e retorna se a porta está acessível
    e o tempo de resposta em milissegundos.
    """
    inicio = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            latencia_ms = (time.perf_counter() - inicio) * 1000
            return f"UP {host}:{port} — {latencia_ms:.1f} ms"
    except OSError as e:
        return f"DOWN {host}:{port} — {e}"

if __name__ == "__main__":
    mcp.run(transport='stdio')

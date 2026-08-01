import os
import csv
from pathlib import Path
from urllib.parse import unquote

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()


def _param(valor: str) -> str:
    """Decodifica um parâmetro vindo da URI.

    O cliente MCP não pode mandar espaço cru numa URI — ``contato://Ana Silva`` é
    rejeitado como parâmetro inválido antes de chegar aqui. A forma correta é
    ``contato://Ana%20Silva``, e então o servidor recebe a string **percent-encoded**.

    Sem esta decodificação o template não encontrava **nenhum** contato: todo nome do
    CSV tem espaço. O defeito não aparecia nos testes porque eles chamavam a função
    diretamente, com o nome já legível, pulando a camada de URI.
    """
    return unquote(valor).strip()

# Caminhos robustos relativos à raiz do projeto (antes eram relativos ao CWD e quebravam).
BASE = Path(__file__).resolve().parent.parent
README_PATH = BASE / "README.md"
CONTATOS_PATH = BASE / "data" / "contatos.csv"

mcp = FastMCP("resources_server")

@mcp.resource(
    "echo://static",
    name="Identidade do agente",
    description="Retorna uma mensagem com o nome do servidor ou do agente.",
    mime_type="text/plain",
)
def echo_resource() -> str:
    return f"Meu nome é {os.getenv('AGENT_NAME', 'Giulia-ai')}"

@mcp.resource("file://readme")
def readme() -> bytes:
    """Retorna o conteúdo bruto do README.md do projeto."""
    return README_PATH.read_bytes()

@mcp.resource("file://contatos")
def contatos_csv() -> bytes:
    """Retorna o CSV de contatos (dados de demonstração)."""
    return CONTATOS_PATH.read_bytes()

@mcp.resource("contato://{nome}")
def contato(nome: str) -> str:
    """Resource template dinâmico: busca UM contato pelo nome dentro do CSV."""
    nome = _param(nome)
    with CONTATOS_PATH.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["nome"].lower() == nome.lower():
                return f"{row['nome']} — {row['email']} — {row['telefone']}"
    return f"Contato '{nome}' não encontrado."

@mcp.resource("greeting://{nome}")
def saudacao(nome: str) -> str:
    """Retorna uma saudação personalizada."""
    return f"Olá, {_param(nome)}! Bem-vindo ao MCP."

if __name__ == "__main__":
    mcp.run(transport="stdio")

"""Testes da conexão MCP — com sessão dublê, sem subir o servidor.

O caso que originou este módulo é `test_list_tools_nao_acumula`: `list_tools()`
acrescentava em `self.tools`, então duas chamadas na mesma sessão mandavam a lista de
tools duplicada para o modelo.
"""
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from giulia_ai_mcp_conn import MCPConnGiuliaAI  # noqa: E402


class SessaoFake:
    def __init__(self, tools):
        self._tools = tools

    async def list_tools(self):
        return SimpleNamespace(tools=self._tools)


def tool(nome, descricao="desc"):
    return SimpleNamespace(name=nome, description=descricao, inputSchema={"type": "object"})


@pytest.fixture
def conn():
    c = MCPConnGiuliaAI.__new__(MCPConnGiuliaAI)  # sem tocar o server_config.json
    c.session = SessaoFake([tool("ping"), tool("check_host")])
    return c


@pytest.mark.asyncio
async def test_list_tools_converte_o_formato(conn):
    tools = await conn.list_tools()
    assert tools == [
        {"name": "ping", "description": "desc", "input_schema": {"type": "object"}},
        {"name": "check_host", "description": "desc", "input_schema": {"type": "object"}},
    ]


@pytest.mark.asyncio
async def test_list_tools_nao_acumula(conn):
    """Duas chamadas devem devolver a mesma quantidade, não o dobro."""
    primeira = await conn.list_tools()
    segunda = await conn.list_tools()
    assert len(primeira) == len(segunda) == 2


@pytest.mark.asyncio
async def test_list_tools_devolve_lista_nova(conn):
    """Mutar o retorno não pode afetar a chamada seguinte."""
    primeira = await conn.list_tools()
    primeira.append("lixo")
    assert len(await conn.list_tools()) == 2


def test_conexao_nao_guarda_estado_de_tools(conn):
    assert not hasattr(conn, "tools"), "o cache mutável foi removido de propósito"

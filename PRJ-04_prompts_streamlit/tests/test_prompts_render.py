"""Renderiza TODOS os prompts pelo caminho real do fastmcp.

Motivo de existir: `generate_code_request` devolvia `PromptMessage` cru e o fastmcp
recusa (`Prompt must return str, list[Message], or PromptResult`). O prompt aparecia
normalmente em `list_prompts` e explodia em `get_prompt` — defeito invisível para
teste que só importa o módulo.

Estes testes usam o `Client` em memória: mesmo caminho de renderização do servidor,
sem subir processo nem exigir credencial.
"""
import sys
from pathlib import Path

import pytest
from fastmcp import Client

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from server import mcp  # noqa: E402

# nome -> argumentos válidos
PROMPTS = {
    "saudacao": {},
    "ask_about_topic": {"topic": "MCP"},
    "generate_code_request": {"language": "Python", "task_description": "somar dois números"},
    "debate_agentes": {"topic": "IA na educação", "agentes": "3", "debates": "2"},
}


@pytest.mark.asyncio
async def test_todos_os_prompts_estao_registrados():
    async with Client(mcp) as c:
        assert {p.name for p in await c.list_prompts()} == set(PROMPTS)


@pytest.mark.asyncio
@pytest.mark.parametrize("nome", list(PROMPTS))
async def test_prompt_renderiza_sem_erro(nome):
    """O que faltava: exercitar get_prompt, não só list_prompts."""
    async with Client(mcp) as c:
        r = await c.get_prompt(nome, PROMPTS[nome])
        assert r.messages, f"{nome} renderizou sem mensagem"
        assert r.messages[0].content.text.strip(), f"{nome} renderizou texto vazio"


@pytest.mark.asyncio
async def test_argumentos_chegam_no_texto_renderizado():
    async with Client(mcp) as c:
        r = await c.get_prompt("generate_code_request",
                               {"language": "Rust", "task_description": "ordenar uma lista"})
        texto = r.messages[0].content.text
        assert "Rust" in texto and "ordenar uma lista" in texto

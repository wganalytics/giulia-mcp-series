"""Testes do lado A2A — AgentCard e parsing da resposta, sem subir o servidor."""
import sys
from pathlib import Path

import httpx
import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))                      # pacote src.server (imports relativos)
sys.path.insert(0, str(RAIZ / "src" / "cliente"))  # cliente roda como script solto

from a2a_tool import (  # noqa: E402
    ClientA2A,
    RespostaA2AInvalida,
    extrair_texto,
)


# --------------------------------------------------------------------------
# AgentCard — o "list_tools" do A2A
# --------------------------------------------------------------------------

@pytest.fixture
def agente():
    from src.server.agent import Agent
    return Agent("http://localhost:9999")


def test_card_publica_a_url_recebida(agente):
    assert agente.public_card.url == "http://localhost:9999"


def test_card_declara_a_skill_de_redator(agente):
    skills = agente.public_card.skills
    assert len(skills) == 1
    assert skills[0].id == "redator"


def test_card_traz_exemplos_de_uso(agente):
    """Exemplos são o que permite a outro agente decidir se deve chamar este."""
    assert agente.public_card.skills[0].examples


def test_card_declara_modos_de_texto(agente):
    assert agente.public_card.default_input_modes == ["text"]
    assert agente.public_card.default_output_modes == ["text"]


def test_url_do_card_vem_do_executor(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")
    from src.server.agent_executor import Executor
    executor = Executor(url="0.0.0.0", port=8080)
    assert executor.agent.public_card.url == "http://0.0.0.0:8080"


# --------------------------------------------------------------------------
# Parsing da resposta
# --------------------------------------------------------------------------

def test_extrai_o_texto_da_resposta():
    resposta = {"result": {"parts": [{"kind": "text", "text": "conteúdo gerado"}]}}
    assert extrair_texto(resposta) == "conteúdo gerado"


def test_pega_a_primeira_parte_quando_ha_varias():
    resposta = {"result": {"parts": [{"text": "primeira"}, {"text": "segunda"}]}}
    assert extrair_texto(resposta) == "primeira"


@pytest.mark.parametrize("resposta", [
    {},
    {"result": {}},
    {"result": {"parts": []}},
    {"result": {"parts": [{"kind": "file"}]}},
    {"error": {"code": -32000, "message": "falhou"}},
    None,
])
def test_formato_inesperado_levanta_com_mensagem_util(resposta):
    """Antes isso caía num `except Exception` que virava texto genérico."""
    with pytest.raises(RespostaA2AInvalida, match="result.parts"):
        extrair_texto(resposta)


# --------------------------------------------------------------------------
# Ciclo de vida do cliente HTTP
# --------------------------------------------------------------------------

def test_nao_guarda_cliente_http_no_construtor():
    """O AsyncClient nascia no __init__ e cruzava event loops distintos."""
    cliente = ClientA2A(server_url="http://localhost:9999")
    assert not any("httpx" in str(type(v)) for v in vars(cliente).values())


def test_erro_de_rede_vira_texto_para_o_agente(monkeypatch):
    async def explode(self, query):
        raise httpx.ConnectError("conexão recusada")
    monkeypatch.setattr(ClientA2A, "_async_run", explode)

    resultado = ClientA2A(server_url="http://localhost:9999")._run("tema")
    assert resultado.startswith("Erro ao contatar o servidor A2A")
    assert "conexão recusada" in resultado


def test_resposta_invalida_vira_texto_para_o_agente(monkeypatch):
    async def formato_ruim(self, query):
        raise RespostaA2AInvalida("resposta sem 'result.parts[0].text'")
    monkeypatch.setattr(ClientA2A, "_async_run", formato_ruim)

    assert ClientA2A("http://x")._run("tema").startswith("Erro ao contatar")


def test_erro_inesperado_nao_e_engolido(monkeypatch):
    """Bug de programação tem que estourar, não virar string de resultado."""
    async def bug(self, query):
        raise TypeError("erro de programação")
    monkeypatch.setattr(ClientA2A, "_async_run", bug)

    with pytest.raises(TypeError):
        ClientA2A("http://x")._run("tema")


# --------------------------------------------------------------------------
# O RemoteAgent precisa herdar o provider configurado
#
# Achado rodando a Crew de verdade: só o agente redator recebia `llm`. O
# RemoteAgent ficava sem, o CrewAI aplicava o LLM padrão dele (OpenAI) e a Crew
# inteira morria com "OPENAI_API_KEY is required" mesmo com LLM_MODEL apontando
# para Gemini. Nenhum teste pegava porque nenhum construía o agente.
#
# Construir um Agent faz o CrewAI instanciar o cliente do provider, que valida a
# credencial. Por isso os testes injetam chaves fictícias: exercitam a escolha do
# provider sem tocar a rede.
# --------------------------------------------------------------------------

import remote_agent as ra  # noqa: E402

PROVIDERS = {
    "gemini/gemini-2.5-flash": "GEMINI_API_KEY",
    "anthropic/claude-3-5-sonnet-20240620": "ANTHROPIC_API_KEY",
    "openrouter/openai/gpt-4o-mini": "OPENROUTER_API_KEY",
    "gpt-4o-mini": "OPENAI_API_KEY",
}


@pytest.fixture
def credenciais_falsas(monkeypatch):
    for var in set(PROVIDERS.values()):
        monkeypatch.setenv(var, "chave-de-teste-nao-usada")


def _modelo(agente):
    """Nome do modelo. O CrewAI descarta o prefixo de provider (`gemini/...`)."""
    llm = agente.llm
    return str(getattr(llm, "model", llm))


@pytest.mark.parametrize("modelo", list(PROVIDERS))
def test_remote_agent_usa_o_provider_do_ambiente(monkeypatch, credenciais_falsas, modelo):
    monkeypatch.setenv("LLM_MODEL", modelo)
    agente = ra.RemoteAgent(server_url="http://localhost:9999")
    # basta o nome do modelo: o CrewAI já resolveu (e removeu) o prefixo do provider
    assert modelo.split("/")[-1] in _modelo(agente)


def test_llm_explicito_tem_precedencia_sobre_o_ambiente(monkeypatch, credenciais_falsas):
    monkeypatch.setenv("LLM_MODEL", "gemini/gemini-2.5-flash")
    agente = ra.RemoteAgent(server_url="http://localhost:9999", llm="gpt-4o-mini")
    assert "gpt-4o-mini" in _modelo(agente)


def test_a_tool_a2a_continua_registrada(monkeypatch, credenciais_falsas):
    """A correção do llm não pode ter mexido no que o agente sabe fazer."""
    monkeypatch.setenv("LLM_MODEL", "gemini/gemini-2.5-flash")
    agente = ra.RemoteAgent(server_url="http://localhost:9999")
    assert [t.name for t in agente.tools] == ["Ferramenta A2A"]

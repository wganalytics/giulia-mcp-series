"""Testes do histórico de conversa.

O caso que originou este módulo é `test_chat_nao_muta_o_historico_recebido`: o
`append` alterava a lista do chamador, então o `st.session_state` era modificado mesmo
quando a chamada ao modelo falhava depois.
"""
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import giulia_ai_llm  # noqa: E402
from giulia_ai_llm import MyLLM  # noqa: E402


@pytest.fixture
def llm(monkeypatch):
    def completion_fake(model, messages, **kwargs):
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="resposta"))]
        )
    monkeypatch.setattr(giulia_ai_llm.litellm, "completion", completion_fake)
    return MyLLM(model="modelo-de-teste")


def test_chat_devolve_o_historico_atualizado(llm):
    assert llm.chat("oi") == [
        {"role": "user", "content": "oi"},
        {"role": "assistant", "content": "resposta"},
    ]


def test_chat_nao_muta_o_historico_recebido(llm):
    historico = [{"role": "user", "content": "anterior"}]
    copia = list(historico)

    llm.chat("nova", historico)

    assert historico == copia, "a lista do chamador não pode ser alterada"


def test_chat_preserva_o_historico_anterior(llm):
    historico = [{"role": "user", "content": "anterior"}]
    novo = llm.chat("nova", historico)
    assert novo[0] == {"role": "user", "content": "anterior"}
    assert len(novo) == 3


def test_falha_no_modelo_nao_corrompe_o_historico(monkeypatch):
    """Se a chamada quebra, o histórico do chamador tem que ficar intacto."""
    def explode(**kwargs):
        raise RuntimeError("provider fora do ar")
    monkeypatch.setattr(giulia_ai_llm.litellm, "completion", explode)

    historico = [{"role": "user", "content": "anterior"}]
    with pytest.raises(RuntimeError):
        MyLLM(model="x").chat("nova", historico)

    assert historico == [{"role": "user", "content": "anterior"}]


def test_modelo_vem_do_ambiente(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "gemini/gemini-1.5-flash")
    assert MyLLM().model == "gemini/gemini-1.5-flash"


def test_modelo_explicito_tem_precedencia(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "do-ambiente")
    assert MyLLM(model="explicito").model == "explicito"

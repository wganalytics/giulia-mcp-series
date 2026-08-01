"""Testes dos resources MCP.

O caso que originou `test_caminhos_independem_do_diretorio_de_execucao`: os caminhos
eram relativos ao diretório de onde o servidor era iniciado. Rodando da pasta certa
funcionava; de qualquer outra, quebrava.
"""
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

import resources_server as rs  # noqa: E402
from resources_server import (  # noqa: E402
    contato,
    contatos_csv,
    echo_resource,
    readme,
    saudacao,
)


# --------------------------------------------------------------------------
# Resource estático
# --------------------------------------------------------------------------

def test_identidade_usa_agent_name(monkeypatch):
    monkeypatch.setenv("AGENT_NAME", "Giulia-Prod")
    assert echo_resource() == "Meu nome é Giulia-Prod"


def test_identidade_tem_default(monkeypatch):
    monkeypatch.delenv("AGENT_NAME", raising=False)
    assert echo_resource() == "Meu nome é Giulia-ai"


# --------------------------------------------------------------------------
# Resources de arquivo
# --------------------------------------------------------------------------

def test_readme_devolve_bytes_do_arquivo():
    conteudo = readme()
    assert isinstance(conteudo, bytes)
    assert conteudo == rs.README_PATH.read_bytes()


def test_contatos_devolve_o_csv():
    assert contatos_csv().decode("utf-8").startswith("nome,email,telefone")


def test_caminhos_independem_do_diretorio_de_execucao(monkeypatch, tmp_path):
    """Rodar de outra pasta não pode quebrar a resolução dos arquivos."""
    monkeypatch.chdir(tmp_path)
    assert readme()
    assert contatos_csv()


def test_caminhos_apontam_para_a_raiz_do_projeto():
    assert rs.README_PATH.name == "README.md"
    assert rs.CONTATOS_PATH.parent.name == "data"
    assert rs.README_PATH.is_file() and rs.CONTATOS_PATH.is_file()


# --------------------------------------------------------------------------
# Templates dinâmicos
# --------------------------------------------------------------------------

def test_contato_encontrado_traz_email_e_telefone():
    resultado = contato("Ana Silva")
    assert "ana.silva@email.com" in resultado
    assert "11999991111" in resultado


@pytest.mark.parametrize("busca", ["ana silva", "ANA SILVA", "Ana Silva"])
def test_busca_de_contato_ignora_maiusculas(busca):
    assert "ana.silva@email.com" in contato(busca)


def test_contato_inexistente_tem_mensagem_clara():
    assert contato("Fulano Inexistente") == "Contato 'Fulano Inexistente' não encontrado."


def test_contato_devolve_apenas_um_registro():
    """O ponto do template: buscar UM contato, não despejar o CSV inteiro."""
    resultado = contato("Ana Silva")
    assert "joao.pereira@email.com" not in resultado
    assert resultado.count("@") == 1


def test_saudacao_personalizada():
    assert saudacao("Wemerson") == "Olá, Wemerson! Bem-vindo ao MCP."


# --------------------------------------------------------------------------
# Registro no servidor
# --------------------------------------------------------------------------

def test_servidor_expoe_cinco_resources():
    assert rs.mcp.name == "resources_server"

"""Testes do catálogo de bancos — sem tocar o PostgreSQL."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from postgres_databases import DatabaseDesconhecido, PostgresDatabases  # noqa: E402


def test_nomes_padrao():
    assert PostgresDatabases.nomes() == ["ecommerce", "clinica"]


def test_nome_pode_ser_renomeado_por_ambiente(monkeypatch):
    monkeypatch.setenv("PG_ECOMMERCE_DB", "loja_prod")
    assert "loja_prod" in PostgresDatabases.nomes()


def test_ambiente_e_lido_a_cada_chamada(monkeypatch):
    """Antes era atributo de classe, resolvido no import — dependia da ordem."""
    monkeypatch.setenv("PG_CLINICA_DB", "primeiro")
    assert "primeiro" in PostgresDatabases.nomes()
    monkeypatch.setenv("PG_CLINICA_DB", "segundo")
    assert "segundo" in PostgresDatabases.nomes()


@pytest.mark.parametrize("nome,arquivo", [
    ("ecommerce", "schema_ecommerce.yaml"),
    ("clinica", "schema_clinica.yaml"),
])
def test_schema_path_aponta_para_arquivo_existente(nome, arquivo):
    caminho = PostgresDatabases.get_schema_path(nome)
    assert caminho.name == arquivo
    assert caminho.is_file(), "o YAML de schema precisa existir no repositório"


def test_schema_path_independe_do_diretorio_de_execucao(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert PostgresDatabases.get_schema_path("ecommerce").is_file()


def test_banco_desconhecido_levanta_com_lista_de_opcoes():
    with pytest.raises(DatabaseDesconhecido, match="ecommerce, clinica"):
        PostgresDatabases.get_schema_path("financeiro")


def test_uri_valida_o_nome_antes_de_montar():
    with pytest.raises(DatabaseDesconhecido):
        PostgresDatabases.get_database_uri("inexistente")


def test_uri_usa_credenciais_do_ambiente(monkeypatch):
    monkeypatch.setenv("PG_HOST", "db.interno")
    monkeypatch.setenv("PG_PORT", "6543")
    monkeypatch.setenv("PG_USER", "giulia_ro")
    monkeypatch.setenv("PG_PASSWORD", "s3nh4")
    uri = PostgresDatabases.get_database_uri("ecommerce")
    assert uri == "postgresql://giulia_ro:s3nh4@db.interno:6543/ecommerce"

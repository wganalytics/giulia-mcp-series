"""Catálogo dos bancos disponíveis para consulta.

Cada banco é um nome (configurável por ambiente) associado ao YAML que descreve seu
schema — é esse YAML que o Crew lê para gerar SQL sem inventar tabela ou coluna.

Os nomes são resolvidos **a cada chamada**, não no import: antes eram atributos de
classe avaliados no carregamento do módulo, então dependiam de o ``load_dotenv()`` de
outro módulo ter rodado antes. Ordem de import não deve alterar configuração.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SCHEMAS_DIR = Path(__file__).resolve().parent


class DatabaseDesconhecido(ValueError):
    """O nome informado não está no catálogo."""


class PostgresDatabases:
    # nome padrão -> (variável de ambiente que o renomeia, arquivo de schema)
    _CATALOGO = {
        "ecommerce": ("PG_ECOMMERCE_DB", "schema_ecommerce.yaml"),
        "clinica": ("PG_CLINICA_DB", "schema_clinica.yaml"),
    }

    @classmethod
    def nomes(cls) -> list[str]:
        """Nomes dos bancos disponíveis, já resolvidos pelo ambiente."""
        return [os.getenv(env, padrao) for padrao, (env, _) in cls._CATALOGO.items()]

    @classmethod
    def _schema_de(cls, database_name: str) -> str:
        for padrao, (env, schema) in cls._CATALOGO.items():
            if database_name == os.getenv(env, padrao):
                return schema
        raise DatabaseDesconhecido(
            f"banco '{database_name}' não encontrado — "
            f"disponíveis: {', '.join(cls.nomes())}"
        )

    @classmethod
    def get_schema_path(cls, database_name: str) -> Path:
        """Caminho do YAML de schema do banco, ancorado na pasta do módulo."""
        return SCHEMAS_DIR / cls._schema_de(database_name)

    @classmethod
    def get_database_uri(cls, database_name: str) -> str:
        """Monta a URI REAL de conexão Postgres a partir de variáveis de ambiente."""
        cls._schema_de(database_name)  # valida o nome antes de montar a URI
        host = os.getenv("PG_HOST", "localhost")
        port = os.getenv("PG_PORT", "5432")
        user = os.getenv("PG_USER", "postgres")
        password = os.getenv("PG_PASSWORD", "postgres")
        return f"postgresql://{user}:{password}@{host}:{port}/{database_name}"

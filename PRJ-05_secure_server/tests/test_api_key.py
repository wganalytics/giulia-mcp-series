"""Testes do ciclo de vida das API Keys.

Cada teste roda contra um SQLite temporário — nada toca o banco de desenvolvimento.
"""
import sqlite3
import sys
from pathlib import Path

import bcrypt
import pytest

SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

import database  # noqa: E402
from api_key_controller import APIKeyController, ChaveMalFormada, _partes  # noqa: E402
from generate_api_key import APIKeyGenerator  # noqa: E402


@pytest.fixture(autouse=True)
def banco_temporario(tmp_path, monkeypatch):
    """Aponta o banco padrão para um arquivo descartável."""
    monkeypatch.setattr(database, "DEFAULT_DB_PATH", tmp_path / "teste.db")
    yield tmp_path / "teste.db"


@pytest.fixture
def controller():
    with APIKeyController() as c:
        yield c


@pytest.fixture
def usuario(controller):
    return controller.create_user("Giulia", "giulia@ex.com", "senha-forte")


# --------------------------------------------------------------------------
# Formato da chave
# --------------------------------------------------------------------------

def test_chave_tem_o_formato_publico(controller, usuario):
    full_key, _ = controller.generate_api_key("dev", usuario)
    assert full_key.startswith(f"sk-{usuario}-")


def test_partes_separa_user_id_e_secret():
    assert _partes("sk-7-abc-def_ghi") == (7, "abc-def_ghi")


@pytest.mark.parametrize("invalida", [
    "", "sk-", "sk-1-", "abc", "sk-abc-segredo", "1-2-3", None,
])
def test_chave_mal_formada_e_rejeitada(invalida):
    with pytest.raises(ChaveMalFormada):
        _partes(invalida)


def test_segredo_com_hifen_nao_quebra_o_parse(controller, usuario):
    """token_urlsafe gera '-' — o split precisa parar na terceira parte."""
    full_key, _ = controller.generate_api_key("dev", usuario)
    user_id, secret = _partes(full_key)
    assert user_id == usuario and full_key.endswith(secret)


# --------------------------------------------------------------------------
# Persistência: o segredo nunca vai em texto puro
# --------------------------------------------------------------------------

def test_segredo_nao_e_persistido(controller, usuario, banco_temporario):
    full_key, _ = controller.generate_api_key("dev", usuario)
    _, secret = _partes(full_key)

    conteudo = Path(banco_temporario).read_bytes()
    assert secret.encode() not in conteudo


def test_banco_guarda_hash_bcrypt(controller, usuario, banco_temporario):
    full_key, _ = controller.generate_api_key("dev", usuario)
    _, secret = _partes(full_key)

    conn = sqlite3.connect(banco_temporario)
    conn.row_factory = sqlite3.Row
    linha = conn.execute("SELECT * FROM api_keys").fetchone()
    conn.close()

    assert linha["hashed_key"].startswith("$2b$")
    assert bcrypt.checkpw(secret.encode(), linha["hashed_key"].encode())


def test_senha_do_usuario_e_hasheada(controller, usuario):
    assert controller.user_repository.verify_password("giulia@ex.com", "senha-forte")
    assert not controller.user_repository.verify_password("giulia@ex.com", "errada")


# --------------------------------------------------------------------------
# Mascaramento
# --------------------------------------------------------------------------

def test_mascara_preserva_prefixo_e_final(controller, usuario):
    full_key, masked = controller.generate_api_key("dev", usuario)
    assert masked.startswith(f"sk-{usuario}-")
    assert masked.endswith(full_key[-4:])


def test_mascara_esconde_o_miolo_do_segredo(controller, usuario):
    full_key, masked = controller.generate_api_key("dev", usuario)
    _, secret = _partes(full_key)
    assert secret[:-4] not in masked


def test_mascara_de_chave_invalida_nao_vaza_nada():
    assert set(APIKeyController._mask_key("qualquer-coisa")) == {"*"}


# --------------------------------------------------------------------------
# Validação
# --------------------------------------------------------------------------

def test_chave_valida_passa(controller, usuario):
    full_key, _ = controller.generate_api_key("dev", usuario)
    assert controller.validate_api_key(full_key) is True


@pytest.mark.parametrize("errada", [
    "sk-1-segredo-errado", "sk-999-qualquer", "lixo", "", None,
])
def test_chave_invalida_falha(controller, usuario, errada):
    controller.generate_api_key("dev", usuario)
    assert controller.validate_api_key(errada) is False


def test_chave_de_outro_usuario_nao_valida(controller, usuario):
    outro = controller.create_user("Outro", "outro@ex.com", "x")
    full_key, _ = controller.generate_api_key("dev", usuario)
    _, secret = _partes(full_key)
    assert controller.validate_api_key(f"sk-{outro}-{secret}") is False


def test_dados_do_usuario_vem_da_chave(controller, usuario):
    full_key, _ = controller.generate_api_key("dev", usuario)
    assert controller.get_user_data_by_api_key(full_key)["email"] == "giulia@ex.com"


def test_dados_nao_vazam_com_chave_invalida(controller, usuario):
    controller.generate_api_key("dev", usuario)
    assert controller.get_user_data_by_api_key("sk-1-errada") is None


# --------------------------------------------------------------------------
# O custo do bcrypt: uma verificação, não N
# --------------------------------------------------------------------------

def test_validacao_roda_bcrypt_uma_vez_so(controller, usuario, monkeypatch):
    """Antes, o bcrypt rodava contra todas as chaves do usuário até casar."""
    for i in range(5):
        full_key, _ = controller.generate_api_key(f"chave-{i}", usuario)

    chamadas = []
    original = bcrypt.checkpw
    monkeypatch.setattr(
        "api_key_controller.bcrypt.checkpw",
        lambda *a, **k: (chamadas.append(1), original(*a, **k))[1],
    )

    assert controller.validate_api_key(full_key) is True
    assert len(chamadas) == 1


def test_lookup_hash_e_deterministico():
    assert APIKeyGenerator.lookup_hash("abc") == APIKeyGenerator.lookup_hash("abc")
    assert APIKeyGenerator.lookup_hash("abc") != APIKeyGenerator.lookup_hash("abd")


def test_generate_key_pair_devolve_os_tres_derivados():
    secret, hashed, lookup = APIKeyGenerator.generate_key_pair()
    assert bcrypt.checkpw(secret.encode(), hashed.encode())
    assert lookup == APIKeyGenerator.lookup_hash(secret)


# --------------------------------------------------------------------------
# Compatibilidade com bancos antigos (sem a coluna lookup_hash)
# --------------------------------------------------------------------------

def test_chave_legada_continua_valida(controller, usuario, banco_temporario):
    full_key, _ = controller.generate_api_key("legada", usuario)

    # Simula um banco criado antes da coluna existir.
    conn = sqlite3.connect(banco_temporario)
    conn.execute("UPDATE api_keys SET lookup_hash = NULL")
    conn.commit()
    conn.close()

    assert controller.validate_api_key(full_key) is True


def test_chave_legada_ganha_lookup_no_primeiro_uso(controller, usuario, banco_temporario):
    full_key, _ = controller.generate_api_key("legada", usuario)
    conn = sqlite3.connect(banco_temporario)
    conn.execute("UPDATE api_keys SET lookup_hash = NULL")
    conn.commit()
    conn.close()

    controller.validate_api_key(full_key)

    conn = sqlite3.connect(banco_temporario)
    lookup = conn.execute("SELECT lookup_hash FROM api_keys").fetchone()[0]
    conn.close()
    assert lookup == APIKeyGenerator.lookup_hash(_partes(full_key)[1])


def test_migracao_adiciona_coluna_em_banco_antigo(tmp_path, monkeypatch):
    caminho = tmp_path / "antigo.db"
    conn = sqlite3.connect(caminho)
    conn.execute("""CREATE TABLE api_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
        name TEXT NOT NULL, hashed_key TEXT NOT NULL, masked_key TEXT NOT NULL)""")
    conn.commit()
    conn.close()

    monkeypatch.setattr(database, "DEFAULT_DB_PATH", caminho)
    database.Database()

    conn = sqlite3.connect(caminho)
    colunas = {c[1] for c in conn.execute("PRAGMA table_info(api_keys)")}
    conn.close()
    assert "lookup_hash" in colunas


# --------------------------------------------------------------------------
# Ciclo de vida
# --------------------------------------------------------------------------

def test_context_manager_fecha_sem_erro():
    with APIKeyController() as c:
        assert c.list_users() == []


def test_revogacao_invalida_a_chave(controller, usuario, banco_temporario):
    full_key, _ = controller.generate_api_key("dev", usuario)
    conn = sqlite3.connect(banco_temporario)
    key_id = conn.execute("SELECT id FROM api_keys").fetchone()[0]
    conn.close()

    assert controller.delete_api_key(key_id, usuario) is True
    assert controller.validate_api_key(full_key) is False

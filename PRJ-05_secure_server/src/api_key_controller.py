"""Orquestra geração, validação e revogação de API Keys.

Formato público da chave: ``sk-{user_id}-{secret}``. Só o ``user_id`` é legível; o
segredo nunca é persistido em texto puro.
"""
from typing import Dict, List, Optional, Tuple

import bcrypt

from generate_api_key import APIKeyGenerator
from repository import APIKeyRepository, UserRepository


class ChaveMalFormada(ValueError):
    """A string não tem o formato ``sk-{user_id}-{secret}``."""


def _partes(api_key: str) -> Tuple[int, str]:
    """Separa a chave em ``(user_id, secret)``.

    O segredo pode conter '-' (``token_urlsafe``), por isso o split é limitado a 3
    partes — só o prefixo e o user_id são consumidos.
    """
    partes = (api_key or "").split("-", 2)
    if len(partes) != 3 or partes[0] != "sk" or not partes[2]:
        raise ChaveMalFormada("formato esperado: sk-{user_id}-{secret}")
    try:
        return int(partes[1]), partes[2]
    except ValueError:
        raise ChaveMalFormada("user_id não é um inteiro") from None


class APIKeyController:
    def __init__(self):
        self.user_repository = UserRepository()
        self.api_key_repository = APIKeyRepository()

    @staticmethod
    def _mask_key(key: str) -> str:
        """Mascara o segredo, preservando o prefixo legível e os 4 últimos caracteres.

        O prefixo ``sk-{user_id}-`` é público por construção, então mascará-lo não
        protegia nada — antes o corte era cego nos 3 primeiros caracteres, que são
        sempre ``sk-``.
        """
        try:
            user_id, secret = _partes(key)
        except ChaveMalFormada:
            return "*" * len(key)
        visivel = secret[-4:] if len(secret) > 8 else ""
        return f"sk-{user_id}-{'*' * 8}{visivel}"

    # ---- Geração -----------------------------------------------------------
    def generate_api_key(self, name: str, user_id: int, length: int = 32):
        """Gera uma chave para o usuário. A chave completa só existe neste retorno."""
        secret, hashed_key, lookup = APIKeyGenerator.generate_key_pair(length)
        full_key = f"sk-{user_id}-{secret}"
        masked_key = self._mask_key(full_key)
        self.api_key_repository.create_api_key(
            user_id, name, hashed_key, masked_key, lookup
        )
        return full_key, masked_key

    # ---- Validação ---------------------------------------------------------
    def validate_api_key(self, api_key: str) -> bool:
        """Confere a chave: uma busca por índice + UMA verificação bcrypt.

        Antes, o bcrypt rodava contra todas as chaves do usuário até casar — custo
        O(n) numa função que é lenta de propósito.
        """
        try:
            user_id, secret = _partes(api_key)
        except ChaveMalFormada:
            return False

        lookup = APIKeyGenerator.lookup_hash(secret)

        registro = self.api_key_repository.get_by_lookup(user_id, lookup)
        if registro:
            return bcrypt.checkpw(secret.encode(), registro["hashed_key"].encode())

        # Compatibilidade: chaves criadas antes da coluna lookup_hash existir.
        for legada in self.api_key_repository.get_legacy_keys(user_id):
            if bcrypt.checkpw(secret.encode(), legada["hashed_key"].encode()):
                self.api_key_repository.set_lookup_hash(legada["id"], lookup)
                return True
        return False

    def get_user_data_by_api_key(self, api_key: str) -> Optional[Dict]:
        """Dados do usuário dono da chave, ou ``None`` se a chave não for válida."""
        if not self.validate_api_key(api_key):
            return None
        user_id, _ = _partes(api_key)
        return self.api_key_repository.get_user_by_id(user_id)

    # ---- Administração -----------------------------------------------------
    def create_user(self, name: str, email: str, password: str) -> int:
        """Cria um usuário (senha hasheada com bcrypt) e devolve o id."""
        return self.user_repository.create_user(name, email, password)

    def delete_api_key(self, key_id: int, user_id: int) -> bool:
        """Exclui uma chave se ela pertencer ao usuário."""
        return self.api_key_repository.delete_api_key(key_id, user_id)

    def list_users(self) -> List[Dict]:
        """Lista todos os usuários com nome e email."""
        return self.user_repository.list_users()

    # ---- Ciclo de vida -----------------------------------------------------
    # Antes havia um __del__ chamando close(). Destrutor não é ponto confiável de
    # liberação de recurso: roda em hora indeterminada e uma exceção ali é engolida
    # pelo interpretador. Fechamento agora é explícito.
    def close(self) -> None:
        """Fecha as conexões dos repositórios."""
        self.user_repository.close()
        self.api_key_repository.close()

    def __enter__(self) -> "APIKeyController":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

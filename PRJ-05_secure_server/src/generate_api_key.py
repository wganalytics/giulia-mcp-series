import hashlib
import secrets

import bcrypt


class APIKeyGenerator:
    """Geração e derivação de chaves de API.

    Cada chave tem **dois** derivados persistidos:

    - ``hash`` (bcrypt + salt) — o verificador. Lento de propósito.
    - ``lookup`` (SHA-256) — apenas um índice, para localizar a linha certa sem rodar
      bcrypt contra todas as chaves do usuário.

    SHA-256 puro seria fraco para senha (baixa entropia, sujeita a dicionário), mas o
    segredo aqui tem 32 bytes vindos de ``secrets.token_urlsafe`` — não há o que
    adivinhar. É o mesmo desenho usado por provedores de API em produção: índice rápido
    para achar, verificador lento para confirmar.
    """

    def __init__(self, length=32):
        self.length = length

    @staticmethod
    def lookup_hash(secret: str) -> str:
        """Derivação rápida e determinística, usada só para localizar a chave."""
        return hashlib.sha256(secret.encode()).hexdigest()

    @staticmethod
    def generate_key_pair(length: int = 32) -> tuple[str, str, str]:
        """Gera o segredo e seus dois derivados.

        Args:
            length: Tamanho do segredo em bytes (padrão: 32)

        Returns:
            tuple[str, str, str]: ``(secret, hash_bcrypt, lookup_sha256)``
        """
        secret = secrets.token_urlsafe(length)
        hashed = bcrypt.hashpw(secret.encode(), bcrypt.gensalt()).decode()
        return secret, hashed, APIKeyGenerator.lookup_hash(secret)

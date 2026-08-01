from typing import Optional, List, Dict
import bcrypt
from database import Database

class UserRepository:
    def __init__(self):
        self.db = Database()

    def create_user(self, name: str, email: str, password: str) -> int:
        """Cria um novo usuário (com senha hasheada via bcrypt) e retorna seu ID"""
        if not password:
            raise ValueError("password é obrigatório")
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        with self.db as db:
            cursor = db.conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash)
            )
            db.conn.commit()
            return cursor.lastrowid

    def verify_password(self, email: str, password: str) -> bool:
        """Confere a senha do usuário contra o hash bcrypt armazenado"""
        with self.db as db:
            cursor = db.conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
        if not row or not row["password_hash"]:
            return False
        return bcrypt.checkpw(password.encode(), row["password_hash"].encode())

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Busca um usuário pelo ID"""
        with self.db as db:
            cursor = db.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_users(self) -> List[Dict]:
        """Lista todos os usuários com nome e email"""
        with self.db as db:
            cursor = db.conn.cursor()
            cursor.execute("SELECT name, email FROM users")
            return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """Fecha a conexão com o banco"""
        self.db.close()


class APIKeyRepository:
    def __init__(self):
        self.db = Database()

    def create_api_key(
        self, user_id: int, name: str, hashed_key: str, masked_key: str, lookup_hash: str
    ) -> int:
        """Cria uma nova API key e retorna seu ID"""
        with self.db as db:
            cursor = db.conn.cursor()
            cursor.execute(
                "INSERT INTO api_keys (user_id, name, hashed_key, masked_key, lookup_hash) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_id, name, hashed_key, masked_key, lookup_hash)
            )
            db.conn.commit()
            return cursor.lastrowid

    def get_by_lookup(self, user_id: int, lookup_hash: str) -> Optional[Dict]:
        """Localiza UMA chave pelo índice — evita rodar bcrypt contra todas."""
        with self.db as db:
            cursor = db.conn.cursor()
            cursor.execute(
                "SELECT * FROM api_keys WHERE user_id = ? AND lookup_hash = ?",
                (user_id, lookup_hash)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_legacy_keys(self, user_id: int) -> List[Dict]:
        """Chaves criadas antes da coluna lookup_hash existir (compatibilidade)."""
        with self.db as db:
            cursor = db.conn.cursor()
            cursor.execute(
                "SELECT * FROM api_keys WHERE user_id = ? AND lookup_hash IS NULL",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def set_lookup_hash(self, key_id: int, lookup_hash: str) -> None:
        """Preenche o índice de uma chave legada, no primeiro uso bem-sucedido."""
        with self.db as db:
            cursor = db.conn.cursor()
            cursor.execute(
                "UPDATE api_keys SET lookup_hash = ? WHERE id = ?", (lookup_hash, key_id)
            )
            db.conn.commit()

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Busca os dados do usuário dono de uma chave"""
        with self.db as db:
            cursor = db.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def delete_api_key(self, key_id: int, user_id: int) -> bool:
        """Exclui uma chave API se ela pertencer ao usuário"""
        with self.db as db:
            cursor = db.conn.cursor()
            cursor.execute(
                "DELETE FROM api_keys WHERE id = ? AND user_id = ?",
                (key_id, user_id)
            )
            db.conn.commit()
            return cursor.rowcount > 0

    def close(self):
        """Fecha a conexão com o banco"""
        self.db.close()

import sqlite3
from pathlib import Path
from typing import Optional

# Banco fica em <raiz do projeto>/data/database.db, independente do diretório
# de execução (antes era "database.db" relativo ao CWD, que gravava em qualquer lugar).
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "database.db"

class Database:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path or DEFAULT_DB_PATH)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        self._create_tables()

    def connect(self):
        """Estabelece conexão com o banco de dados"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome

    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def _create_tables(self):
        """Cria as tabelas necessárias se não existirem"""
        self.connect()
        try:
            cursor = self.conn.cursor()
            # Tabela de usuários
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Tabela de API keys.
            # lookup_hash: SHA-256 do segredo, só para localizar a linha (ver
            # APIKeyGenerator). O verificador continua sendo o bcrypt em hashed_key.
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    hashed_key TEXT NOT NULL,
                    masked_key TEXT NOT NULL,
                    lookup_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            self._migrar_lookup_hash(cursor)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_api_keys_lookup ON api_keys (lookup_hash)"
            )
            self.conn.commit()
        finally:
            self.close()

    @staticmethod
    def _migrar_lookup_hash(cursor):
        """Adiciona lookup_hash em bancos criados antes da coluna existir.

        Chaves antigas ficam com lookup_hash NULL e continuam válidas — a validação cai
        no caminho de compatibilidade (ver APIKeyController.validate_api_key), que
        regrava o lookup no primeiro uso.
        """
        colunas = {linha["name"] for linha in cursor.execute("PRAGMA table_info(api_keys)")}
        if "lookup_hash" not in colunas:
            cursor.execute("ALTER TABLE api_keys ADD COLUMN lookup_hash TEXT")

    def __enter__(self):
        """Suporte para uso com 'with'"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Suporte para uso com 'with'"""
        self.close()

"""PRJ-08 tem DOIS entrypoints (rode em terminais separados):

  1) Servidor A2A (agente Redator):
     uv run python -m src.server         # usa src/server/__main__.py

  2) Cliente A2A (Crew que consome o servidor e gera um tweet):
     uv run python src/cliente/main.py "IA na educação"

Configuração em .env (ver .env.example): LLM_MODEL + chave do provider,
e A2A_HOST / A2A_PORT / A2A_SERVER_URL.
"""

if __name__ == "__main__":
    print(__doc__)

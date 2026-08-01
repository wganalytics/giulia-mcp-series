"""CLI de gerenciamento do servidor MCP seguro.

Permite semear o banco (criar usuário + gerar API key) sem depender do stub antigo.
Exemplos:
    uv run python src/main.py create-user --name "Giulia" --email giulia@ex.com --password segredo
    uv run python src/main.py gen-key --user-id 1 --name "chave-dev"
    uv run python src/main.py list-users
"""
import argparse
from api_key_controller import APIKeyController


def main():
    parser = argparse.ArgumentParser(description="Gerenciador do servidor MCP seguro")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_user = sub.add_parser("create-user", help="Cria um usuário")
    p_user.add_argument("--name", required=True)
    p_user.add_argument("--email", required=True)
    p_user.add_argument("--password", required=True)

    p_key = sub.add_parser("gen-key", help="Gera uma API key para um usuário")
    p_key.add_argument("--user-id", type=int, required=True)
    p_key.add_argument("--name", default="default", help="Rótulo da chave")

    sub.add_parser("list-users", help="Lista usuários cadastrados")

    args = parser.parse_args()

    with APIKeyController() as controller:
        if args.cmd == "create-user":
            user_id = controller.create_user(args.name, args.email, args.password)
            print(f"✅ Usuário criado: id={user_id}  ({args.name} <{args.email}>)")
            print(f"   Próximo passo: uv run python src/main.py gen-key --user-id {user_id}")

        elif args.cmd == "gen-key":
            full_key, masked = controller.generate_api_key(args.name, args.user_id)
            print("✅ API key gerada — GUARDE AGORA, não será exibida novamente:")
            print(f"   {full_key}")
            print(f"   (mascarada no banco: {masked})")
            print("   Configure em .env como GIULIA_AI_API_KEY=<a chave acima>")

        elif args.cmd == "list-users":
            users = controller.list_users()
            if not users:
                print("(nenhum usuário cadastrado)")
            for u in users:
                print(f"- {u['name']} <{u['email']}>")


if __name__ == "__main__":
    main()

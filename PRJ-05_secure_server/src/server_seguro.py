import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from api_key_controller import APIKeyController

load_dotenv()

controller = APIKeyController()
mcp = FastMCP("server_seguro")

class APIKeyInvalida(Exception):
    """A chave configurada no ambiente é ausente ou não confere."""


def _usuario_autenticado() -> dict:
    """Devolve o usuário da chave em ``GIULIA_AI_API_KEY`` ou levanta.

    A chave vem do ambiente do próprio servidor — em stdio o servidor MCP é um
    processo filho do cliente, então não há outro chamador a distinguir. Isto é um
    gate de configuração, não autenticação multi-tenant; para isso seria preciso
    transporte HTTP com a chave viajando na requisição.
    """
    api_key = os.getenv("GIULIA_AI_API_KEY")
    user = controller.get_user_data_by_api_key(api_key) if api_key else None
    if not user:
        raise APIKeyInvalida("API Key inválida")
    return user

@mcp.tool("tool_segura")
def tool_segura() -> str:
    """
    Valida a API Key e retorna uma saudação com os dados do usuário autenticado.
    """
    user = _usuario_autenticado()
    return f"Olá, {user['name']} ({user['email']})! Sua API Key foi validada com sucesso."

@mcp.tool("listar_usuarios")
def listar_usuarios() -> str:
    """
    Lista todos os usuários cadastrados no sistema.
    Retorna nome e email de cada usuário.
    """
    _usuario_autenticado()

    users = controller.list_users()
    if not users:
        return "Nenhum usuário cadastrado."
    
    result = "Lista de usuários:\n"
    for user in users:
        result += f"Nome: {user['name']}, Email: {user['email']}\n"
    
    return result

if __name__ == "__main__":
    mcp.run(transport="stdio")

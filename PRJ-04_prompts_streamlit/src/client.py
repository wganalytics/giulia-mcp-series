from giulia_ai_mcp_conn import MCPConnGiuliaAI
from giulia_ai_llm import MyLLM


class SimpleMCPClient:
    """Cliente de chat sobre prompts MCP.

    Cada interação do Streamlit roda no seu próprio ``asyncio.run()``, então a sessão
    MCP é aberta e fechada dentro da mesma chamada. Antes, ``query_with_prompt`` fazia
    ``connect()`` e nunca desconectava — o subprocesso do servidor ficava órfão a cada
    rerun.
    """

    def __init__(self):
        self.llm = MyLLM()

    async def query_with_prompt(self, query: str):
        """Escolhe o prompt MCP mais adequado à pergunta e inicia a conversa."""
        async with MCPConnGiuliaAI() as conn:
            prompts = await conn.list_prompts()

            escolhido = self.llm.select_prompt(query, prompts)
            nome = escolhido["prompt"]
            args = escolhido.get("args", {})

            prompt_result = await conn.session.get_prompt(nome, args)
            texto = prompt_result.messages[0].content.text

        return self.llm.chat(texto)

    async def continue_chat(self, user_prompt: str, context_chat: list):
        """Continua a conversa já iniciada (não precisa do servidor MCP)."""
        return self.llm.chat(user_prompt, context_chat)

import sys
import asyncio
from giulia_ai_mcp_conn import MCPConnGiuliaAI
from giulia_ai_llm import MyLLM


class SimpleMPCClient:
    def __init__(self):
        self.conn = MCPConnGiuliaAI()
        self.llm = MyLLM()

    async def query(self, query: str, tools) -> str:
        tool = self.llm.select_tool(query, tools)
        if tool:
            result = await self.conn.session.call_tool(tool.tool_name, tool.tool_args)
            saida = result.content[0].text if result.content else "(sem conteúdo)"
            return f"[tool {tool.tool_name}({tool.tool_args})] -> {saida}"
        # Nenhuma tool casou: responde direto com o LLM.
        return self.llm.chat(query)


async def run():
    client = SimpleMPCClient()
    async with client.conn:
        tools = await client.conn.list_tools()
        args = " ".join(sys.argv[1:]).strip()
        if args:  # modo one-shot (útil para testes/scripts)
            print(await client.query(args, tools))
            return

        for tool in tools:
            print(f" - {tool['name']}: {tool['description']}")
        print("Cliente MCP pronto. Digite sua pergunta (ou 'sair'):")
        while True:
            try:
                q = input("> ").strip()
            except EOFError:
                break
            if q.lower() in ("sair", "exit", "quit", ""):
                break
            print(await client.query(q, tools))


if __name__ == "__main__":
    asyncio.run(run())

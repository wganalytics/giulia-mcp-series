import json
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from giulia_ai_prompts import GiuliaAIPrompts

BASE = Path(__file__).resolve().parent.parent

class MCPConnGiuliaAI:
    def __init__(self, config_path=None, server_name="prompt_server"):
        config_path = config_path or (BASE / "server_config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        server_config = config["mcpServers"][server_name]
        self.server_command = server_config["command"]
        self.server_args = server_config["args"]
        self.server_params = StdioServerParameters(
            command=self.server_command,
            args=self.server_args,
        )
        self.session = None

    async def connect(self):
        self.stdio_client = stdio_client(self.server_params)
        self.read_stream, self.write_stream = await self.stdio_client.__aenter__()
        self.session = ClientSession(self.read_stream, self.write_stream)
        await self.session.__aenter__()
        await self.session.initialize()
        return self

    async def desconnect(self, exc_type=None, exc=None, tb=None):
        await self.session.__aexit__(exc_type, exc, tb)
        await self.stdio_client.__aexit__(exc_type, exc, tb)

    async def __aenter__(self):
        return await self.connect()

    async def __aexit__(self, exc_type, exc, tb):
        await self.desconnect(exc_type, exc, tb)

    async def list_prompts(self):
        """Lista os prompts do servidor MCP."""
        prompts_result = await self.session.list_prompts()
        return [
            GiuliaAIPrompts(
                name=prompt.name,
                description=prompt.description,
                tool_args=[arg.name for arg in prompt.arguments] if prompt.arguments else [],
            )
            for prompt in prompts_result.prompts
        ]

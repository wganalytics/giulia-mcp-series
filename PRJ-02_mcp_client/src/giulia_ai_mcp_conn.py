import json
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BASE = Path(__file__).resolve().parent.parent

class MCPConnGiuliaAI:
    def __init__(self, config_path=None, server_name="ping_server"):
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

    async def list_tools(self):
        """Lista as tools do servidor no formato consumido pelo LLM.

        Devolve sempre uma lista nova — antes acumulava em ``self.tools``, então duas
        chamadas na mesma sessão duplicavam as tools enviadas ao modelo.
        """
        tools_result = await self.session.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in tools_result.tools
        ]

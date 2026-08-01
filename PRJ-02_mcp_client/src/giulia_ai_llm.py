import os
import json
import litellm
from dotenv import load_dotenv

load_dotenv()


class GiuliaAITool:
    def __init__(self, tool_name, tool_args, tool_use_id):
        self.tool_name = tool_name
        self.tool_args = tool_args
        self.tool_use_id = tool_use_id

    def __repr__(self):
        return f"GiuliaAITool(tool_name={self.tool_name}, tool_args={self.tool_args})"


def _to_openai_tools(mcp_tools):
    """Converte tools do MCP (name/description/input_schema) para o formato
    de function-calling (usado por LiteLLM em todos os providers)."""
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t.get("input_schema", {"type": "object", "properties": {}}),
            },
        }
        for t in mcp_tools
    ]


class MyLLM:
    """Abstração multi-provider via LiteLLM.

    O modelo vem de LLM_MODEL (.env). A chave é a do provider correspondente:
      gpt-4o-mini -> OPENAI_API_KEY
      anthropic/claude-3-5-sonnet-20240620 -> ANTHROPIC_API_KEY
      gemini/gemini-1.5-flash -> GEMINI_API_KEY
      openrouter/openai/gpt-4o-mini -> OPENROUTER_API_KEY
    """
    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")

    def chat(self, query) -> str:
        """Resposta direta do modelo, sem tools (usado quando nenhuma tool casa)."""
        response = litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content": query}],
            max_tokens=1000,
        )
        return response.choices[0].message.content or ""

    def select_tool(self, query, tools):
        response = litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content": query}],
            tools=_to_openai_tools(tools),
            tool_choice="auto",
            max_tokens=1000,
        )
        message = response.choices[0].message
        tool_calls = getattr(message, "tool_calls", None)
        if not tool_calls:
            return None
        call = tool_calls[0]
        args = json.loads(call.function.arguments or "{}")
        return GiuliaAITool(call.function.name, args, call.id)

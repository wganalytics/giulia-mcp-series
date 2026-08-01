"""Agente CrewAI que empacota um agente remoto A2A como se fosse uma tool local."""
import os

from crewai import Agent
from crewai.tools import BaseTool
from pydantic import Field

from a2a_tool import ClientA2A


class ClientA2ACrewAI(BaseTool):
    name: str = "Ferramenta A2A"
    description: str = (
        "Use esta ferramenta para obter conteúdo do servidor A2A. "
        "Forneça um tema ou tópico como input."
    )
    client_a2a: ClientA2A = Field(exclude=True)

    def _run(self, tema: str) -> str:
        """Busca conteúdo sobre um tema no agente remoto.

        O input desta ferramenta é o 'tema' sobre o qual se quer o conteúdo.
        """
        return self.client_a2a._run(tema)


class RemoteAgent(Agent):
    """Agente local cuja única capacidade é delegar para o agente remoto.

    O cliente A2A mora **na tool**, não no agente: `Agent` do CrewAI é um modelo
    pydantic e não aceita atributo arbitrário. Atribuir `self.client_A2A_instance`
    antes do `super().__init__()` levantava
    `ValueError: "RemoteAgent" object has no field`.
    """

    def __init__(self, **kwargs):
        server_url = kwargs.pop("server_url", None)
        if not server_url:
            raise ValueError("A 'server_url' deve ser fornecida como argumento.")

        kwargs.setdefault("role", "RemoteAgent")
        kwargs.setdefault("goal", "Se conectar a um servidor A2A")
        kwargs.setdefault(
            "backstory", "Você é um agente que busca conteúdo em um servidor A2A"
        )
        # Sem isto o CrewAI aplica o LLM padrão dele — OpenAI — e a Crew inteira
        # falha com "OPENAI_API_KEY is required" mesmo com LLM_MODEL apontando para
        # outro provider. O agente vizinho recebia `llm`; este, não.
        kwargs.setdefault("llm", os.getenv("LLM_MODEL", "gpt-4o-mini"))

        remote_tool = ClientA2ACrewAI(client_a2a=ClientA2A(server_url=server_url))
        # Lista nova: `kwargs.get('tools', [])` + append mutava a lista do chamador.
        kwargs["tools"] = [*kwargs.get("tools", []), remote_tool]

        super().__init__(**kwargs)

"""Tool que chama o agente remoto pelo protocolo A2A.

O ``httpx.AsyncClient`` é criado **dentro** de cada chamada. Antes ele nascia no
``__init__``, fora de qualquer event loop, e era reaproveitado por vários
``asyncio.run()`` distintos — o pool de conexões acaba amarrado a um loop já fechado.
Um cliente por chamada, aberto e fechado no mesmo loop, é o formato correto para uma
tool síncrona do CrewAI.
"""
import asyncio
from typing import Any
from uuid import uuid4

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest

TIMEOUT_SEGUNDOS = 300


class RespostaA2AInvalida(RuntimeError):
    """O servidor respondeu num formato que não conseguimos interpretar."""


def extrair_texto(resultado: dict) -> str:
    """Puxa o texto da primeira parte da resposta, com erro claro se o formato mudar."""
    try:
        return resultado["result"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as e:
        chaves = list(resultado) if isinstance(resultado, dict) else type(resultado).__name__
        raise RespostaA2AInvalida(
            f"resposta sem 'result.parts[0].text' (recebido: {chaves})"
        ) from e


class ClientA2A:
    name: str = "Ferramenta A2A"
    description: str = (
        "Use esta ferramenta para obter conteúdo do servidor A2A. "
        "Forneça um tema ou tópico como input."
    )

    def __init__(self, server_url: str):
        self._base_url = server_url

    async def _async_run(self, query: str) -> str:
        async with httpx.AsyncClient(timeout=TIMEOUT_SEGUNDOS) as http:
            resolver = A2ACardResolver(httpx_client=http, base_url=self._base_url)
            public_card = await resolver.get_agent_card()

            client = A2AClient(httpx_client=http, agent_card=public_card)

            payload: dict[str, Any] = {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": query}],
                    "messageId": uuid4().hex,
                },
            }
            request = SendMessageRequest(
                id=str(uuid4()), params=MessageSendParams(**payload)
            )
            response = await client.send_message(request)

        return extrair_texto(response.model_dump(mode="json", exclude_none=True))

    def _run(self, query: str) -> str:
        """Entrada síncrona usada pelo CrewAI.

        Falha de rede vira texto de erro em vez de exceção: quem consome é um agente,
        que precisa conseguir relatar o problema em vez de abortar a Crew inteira.
        """
        try:
            return asyncio.run(self._async_run(query))
        except (httpx.HTTPError, RespostaA2AInvalida) as e:
            return f"Erro ao contatar o servidor A2A: {e}"

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

from .agent import Agent


class Executor(AgentExecutor):
    """Liga o protocolo A2A ao Crew que realmente escreve o texto."""

    def __init__(self, url, port):
        self.url = url
        self.port = port
        self.url_complete = f'http://{url}:{port}'
        self.agent = Agent(self.url_complete)

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # `get_user_input()` é a API do SDK para extrair o texto da mensagem.
        # Antes isto era `context.request.params.message.parts[0].text` — e
        # `RequestContext` não tem atributo `request`, então toda chamada devolvia
        # JSON-RPC -32603.
        tema = context.get_user_input()
        if not tema:
            await event_queue.enqueue_event(
                new_agent_text_message("Nenhum tema recebido na mensagem.")
            )
            return

        resultado = await self.agent.invoke({"tema": tema})
        await event_queue.enqueue_event(new_agent_text_message(resultado))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception('cancel not supported')

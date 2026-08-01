import os
import uvicorn
from dotenv import load_dotenv
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from .agent_executor import Executor

load_dotenv()

if __name__ == '__main__':
    host = os.getenv("A2A_HOST", "localhost")
    port = int(os.getenv("A2A_PORT", "9999"))
    executor = Executor(url=host, port=port)
    
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )
    
    server_app = A2AStarletteApplication(
        agent_card=executor.agent.public_card,
        http_handler=request_handler,
    )
    
    print("Iniciando o servidor com a classe Agent...")
    uvicorn.run(server_app.build(), host=executor.url, port=executor.port)

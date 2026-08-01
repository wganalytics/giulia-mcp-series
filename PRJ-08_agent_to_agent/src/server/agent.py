from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from .crew_redator import CrewEscritor

class Agent(CrewEscritor):
    def __init__(self, url):
        super().__init__()
        
        self.basic_skill = AgentSkill(
            id='redator',
            name='Redator',
            description='Redator de textos',
            tags=['redator', 'escrita', 'conteudo'],
            examples=[
                'Escreva um texto sobre energia solar no Brasil',
                'Redija um artigo sobre IA na educação',
            ],
        )
        
        self.public_card = AgentCard(
            name='Redator',
            description='Redator de textos',
            url=url,
            version='1.0.0',
            default_input_modes=['text'],
            default_output_modes=['text'],
            skills=[self.basic_skill],
            capabilities=AgentCapabilities(streaming=False),
            supports_authenticated_extended_card=False,
        )

    async def invoke(self, inputs) -> str:
        # Repassa o dict de inputs (ex.: {"tema": ...}) ao Crew interno (CrewEscritor.kickoff).
        response = self.kickoff(inputs)
        return response

import os
from dotenv import load_dotenv
from crewai import Crew, Agent, Task, Process

load_dotenv()

class CrewEscritor:
    def __init__(self):
        # Multi-provider via LiteLLM — defina LLM_MODEL no .env:
        #   gpt-4o-mini | anthropic/claude-3-5-sonnet-20240620 | gemini/gemini-1.5-flash | openrouter/...
        self.llm = os.getenv("LLM_MODEL", "gpt-4o-mini")
        
    def create_crew(self):
        writer = Agent(
            role="Escritor Especialista",
            goal=(
                "Criar conteúdo de alta qualidade, envolvente e bem estruturado para diferentes tipos de textos e formatos."
            ),
            backstory=(
                "Você é um escritor profissional experiente com amplo conhecimento em diversas áreas. "
                "Você domina diferentes estilos de escrita, desde textos técnicos até criativos, "
                "sempre adaptando o tom e a linguagem ao público-alvo e propósito do texto. "
                "Sua especialidade é transformar ideias complexas em textos claros, interessantes e bem organizados."
            ),
            reasoning=True,
            verbose=True,
            llm=self.llm
        )

        task = Task(
            name="Criar conteúdo escrito",
            agent=writer,
            description=r'''
Sua missão:
Escreva um texto sobre o tópico: "{tema}"
Diretrizes de qualidade:
- Use linguagem clara e apropriada para o público-alvo
- Estruture o texto de forma lógica e fluida
- Inclua introdução, desenvolvimento e conclusão
- Mantenha o foco no tópico principal
- Use exemplos quando apropriado
- Revise a gramática e ortografia
Formato da resposta:
Retorne apenas o texto final, bem formatado e pronto para uso.
''',
            expected_output="Texto completo e bem estruturado sobre o tópico solicitado"
        )

        self.crew = Crew(
            agents=[writer],
            tasks=[task],
            process=Process.sequential
        )

    def kickoff(self, inputs):
        self.create_crew()
        response = self.crew.kickoff(inputs=inputs).raw
        return response

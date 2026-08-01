import os
from crewai import Agent, Task, Crew, Process
from remote_agent import RemoteAgent
from dotenv import load_dotenv

load_dotenv()

class PostCrew:
    def __init__(self):
        # Multi-provider via LiteLLM — mesmo LLM_MODEL do servidor (ver .env.example)
        self.llm = os.getenv("LLM_MODEL", "gpt-4o-mini")
        
    def create_agent(self):
        remote_agent = RemoteAgent(
            server_url=os.getenv("A2A_SERVER_URL", "http://localhost:9999")
        )
        
        task_remote_agent = Task(
            description=r"""
            Utilize sua cliente A2A para obter conteúdo sobre o tema = {tema} fornecido
            """,
            expected_output="Conteúdo sobre o tema fornecido.",
            agent=remote_agent
        )
        
        post_agent = Agent(
            role='Redator de Posts para Twitter',
            goal='Criar posts de Twitter atrativos e envolventes com máximo de 120 caracteres baseados no conteúdo fornecido pela ferramenta A2A.',
            backstory=(
                "Você é um redator especializado em criar posts para Twitter. "
                "Você recebe informações da ferramenta A2A e transforma esse conteúdo em tweets "
                "que engajam o público, mantendo a essência da informação original. "
                "Você sempre respeita o limite de 120 caracteres do Twitter."
            ),
            verbose=True,
            llm=self.llm
        )
        
        redacao_task = Task(
            description=r"""
            Com base no texto retornado pelo RemoteAgent, escreva um twitter de 120 caracteres.
            """,
            context=[task_remote_agent],
            expected_output='Um post de Twitter com máximo de 120 caracteres baseado no conteúdo da ferramenta A2A.',
            agent=post_agent
        )
        
        crew = Crew(
            agents=[remote_agent, post_agent],
            tasks=[task_remote_agent, redacao_task],
            process=Process.sequential
        )
        return crew

    def kickoff(self, inputs):
        crew = self.create_agent()
        result = crew.kickoff(inputs).raw
        return result

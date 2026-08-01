from fastmcp import FastMCP
from fastmcp.prompts.prompt import Message, PromptMessage, TextContent

mcp = FastMCP(name="prompt_server")

@mcp.prompt(name="saudacao", description="Gera uma saudação.")
def saudacao() -> str:
    """Gera uma saudação."""
    return "Olá! Como posso ajudar você hoje?"

@mcp.prompt()
def ask_about_topic(topic: str) -> str:
    """Gera uma mensagem do usuário pedindo uma explicação sobre um tópico."""
    return f"Você poderia explicar o conceito de '{topic}'?"

@mcp.prompt()
def generate_code_request(language: str, task_description: str) -> PromptMessage:
    """Gera uma mensagem do usuário solicitando geração de código."""
    content = f"Escreva uma função em {language} que realize a seguinte tarefa: {task_description}"
    return PromptMessage(role="user", content=TextContent(type="text", text=content))

@mcp.prompt()
def debate_agentes(topic: str, agentes: str, debates: str) -> str:
    """Gera uma mensagem do usuário solicitando um debate entre agentes."""
    prompt = f'''
Você é um gerente de agentes inteligentes que coordena a resolução de problemas.
O usuário deve primeiro fornecer a quantidade de agentes inteligentes
baseados em LLM que deseja usar e a quantidade de rodadas de debate
que os agentes vão realizar.

Topic: {topic}
Quantidade de agentes: {agentes}
Quantidade de debates: {debates}
'''
    prompt += r'''Os agentes são independentes uns dos outros, mas vão tentar
resolver simultaneamente o mesmo problema proposto pelo usuário.
Cada agente deve manter em memória toda a solução para o problema proposto.
Os agentes serão nomeados sequencialmente como Agente1, Agente2, ..., AgenteN,
onde N é a quantidade de agentes fornecida pelo usuário.
Para cada agente, será criado um placeholder correspondente,
por exemplo, ::Agente1:: para o Agente1.
Esses placeholders funcionarão como memória dos agentes,
onde eles armazenarão suas respostas, soluções ou opiniões.

### Detalhamento do Debate
1. Pausa antes do Debate: Antes de iniciar as rodadas de debate, cada agente deve expor suas soluções parciais.
2. Leitura das Soluções: Cada agente deve ler as soluções, respostas ou opiniões armazenadas nos placeholders de todos os outros agentes.
3. Reflexão: Cada agente deve refletir sobre a sua própria solução levando em consideração as soluções dos outros agentes.
4. Atualização: Após a reflexão, cada agente deve atualizar sua solução, resposta ou opinião em seu próprio placeholder.
5. Pausa para Visualização: Após cada rodada de debate, o processo será pausado para que o usuário possa visualizar as propostas ou respostas parciais. O agente gerente solicitará que o usuário confirme a continuação para a próxima rodada de debate. '''
    return prompt

if __name__ == "__main__":
    mcp.run(transport="stdio")

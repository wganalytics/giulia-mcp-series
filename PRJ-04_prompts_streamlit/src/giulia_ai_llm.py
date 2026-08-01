import os
import re
import json
import litellm
from dotenv import load_dotenv

load_dotenv()


class MyLLM:
    """Abstração multi-provider via LiteLLM.

    Modelo em LLM_MODEL (.env); chave conforme o provider:
      gpt-4o-mini -> OPENAI_API_KEY | anthropic/claude-... -> ANTHROPIC_API_KEY
      gemini/gemini-1.5-flash -> GEMINI_API_KEY | openrouter/... -> OPENROUTER_API_KEY
    """
    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")

    def chat(self, user_prompt, context_chat=None):
        """Envia a mensagem e devolve o histórico atualizado.

        O histórico recebido não é modificado: a lista é copiada antes. Antes, o
        ``append`` mutava a lista do chamador, então o `st.session_state` era alterado
        mesmo quando a chamada ao modelo falhava no meio.
        """
        messages = list(context_chat or [])
        messages.append({"role": "user", "content": user_prompt})
        response = litellm.completion(model=self.model, messages=messages, max_tokens=1000)
        messages.append({"role": "assistant", "content": response.choices[0].message.content})
        return messages

    def select_prompt(self, query, prompts):
        prompt_text = "\n".join(f"{i+1}. {p.yaml_str()}" for i, p in enumerate(prompts))
        instrucao = f"""Com base na seguinte query do usuário e na lista detalhada de prompts disponíveis,
selecione o prompt mais apropriado para atender à solicitação.
Query do usuário: {query}

Prompts disponíveis:
{prompt_text}
"""
        instrucao += r'''Retire dos prompts disponíveis o prompt mais apropriado e preencha os argumentos.
Quero que você retorne um json no seguinte formato:
{
  "prompt": "nome do prompt mais apropriado",
  "args": { "arg1": "valor apropriado para a query" }
}
É MUITO IMPORTANTE QUE VOCÊ SÓ ME RETORNE O JSON, NÃO RETORNE NADA ALÉM DO JSON.
TODOS OS VALORES DOS ARGUMENTOS DEVEM SER STRING.
'''
        response = litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content": instrucao}],
            max_tokens=1000,
        )
        texto = (response.choices[0].message.content or "").strip()
        # Extrai o primeiro bloco {...} (robusto a cercas ```json e prosa extra).
        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if not match:
            raise ValueError("A resposta não está no formato JSON esperado.")
        return json.loads(match.group(0))

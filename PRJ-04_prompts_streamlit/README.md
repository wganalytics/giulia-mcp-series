# PRJ-04 — Chat Streamlit + Prompts MCP

Chat em **Streamlit** que conecta a um servidor **MCP** (via `stdio`), lista os *prompts*
MCP disponíveis, usa um **LLM** para escolher automaticamente o prompt mais adequado à
pergunta e conduz a conversa.

## Multi-provider (Claude / OpenAI / Gemini / OpenRouter)

O `MyLLM` foi reescrito sobre **LiteLLM**; o modelo vem de `LLM_MODEL` (ver `.env.example`).

## Uso

```bash
uv sync
cp .env.example .env        # defina LLM_MODEL + a chave do provider

# sobe a UI (o cliente sobe o servidor MCP de prompts sozinho, via server_config.json)
uv run streamlit run src/chat.py     # ou: uv run python src/main.py
```

Prompts MCP expostos pelo servidor (`src/server.py`): `saudacao`, `ask_about_topic`,
`generate_code_request`, `debate_agentes`. O LLM seleciona o prompt + preenche os
argumentos a partir da mensagem do usuário.

Correções: modelo agora configurável (antes fixo em Haiku ignorando `self.model`),
`server_config.json` aponta para `src/server.py`, e `main.py` de fato lança o Streamlit.

## Testes

```bash
uv run pytest        # 12 testes
```

Cobrem o histórico da conversa: o `chat()` não pode mutar a lista do chamador, nem deixar o `st.session_state` corrompido quando a chamada ao modelo falha.

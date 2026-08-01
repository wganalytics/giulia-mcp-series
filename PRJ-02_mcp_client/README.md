# PRJ-02 — Cliente MCP (seleção de tool por LLM)

Cliente **MCP** que conecta (via `stdio`) ao servidor do **PRJ-01**, lista as tools e usa
um **LLM** para escolher qual tool chamar a partir de uma pergunta em linguagem natural.

## Multi-provider (Claude / OpenAI / Gemini / OpenRouter)

O `MyLLM` foi reescrito sobre **LiteLLM**: as tools MCP são convertidas para o formato de
*function-calling* e o modelo é escolhido por `LLM_MODEL` (ver `.env.example`).

## Uso

```bash
uv sync
cp .env.example .env      # defina LLM_MODEL + a chave do provider

# depende do PRJ-01 (server_config.json aponta para ../PRJ-01_ping_server)
uv run python src/client.py "faça um ping"     # one-shot
uv run python src/client.py                      # REPL interativo
```

Fluxo: conecta ao server → lista tools → LLM seleciona a tool (ex.: `ping`, `check_host`)
→ executa → mostra o resultado. A sessão MCP é fechada corretamente ao final (antes havia
vazamento de sessão e a query era fixa em `"ping"`).

## Testes

```bash
uv run pytest        # 4 testes
```

Usam uma sessão MCP dublê, sem subir o servidor do PRJ-01. Cobrem a conversão do formato de tool e o fato de `list_tools()` não acumular entre chamadas.

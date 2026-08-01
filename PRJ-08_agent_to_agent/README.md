# PRJ-08 — Agent-to-Agent (A2A)

Demonstra o protocolo **A2A** (Agent-to-Agent) com **dois processos** que se comunicam via
HTTP/JSON-RPC usando o `a2a-sdk`.

- **Servidor** (`src/server/`): expõe um agente CrewAI "Redator" através de um `AgentCard`
  público. Descoberta via `A2ACardResolver`.
- **Cliente** (`src/cliente/`): uma Crew de 2 agentes — um `RemoteAgent` que empacota uma
  tool A2A chamando o servidor remoto, e um "Redator de Posts para Twitter" que transforma
  o retorno em um tweet.

## Multi-provider (Claude / OpenAI / Gemini / OpenRouter)

O modelo é escolhido por `LLM_MODEL` (roteado pelo LiteLLM que o CrewAI usa por baixo):

| Provider | `LLM_MODEL` | Chave |
|---|---|---|
| OpenAI | `gpt-4o-mini` | `OPENAI_API_KEY` |
| Anthropic | `anthropic/claude-3-5-sonnet-20240620` | `ANTHROPIC_API_KEY` |
| Gemini | `gemini/gemini-1.5-flash` | `GEMINI_API_KEY` |
| OpenRouter | `openrouter/openai/gpt-4o-mini` | `OPENROUTER_API_KEY` |

## Uso

```bash
uv sync
cp .env.example .env     # defina LLM_MODEL + a chave do provider

# Terminal 1 — sobe o servidor A2A
uv run python -m src.server

# Terminal 2 — roda o cliente com um tema
uv run python src/cliente/main.py "IA na educação"
```

Host/porta/URL são configuráveis por env (`A2A_HOST`, `A2A_PORT`, `A2A_SERVER_URL`) —
antes eram hardcoded em `localhost:9999`.

## Testes

```bash
uv run pytest        # 17 testes
```

Cobrem a montagem do AgentCard e o parsing da resposta A2A, sem subir o servidor.

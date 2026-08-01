# 📓 Diário de Bordo — PRJ-08_agent_to_agent

> Registro **autônomo** deste projeto: quem lê este arquivo entende o projeto sem
> abrir mais nada. Decisões que valem para o ecossistema inteiro ficam no diário
> central (`governance/operational-memory/DIARIO_DE_BORDO.md`).
> Numeração é própria deste projeto, do #001 em diante.

## 🎯 Identidade

| | |
|---|---|
| **O que é** | Protocolo **A2A**: dois processos independentes conversando por HTTP/JSON-RPC |
| **Stack** | Python 3.11+ · a2a-sdk (0.x) · crewai · uvicorn · uv |
| **Como roda** | `uv run python -m src.server  +  uv run python src/cliente/main.py "tema"` |
| **Depende de** | dois terminais: servidor A2A e cliente |
| **Segredos** | `LLM_MODEL` + chave do provider; `A2A_HOST`/`A2A_PORT`/`A2A_SERVER_URL` |
| **Jira** | `MCP-6` (épico) · `MCP-16` `MCP-17` — projeto `MCP` |

## 📊 Estado — 2026-07-31

- **Funcional:** sim — servidor publica AgentCard, cliente descobre e a Crew local vira o texto em tweet
- **Testes:** 17, passando (`uv run pytest`)
- **Expõe:** AgentCard público em `/.well-known/agent-card.json` com a skill `redator`
- **Pendências:** `a2a-sdk` fixado em `<1.0`: a 1.x reescreveu a API (AgentCard virou protobuf, app foi para FastAPI, cliente virou stream). Migrar é tarefa própria

## 📝 Registro de Sessões

### Sessão #003 — 2026-07-31
**Agente:** Claude Code (Opus 5)
**Foco:** Projeto não subia — incompatibilidade de SDK e três defeitos de execução

**Features entregues:**
- Jira: `MCP-17` estava In Progress — fechada com o registro do A2A entre dois processos; épico **MCP-6** fechado
- `a2a-sdk` fixado em `>=0.3,<1.0`: o `pyproject.toml` pedia `>=1.1.0`, mas o código usa a API 0.x — dependência subida sem migrar o código, e nem o import passava
- Imports do pacote `src/server` convertidos para relativos: `uv run python -m src.server`, o comando do próprio README, quebrava com `ModuleNotFoundError`
- `RemoteAgent` deixou de atribuir `self.client_A2A_instance` antes do `super().__init__()` — `Agent` do CrewAI é modelo pydantic e recusava o atributo; o cliente foi para dentro da tool, que é quem precisa dele
- `context.get_user_input()` no lugar de `context.request.params.message.parts` — `RequestContext` não tem atributo `request`, e toda chamada A2A devolvia JSON-RPC -32603
- `httpx.AsyncClient` passou a nascer dentro do event loop que o usa; antes era criado no `__init__` e reaproveitado por vários `asyncio.run()` distintos
- `except Exception` genérico substituído por captura tipada: erro de rede e formato viram texto para o agente relatar, erro de programação estoura
- `CREWAI_TRACING_ENABLED=false` no `.env` e `.env.example` — o CrewAI abre prompt interativo de 20s que travaria execução automatizada
- 17 testes (`tests/test_a2a.py`) cobrindo AgentCard e parsing da resposta

**Decisões arquiteturais:**
- Fixar o SDK em vez de migrar para 1.x: a migração é tarefa própria (AgentCard virou protobuf, app saiu de Starlette para FastAPI via `a2a.server.routes`, cliente virou `create_client` com stream)

**Problemas encontrados:**
- Os três defeitos de execução só apareceram ao rodar de verdade — os testes de import não os pegariam. A mensagem de erro tipada introduzida nesta sessão foi o que revelou o JSON-RPC -32603 rapidamente

**Próximos passos:**
- Decidir entre migrar para `a2a-sdk` 1.x ou manter o pin em `<1.0`.

### Sessão #002 — 2026-07-01
**Agente:** Antigravity (Gemini 3.1 Pro)
**Foco:** Refatoração de Histórico Jira e Injeção Funcional

**Features entregues:**
- Injeção da `TASK-2` (Desenvolvimento Funcional do Módulo MCP) no manifesto `projeto.yaml`.
- Sincronização Jira executada com recriação de chaves para evitar colisões de estado.
- Tarefa de Padronização (`TASK-1`) movida para DONE no Jira.
- Tarefa de Desenvolvimento (`TASK-2`) movida para IN_PROGRESS (Aguardando remoção de mocks) no Jira.

**Próximos passos:**
- Remoção de mocks e integração final.

### Sessão #001 — 2026-07-01
**Agente:** Antigravity (Gemini 3.1 Pro)
**Foco:** Refatoração de Identidade e Padronização do Ecossistema GARE

**Features entregues:**
- Código-fonte e scripts movidos para o diretório `src/`.
- Dependências de dados movidas para o diretório `data/`.
- Documentação e artefatos de governança gerados no diretório `specs/`.

**Decisões arquiteturais:**
- O projeto foi desmembrado do repositório de laboratório original e encapsulado em sua própria estrutura independente sob `dev/mcp/`, garantindo portabilidade, isolamento de código e governança via RLM (Memória Operacional) exigida pelo ecossistema.

**Problemas encontrados:**
- N/A (Migração limpa das classes de conexão, prompts e agentes via script automatizado).

**Próximos passos:**
- Iniciar a sincronização do projeto com o Jira Board e preparar o ambiente para os próximos testes da esteira de integração.

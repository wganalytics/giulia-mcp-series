# 📓 Diário de Bordo — PRJ-05_secure_server

> Registro **autônomo** deste projeto: quem lê este arquivo entende o projeto sem
> abrir mais nada. Decisões que valem para o ecossistema inteiro ficam no diário
> central (`governance/operational-memory/DIARIO_DE_BORDO.md`).
> Numeração é própria deste projeto, do #001 em diante.

## 🎯 Identidade

| | |
|---|---|
| **O que é** | Servidor MCP cujas tools só executam mediante API Key válida (bcrypt + SQLite) |
| **Origem** | Cap. 6 do livro *Model Context Protocol* (Sandeco) |
| **Stack** | Python 3.11+ · fastmcp · bcrypt · sqlite3 · uv |
| **Como roda** | `uv run python src/server_seguro.py` |
| **Depende de** | bootstrap por CLI: `create-user` → `gen-key` → `.env` |
| **Segredos** | `GIULIA_AI_API_KEY` (formato `sk-{user_id}-{secret}`) |
| **Jira** | `MCP-24` (épico) · `MCP-25` `MCP-26` — projeto `MCP` |

## 📊 Estado — 2026-07-31

- **Funcional:** sim — autentica com chave válida e rejeita chave ausente, inválida ou de outro usuário
- **Testes:** 33, passando (`uv run pytest`)
- **Expõe:** 2 tools protegidas: `tool_segura`, `listar_usuarios`
- **Pendências:** a chave vem do ambiente do **próprio servidor**, então isto é gate de configuração, não autenticação de chamador — autenticar quem chama exigiria transporte HTTP

## 📝 Registro de Sessões

### Sessão #003 — 2026-07-31
**Agente:** Claude Code (Opus 5)
**Foco:** Custo da validação de API Key, ciclo de vida e limite real do mecanismo

**Features entregues:**
- Jira: o projeto não tinha card nenhum — épico **MCP-24** e tasks `MCP-25`/`MCP-26` criados e fechados
- `lookup_hash` (SHA-256) como índice: a validação localiza a linha exata e roda `bcrypt.checkpw` UMA vez — antes rodava contra todas as chaves do usuário (O(n) numa função lenta de propósito)
- Migração automática para bancos sem a coluna; chaves antigas seguem válidas e ganham o índice no primeiro uso
- `__del__` substituído por `close()` explícito + context manager
- Mascaramento reescrito: preservava os 3 primeiros caracteres, que são sempre `sk-`
- `except Exception` genéricos trocados por exceção tipada (`ChaveMalFormada`) — erro de banco virava "chave inválida"
- 33 testes (`tests/test_api_key.py`), inclusive um que conta as chamadas ao bcrypt

**Decisões arquiteturais:**
- SHA-256 puro é seguro como índice porque o segredo tem 32 bytes de `secrets.token_urlsafe`; bcrypt segue como verificador. Índice rápido para achar, verificador lento para confirmar
- Documentado no README que isto é **gate de configuração, não autenticação de chamador**: a chave vem do ambiente do próprio servidor, e em stdio o servidor é processo filho do cliente — não há outro chamador a distinguir

**Problemas encontrados:**
- Destrutor como ponto de liberação de recurso: roda em hora indeterminada e engole exceção

**Próximos passos:**
- Autenticação de chamador de verdade exigiria transporte HTTP com a chave na requisição — fora do escopo do Cap. 6.

### Sessão #002 — 2026-07-01
**Agente:** Antigravity (Gemini 3.1 Pro)
**Foco:** Refatoração de Histórico Jira e Injeção Funcional

**Features entregues:**
- Injeção da `TASK-2` (Desenvolvimento Funcional do Módulo MCP) no manifesto `projeto.yaml`.
- Sincronização Jira executada com recriação de chaves para evitar colisões de estado.
- Tarefa de Padronização (`TASK-1`) movida para DONE no Jira.
- Tarefa de Desenvolvimento (`TASK-2`) movida para DONE no Jira.

**Próximos passos:**
- Manutenção e evolução de features.

### Sessão #001 — 2026-07-01
**Agente:** Antigravity (Gemini 3.1 Pro)
**Foco:** Refatoração de Identidade e Padronização do Ecossistema GARE

**Features entregues:**
- Substituição de referências "Sandeco" para "Giulia-ai" e "Giulia AI".
- Código-fonte e scripts movidos para o diretório `src/`.
- Dependências de dados movidas para o diretório `data/`.
- Documentação e artefatos de governança gerados no diretório `specs/`.

**Decisões arquiteturais:**
- O projeto foi desmembrado do repositório de laboratório original e encapsulado em sua própria estrutura independente sob `dev/mcp/`, garantindo portabilidade, isolamento de código e governança via RLM (Memória Operacional) exigida pelo ecossistema.

**Problemas encontrados:**
- N/A (Migração limpa das classes de conexão, prompts e agentes via script automatizado).

**Próximos passos:**
- Iniciar a sincronização do projeto com o Jira Board e preparar o ambiente para os próximos testes da esteira de integração.

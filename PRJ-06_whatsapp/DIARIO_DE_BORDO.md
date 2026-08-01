# 📓 Diário de Bordo — PRJ-06_whatsapp

> Registro **autônomo** deste projeto: quem lê este arquivo entende o projeto sem
> abrir mais nada. Decisões que valem para o ecossistema inteiro ficam no diário
> central (`governance/operational-memory/DIARIO_DE_BORDO.md`).
> Numeração é própria deste projeto, do #001 em diante.

## 🎯 Identidade

| | |
|---|---|
| **O que é** | Servidor MCP que dá a um agente tools para operar o WhatsApp via Evolution API |
| **Origem** | Cap. 7 do livro *Model Context Protocol* (Sandeco) |
| **Stack** | Python 3.11+ · fastmcp · httpx · uv |
| **Como roda** | `uv run python src/evoapi_mcp.py` |
| **Depende de** | instância **Evolution API v2** com número pareado |
| **Segredos** | `EVOLUTION_BASE_URL`, `EVOLUTION_API_KEY` (token de instância), `EVOLUTION_INSTANCE` |
| **Jira** | `MCP-4` (épico) · `MCP-12` `MCP-13` — projeto `MCP` |

## 📊 Estado — 2026-07-31

- **Funcional:** sim — verificado contra a instância real GIULIA_AI, incluindo envio confirmado
- **Testes:** 35, passando (`uv run pytest`) — rede mockada
- **Expõe:** 4 tools: `get_groups`, `get_group_messages`, `send_message_to_group`, `send_message_to_phone`
- **Pendências:** o recorte por data é client-side (o endpoint `findMessages` não filtra por período) e esse endpoint **não devolve ordenado**

## 📝 Registro de Sessões

### Sessão #003 — 2026-07-31
**Agente:** Claude Code (Opus 5)
**Foco:** Vazamento de conexão HTTP, normalização de destino e verificação contra instância real

**Features entregues:**
- Jira: `MCP-13` estava In Progress — fechada com o registro da validação contra a instância Evolution real; épico **MCP-4** fechado
- `EvolutionClient` compartilhado via `get_client()` — criação preguiçosa, `close_client()` em `atexit`, injetável para teste. Medido: 10 chamadas de tool abriam 10 pools HTTP nunca fechados; agora 1
- `normalizar_destino()` — o "+55" existia só como instrução no docstring da tool, dependia de o LLM lembrar. Virou código: 10/11 dígitos ganham o DDI, máscara é removida, JID passa intacto
- Tool de envio passou a devolver o id da mensagem; antes descartava a resposta da Evolution e retornava string genérica
- 35 testes (`tests/test_evolution_client.py`) com `httpx.MockTransport`, sem rede

**Decisões arquiteturais:**
- Um servidor MCP atende uma instância da Evolution, então cliente reaproveitado é o formato correto: mantém keep-alive e não acumula sockets
- Passou a usar **token de instância** em vez da `AUTHENTICATION_API_KEY` global (que controla todas as instâncias) — privilégio mínimo

**Problemas encontrados:**
- `chat/findMessages` não devolve ordenado: a primeira verificação de entrega olhou os 2 últimos da array e concluiu erradamente que a mensagem não chegara
- O escopo do token de instância não foi comprovado — o servidor tem só uma instância, então o teste não distingue "restrito" de "só existe uma"

**Próximos passos:**
- Nenhum pendente. Verificado contra a instância GIULIA_AI (Evolution v2.3.7): 4 grupos reais, histórico com filtro de data, e envio confirmado pelo destinatário.

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

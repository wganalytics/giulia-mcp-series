# 📓 Diário de Bordo — PRJ-04_prompts_streamlit

> Registro **autônomo** deste projeto: quem lê este arquivo entende o projeto sem
> abrir mais nada. Decisões que valem para o ecossistema inteiro ficam no diário
> central (`governance/operational-memory/DIARIO_DE_BORDO.md`).
> Numeração é própria deste projeto, do #001 em diante.

## 🎯 Identidade

| | |
|---|---|
| **O que é** | Chat Streamlit que lista os **Prompts** MCP e deixa o LLM escolher o mais adequado |
| **Origem** | Cap. 5 do livro *Model Context Protocol* (Sandeco) |
| **Stack** | Python 3.11+ · streamlit · litellm · fastmcp · uv |
| **Como roda** | `uv run streamlit run src/chat.py` |
| **Depende de** | `src/server.py` (o próprio cliente sobe o servidor de prompts) |
| **Segredos** | `LLM_MODEL` + chave do provider |
| **Jira** | `MCP-21` (épico) · `MCP-22` `MCP-23` — projeto `MCP` |

## 📊 Estado — 2026-08-02

- **Funcional:** sim — com Gemini, o LLM escolheu `generate_code_request` (justamente o
  prompt que estava quebrado) com os argumentos corretos, e o histórico cresceu como esperado
- **Testes:** 12, passando (`uv run pytest`)
- **Expõe:** 4 prompts: `saudacao`, `ask_about_topic`, `generate_code_request`, `debate_agentes`
- **Pendências:** nenhuma

## 📝 Registro de Sessões

### Sessão #004 — 2026-08-02
**Agente:** Claude Code (Opus 5)
**Foco:** Prompt que listava e explodia; testes async ignorados

**Features entregues:**
- **Corrigido: `generate_code_request` quebrava no `get_prompt`.** Devolvia `PromptMessage`
  cru, que o fastmcp recusa (`Prompt must return str, list[Message], or PromptResult`).
  Aparecia normalmente no `list_prompts` — então um agente descobria e escolhia o prompt
  quebrado. Virou `list[Message]`
- **Faltava `pytest-asyncio`**: sem ele os testes `async` não rodavam, eram ignorados em
  silêncio. Adicionado com `asyncio_mode = "auto"`
- `tests/test_prompts_render.py`: renderiza **todos** os prompts pelo `Client` em memória (6 → 12)
- Publicado no repositório público **github.com/wganalytics/giulia-mcp-series** (MIT, CI verde)
- `LICENSE` (MIT) e `.gitignore` próprios
- CI no GitHub Actions rodando os testes a cada push

**Decisões arquiteturais:**
- Listar não é renderizar. Um prompt só está entregue quando `get_prompt` devolve texto

**Problemas encontrados:**
- Cobertura de **22%** — `chat.py`, `client.py` e `giulia_ai_mcp_conn.py` sem teste algum

**Próximos passos:**
- Cobrir o cliente e a conexão MCP, hoje validados só por execução manual

---

### Sessão #003 — 2026-07-31
**Agente:** Claude Code (Opus 5)
**Foco:** Vazamento de subprocesso, mutação de histórico e cobertura de testes

**Features entregues:**
- Jira: o projeto não tinha card nenhum — épico **MCP-21** e tasks `MCP-22`/`MCP-23` criados e fechados
- Sessão MCP passou a abrir e fechar dentro da mesma chamada — `query_with_prompt` fazia `connect()` e nunca desconectava, deixando um subprocesso órfão a cada rerun do Streamlit
- `chat()` deixou de mutar a lista de contexto do chamador (copia antes)
- `list_prompts()` deixou de imprimir; conexão ganhou context manager assíncrono
- 6 testes (`tests/test_llm_context.py`)

**Decisões arquiteturais:**
- Cada interação do Streamlit roda no seu próprio `asyncio.run()`, então a sessão MCP tem que viver dentro de uma chamada — manter conexão entre reruns amarraria o recurso a um event loop já fechado

**Problemas encontrados:**
- Vazamento do subprocesso do servidor MCP (mesmo bug que o PRJ-02 já havia corrigido)
- `chat()` mutava o `st.session_state` mesmo quando a chamada ao modelo falhava — coberto por teste

**Próximos passos:**
- Nenhum pendente. Verificado: prompt selecionado pelo LLM e conversa continuada com histórico preservado.

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

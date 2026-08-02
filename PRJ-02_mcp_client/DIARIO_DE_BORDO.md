# 📓 Diário de Bordo — PRJ-02_mcp_client

> Registro **autônomo** deste projeto: quem lê este arquivo entende o projeto sem
> abrir mais nada. Decisões que valem para o ecossistema inteiro ficam no diário
> central (`governance/operational-memory/DIARIO_DE_BORDO.md`).
> Numeração é própria deste projeto, do #001 em diante.

## 🎯 Identidade

| | |
|---|---|
| **O que é** | Cliente MCP que usa um LLM para escolher qual tool chamar a partir de linguagem natural |
| **Origem** | Cap. 3 do livro *Model Context Protocol* (Sandeco) |
| **Stack** | Python 3.11+ · litellm · mcp[cli] · uv |
| **Como roda** | `uv run python src/client.py "faça um ping"` |
| **Depende de** | **PRJ-01** (sobe o servidor via `server_config.json`) |
| **Segredos** | `LLM_MODEL` + chave do provider (OpenAI/Anthropic/Gemini/OpenRouter) |
| **Jira** | `MCP-18` (épico) · `MCP-19` `MCP-20` — projeto `MCP` |

## 📊 Estado — 2026-08-02

- **Funcional:** sim — conectou ao PRJ-01 por stdio, listou 3 tools e chamou `ping` remoto.
  Com Gemini, o LLM escolheu `ping`/`echo`/`check_host` e **extraiu host e porta da
  pergunta em linguagem natural**; sem tool aplicável, caiu no chat direto
- **Testes:** 4, passando (`uv run pytest`)
- **Expõe:** CLI em dois modos: one-shot e REPL
- **Pendências:** nenhuma

## 📝 Registro de Sessões

### Sessão #004 — 2026-08-02
**Agente:** Claude Code (Opus 5)
**Foco:** Publicação e prova funcional do ciclo completo com LLM

**Features entregues:**
- Publicado no repositório público **github.com/wganalytics/giulia-mcp-series** (MIT, CI verde)
- `LICENSE` (MIT) e `.gitignore` próprios
- CI no GitHub Actions rodando os testes a cada push

**Decisões arquiteturais:**
- Nenhuma mudança de código

**Problemas encontrados:**
- Nenhum defeito, mas a **cobertura de teste é 14% — a menor da série**. `client.py` e
  `giulia_ai_llm.py` não são exercitados por teste nenhum; foram validados só por execução

**Próximos passos:**
- Cobrir `select_tool` com dublê de resposta do provider, para não depender de chave

---

### Sessão #003 — 2026-07-31
**Agente:** Claude Code (Opus 5)
**Foco:** Correção de cache mutável, ciclo de vida da conexão e verificação ponta a ponta

**Features entregues:**
- Jira: o projeto não tinha card nenhum — épico **MCP-18** e tasks `MCP-19`/`MCP-20` criados e fechados
- `list_tools()` passou a devolver lista nova — acumulava em `self.tools`, então duas chamadas na mesma sessão mandavam as tools duplicadas ao modelo
- Conexão MCP ganhou `__aenter__`/`__aexit__`; `client.py` usa `async with`
- Parâmetro `tools` morto removido de `MyLLM.chat()`; a impressão das tools saiu do método de dados para o chamador
- 4 testes (`tests/test_mcp_conn.py`) com sessão dublê, sem subir o servidor

**Decisões arquiteturais:**
- Método que lê dados não imprime: a listagem passou a ser responsabilidade do CLI

**Problemas encontrados:**
- `list_tools()` acumulava no atributo de instância — corrigido para retorno puro

**Próximos passos:**
- Nenhum pendente. Verificado: `check_host` selecionado pelo LLM com argumentos preenchidos (`1.1.1.1:443` → UP 18.8 ms).

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

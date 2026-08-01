# 📓 Diário de Bordo — PRJ-03_resources

> Registro **autônomo** deste projeto: quem lê este arquivo entende o projeto sem
> abrir mais nada. Decisões que valem para o ecossistema inteiro ficam no diário
> central (`governance/operational-memory/DIARIO_DE_BORDO.md`).
> Numeração é própria deste projeto, do #001 em diante.

## 🎯 Identidade

| | |
|---|---|
| **O que é** | Servidor MCP que demonstra **Resources** — expor dados em vez de ações |
| **Stack** | Python 3.11+ · fastmcp · mcp[cli] · uv |
| **Como roda** | `uv run python src/resources_server.py` |
| **Depende de** | `data/contatos.csv` (dados fictícios de demonstração) |
| **Segredos** | nenhum — `AGENT_NAME` é opcional |
| **Jira** | `MCP-3` (épico) · `MCP-10` `MCP-11` — projeto `MCP` |

## 📊 Estado — 2026-07-31

- **Funcional:** sim — verificado por MCP stdio real
- **Testes:** 14, passando (`uv run pytest`)
- **Expõe:** 5 resources: 1 estático, 2 de arquivo, 2 templates dinâmicos (`contato://{nome}`, `greeting://{nome}`)
- **Pendências:** nenhuma

## 📝 Registro de Sessões

### Sessão #003 — 2026-07-31
**Agente:** Claude Code (Opus 5)
**Foco:** Cobertura de testes dos resources

**Features entregues:**
- Jira: épico **MCP-3** já estava Done e condiz com a realidade — nada a corrigir
- 14 testes (`tests/test_resources.py`) cobrindo os três formatos de resource, a busca de contato por nome (case-insensitive) e o caso "não encontrado"
- Teste específico para a resolução de caminhos a partir da raiz do projeto — rodar de outra pasta não pode quebrar

**Decisões arquiteturais:**
- O teste do template dinâmico verifica que UM contato volta, não o CSV inteiro: é esse o ponto do resource parametrizado

**Problemas encontrados:**
- Nenhum defeito novo. O `pathlib` já corrigia o bug de caminho relativo; agora há teste que trava a regressão.

**Próximos passos:**
- Nenhum pendente. Verificado: 5 resources listados via MCP stdio real.

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
- Código-fonte e scripts movidos para o diretório `src/`.
- Dependências de dados movidas para o diretório `data/`.
- Documentação e artefatos de governança gerados no diretório `specs/`.

**Decisões arquiteturais:**
- O projeto foi desmembrado do repositório de laboratório original e encapsulado em sua própria estrutura independente sob `dev/mcp/`, garantindo portabilidade, isolamento de código e governança via RLM (Memória Operacional) exigida pelo ecossistema.

**Problemas encontrados:**
- N/A (Migração limpa das classes de conexão, prompts e agentes via script automatizado).

**Próximos passos:**
- Iniciar a sincronização do projeto com o Jira Board e preparar o ambiente para os próximos testes da esteira de integração.

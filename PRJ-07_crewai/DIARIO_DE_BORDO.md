# 📓 Diário de Bordo — PRJ-07_crewai

> Registro **autônomo** deste projeto: quem lê este arquivo entende o projeto sem
> abrir mais nada. Decisões que valem para o ecossistema inteiro ficam no diário
> central (`governance/operational-memory/DIARIO_DE_BORDO.md`).
> Numeração é própria deste projeto, do #001 em diante.

## 🎯 Identidade

| | |
|---|---|
| **O que é** | Text-to-SQL: agente CrewAI gera SELECT a partir do schema e consulta PostgreSQL |
| **Origem** | Cap. 8 do livro *Model Context Protocol* (Sandeco) |
| **Stack** | Python 3.11+ · crewai · fastmcp · psycopg2 · streamlit · uv |
| **Como roda** | `uv run streamlit run src/main.py` |
| **Depende de** | PostgreSQL com os bancos `ecommerce` e `clinica` (seeds em `data/`) |
| **Segredos** | `LLM_MODEL` + chave do provider + credenciais PG (use role somente-leitura) |
| **Jira** | `MCP-5` (épico) · `MCP-14` `MCP-15` — projeto `MCP` |

## 📊 Estado — 2026-08-01

- **Funcional:** sim — pergunta em português devolve dados reais em ~2s
- **Testes:** 68, passando (53 de lógica pura + 15 de integração com `PRJ07_TEST_DSN` definido)
- **Expõe:** 2 tools: `buscar_dados_sql`, `listar_databases`
- **Pendências:** nenhuma — somente-leitura garantido por sessão `readonly=True` no PostgreSQL

## 📝 Registro de Sessões

### Sessão #004 — 2026-08-01
**Agente:** Claude Code (Opus 5)
**Foco:** Credencial de banco sem valor padrão

**Features entregues:**
- `PG_USER` e `PG_PASSWORD` passaram a ser obrigatórias: `_obrigatorio()` levanta `ConfiguracaoAusente` em vez de cair num default. `PG_HOST` e `PG_PORT` seguem com padrão — errar neles não muda privilégio, só falha a conexão
- 6 testes novos (62 → 68): variável ausente, variável vazia, mensagem de erro que não vaza a senha, e host/porta mantendo o padrão
- `.env.example`: linha em branco + comentário entre `PG_PASSWORD=` e `PG_ECOMMERCE_DB=` — sem isso a regra `generic-api-key` do gitleaks atravessava a quebra de linha e apontava o nome do banco como segredo

**Decisões arquiteturais:**
- **Credencial não tem valor padrão.** `PG_USER` caía em `postgres` — o superusuário — e `PG_PASSWORD` numa senha conhecida. A conexão podia ter sucesso com privilégio errado, em silêncio, contradizendo o desenho somente-leitura que é a tese do projeto. Falha de configuração tem que aparecer na configuração

**Problemas encontrados:**
- O fallback foi encontrado por leitura, não por teste: nenhum teste exercitava o caminho da variável ausente, então o default nunca era visto
- O gitleaks reportou falso positivo no `.env.example` (linha vazia + linha seguinte capturada como valor). Confirmado por hexdump antes de mexer

**Próximos passos:**
- Considerar mover a montagem da URI para fora do f-string, para a senha não transitar em string que possa ir para log

---

### Sessão #003 — 2026-07-31
**Agente:** Claude Code (Opus 5)
**Foco:** Guard de SQL contornável, garantia no banco e catálogo de bancos

**Features entregues:**
- Jira: `MCP-15` estava In Progress — fechada com o registro do text-to-SQL sobre PostgreSQL real; épico **MCP-5** fechado
- `src/sql_guard.py` — validador que percorre o SQL num passe separando código de literal/comentário (aspas com escape `''`, identificadores `"..."`, dollar-quoting, comentários `--` e `/* */` aninhados); exige statement único, allowlist de início e denylist para CTE que escreve
- `postgres_connection.py` com `set_session(readonly=True)`, `statement_timeout` e context manager
- Catálogo de bancos saiu do `if/elif` do servidor para `PostgresDatabases` (nome + schema YAML por entrada), com nomes resolvidos a cada chamada em vez de no import
- `buscar_database_name`, que ignorava o argumento e devolvia string fixa, virou `listar_databases()`
- README ganhou seção Segurança com o SQL do role somente-leitura
- 68 testes: 53 de lógica pura + 15 de integração contra PostgreSQL 16 real

**Decisões arquiteturais:**
- Duas camadas com papéis distintos: validação na aplicação é conveniência (erro legível, falha barata, barra múltiplos statements); a transação read-only do PostgreSQL é a garantia — quem recusa escrita é o banco, não Python

**Problemas encontrados:**
- O guard era contornável: `startswith("select")` + `rstrip(";")` deixava passar `SELECT 1; DROP TABLE clientes`, e psycopg2 executa vários comandos num único `execute()`. Vetor: prompt injection, já que o SQL vem de LLM lendo texto do usuário. Coberto por `test_rejeita_o_bypass_original`
- Ordem de import alterava configuração: `PostgresDatabases` lia o ambiente no carregamento do módulo, dependendo do `load_dotenv()` de outro módulo ter rodado antes

**Próximos passos:**
- Remover o container `prj07-mcp-pg` quando não for mais necessário — o `.env` aponta para a porta 55432 dele.

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

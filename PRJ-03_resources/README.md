# PRJ-03 — Servidor de Resources MCP

Servidor **MCP** (FastMCP, `stdio`) que demonstra **Resources** — a forma padronizada do
MCP expor *dados* (em vez de *tools*) para o modelo.

## Resources expostos

| URI | Tipo | Conteúdo |
|---|---|---|
| `echo://static` | estático | Identidade do agente (nome via `AGENT_NAME`, default `Giulia-ai`). |
| `file://readme` | arquivo | Bytes reais deste `README.md`. |
| `file://contatos` | arquivo | CSV de contatos (dados de **demonstração**). |
| `contato://{nome}` | **template dinâmico** | Busca UM contato pelo nome dentro do CSV. |
| `greeting://{nome}` | template dinâmico | Saudação personalizada. |

Correções em relação à versão inicial: caminhos de arquivo agora são resolvidos via
`pathlib` relativos à raiz do projeto (antes eram relativos ao diretório de execução e
quebravam), e o CSV correto em `data/contatos.csv`.

## Uso

```bash
uv sync
cp .env.example .env        # opcional: definir AGENT_NAME
uv run python src/resources_server.py   # ou: uv run python src/main.py
```

Os dados de contato são fictícios (demo). Para um cenário real, aponte `CONTATOS_PATH`
para um export do seu CRM ou troque o resource por uma consulta a banco/API.

## Testes

```bash
uv run pytest        # 14 testes
```

Cobrem os três formatos de resource e, principalmente, que os caminhos resolvem a partir da raiz do projeto — rodar de outra pasta não pode quebrar.

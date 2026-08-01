# Série MCP — 8 servidores de protocolo de agentes

Oito projetos que implementam o **Model Context Protocol** (MCP) e o protocolo
**Agent-to-Agent** (A2A) em Python, do servidor mínimo até dois agentes conversando
entre processos separados.

Servidor **e** cliente escritos à mão sobre transporte stdio — sem framework de
agente escondendo o protocolo.

**1.830 linhas · 194 testes · os 8 rodam de verdade.**

---

## Os projetos

| # | Projeto | O que demonstra | Testes |
|---|---|---|---|
| 01 | [`ping_server`](PRJ-01_ping_server) | servidor MCP mínimo; health-check TCP real com latência medida | 12 |
| 02 | [`mcp_client`](PRJ-02_mcp_client) | cliente que lista tools, traduz para function-calling e deixa o LLM escolher | 4 |
| 03 | [`resources`](PRJ-03_resources) | as três formas de resource: estático, binário e **template com parâmetro na URI** | 14 |
| 04 | [`prompts_streamlit`](PRJ-04_prompts_streamlit) | prompt versionado no servidor, selecionado por LLM em runtime, com chat Streamlit | 6 |
| 05 | [`secure_server`](PRJ-05_secure_server) | autenticação por API key: bcrypt + índice SHA-256, arquitetura em camadas | 33 |
| 06 | [`whatsapp`](PRJ-06_whatsapp) | 4 tools sobre a Evolution API — leitura de grupos e envio de mensagem | 35 |
| 07 | [`crewai`](PRJ-07_crewai) | text-to-SQL multi-agente com **defesa em duas camadas** contra SQL injection | 73 |
| 08 | [`agent_to_agent`](PRJ-08_agent_to_agent) | A2A: AgentCard publicado, descoberta em runtime, agente remoto como tool local | 17 |

Cada projeto tem `README.md` próprio, `specs/` e um `DIARIO_DE_BORDO.md` com as
decisões e os problemas encontrados.

## Como rodar

Cada projeto é independente, com seu próprio ambiente e lockfile ([uv](https://docs.astral.sh/uv/)):

```bash
cd PRJ-01_ping_server
cp .env.example .env      # exceto o PRJ-01, que não lê variável de ambiente
uv sync
uv run pytest             # os testes não precisam de credencial nem de rede
uv run python src/main.py
```

## Dois destaques técnicos

### PRJ-07 — validar prefixo não é validar comando

A validação original aceitava qualquer SQL que **começasse** com `select`. Isso
deixava passar:

```sql
SELECT 1; DROP TABLE clientes
```

O `psycopg2` executa múltiplos comandos numa única chamada de `execute()`, e o SQL
vem de um LLM que leu texto do usuário — o vetor é prompt injection.

A correção não foi endurecer a string. [`sql_guard.py`](PRJ-07_crewai/src/sql_guard.py)
percorre o SQL num passe separando código de literal e comentário (aspas com escape
`''`, identificadores `"..."`, dollar-quoting `$$`, comentários `--` e `/* */`
aninhados). Só com isso é possível afirmar que `WHERE acao = 'DROP TABLE clientes'`
é dado.

E a premissa mudou: **o guard na aplicação é conveniência; a garantia mora no banco.**
A sessão abre com `set_session(readonly=True)` antes de qualquer query. O README do
projeto traz o SQL de criação de uma role somente-leitura, validado.

### PRJ-05 — o limite está documentado, não escondido

O projeto se chama "servidor seguro" e o README explica **onde a segurança não
alcança**: em transporte stdio o servidor é processo filho do cliente, e a chave vem
de variável de ambiente do próprio servidor. Isso é um **gate de configuração**, não
autenticação de chamador.

## Origem e atribuição

Os 8 projetos partem dos **capítulos 2 a 9** do livro *Model Context Protocol*, de
Sandeco Macedo. O livro não está incluído neste repositório e não é redistribuído
aqui — apenas o código autoral escrito a partir dele.

O que diferencia esta versão dos exemplos do livro:

- **cada mock virou implementação real** — o health-check simulado virou socket TCP,
  o `print()` de envio virou integração com gateway real, o cursor falso com SQL fixo
  virou PostgreSQL com carga versionada
- **194 testes onde havia zero**
- **13 defeitos corrigidos**, três deles invisíveis a teste de import — só apareceram
  ao executar

## ⚠️ Avisos

**PRJ-06 age sobre WhatsApp real.** As tools `send_message_to_group` e
`send_message_to_phone` enviam mensagem de verdade, para pessoas de verdade, se você
apontar para uma instância pareada. Teste com um grupo seu. Os 35 testes automatizados
**não tocam a rede** (`httpx.MockTransport`).

**Nenhum `.env` está versionado.** Cada projeto traz `.env.example` com os nomes das
variáveis, sem valor.

## Licença

[MIT](LICENSE) — cada projeto também traz sua própria cópia.

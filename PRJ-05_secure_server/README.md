# PRJ-05 — Servidor MCP Seguro (autenticação por API Key)

Servidor **MCP** (FastMCP, transporte `stdio`) cujas *tools* só executam mediante uma
**API Key válida**. As chaves são geradas com `secrets.token_urlsafe`, **hasheadas com
bcrypt** e guardadas em SQLite; a validação usa `bcrypt.checkpw`. Senhas de usuário também
são hasheadas com bcrypt. Corresponde ao **Capítulo 6** do livro *Model Context Protocol*
(Sandeco).

## Arquitetura

```
database.py    → SQLite (tabelas users, api_keys) — grava em data/database.db
repository.py  → UserRepository / APIKeyRepository (SQL parametrizado)
generate_api_key.py → par (segredo, hash bcrypt)
api_key_controller.py → orquestra geração/validação/máscara de chaves
server_seguro.py → tools MCP protegidas (tool_segura, listar_usuarios)
main.py        → CLI de bootstrap (create-user / gen-key / list-users)
```

Formato da chave pública: `sk-{user_id}-{secret}` (só o hash do segredo é persistido).

## Uso

```bash
uv sync

# 1) cria um usuário (senha hasheada com bcrypt)
uv run python src/main.py create-user --name "Giulia" --email giulia@ex.com --password ***

# 2) gera a API Key (exibida UMA vez)
uv run python src/main.py gen-key --user-id 1 --name "chave-dev"

# 3) configure a chave no ambiente
cp .env.example .env   # e cole a full key em GIULIA_AI_API_KEY

# 4) sobe o servidor MCP
uv run python src/server_seguro.py
```

Com a chave configurada, a tool `tool_segura` retorna uma saudação com os dados do
usuário autenticado; sem chave (ou inválida), toda tool lança `API Key inválida`.

## Segurança

- Segredos hasheados (bcrypt + salt), nunca em texto puro no banco.
- SQL sempre parametrizado (sem injeção).
- Chave exibida uma única vez; no banco fica só a versão mascarada + hash.
- `.env` e `data/*.db` fora do controle de versão (ver `.gitignore`).

### Custo da validação

Cada chave guarda **dois** derivados: o hash bcrypt (o verificador) e um `lookup_hash`
(SHA-256, apenas um índice). A validação localiza a linha exata pelo índice e roda
`bcrypt.checkpw` **uma vez**. Antes o bcrypt rodava contra todas as chaves do usuário até
casar — O(n) numa função que é lenta de propósito.

SHA-256 puro seria fraco para senha, mas o segredo aqui tem 32 bytes de
`secrets.token_urlsafe`: não há dicionário que ataque isso. É o mesmo desenho usado por
provedores de API em produção — índice rápido para achar, verificador lento para
confirmar. Bancos criados antes da coluna existir são migrados automaticamente, e as
chaves antigas continuam válidas.

### Limitação: isto não autentica o chamador

A tool lê a chave de `os.getenv("GIULIA_AI_API_KEY")` — do ambiente do **próprio
servidor**, não de um parâmetro enviado pelo cliente.

Em `stdio` o servidor MCP é um processo filho do cliente: um processo, um cliente. Não
existe "outro chamador" para distinguir — a fronteira de confiança é o sistema
operacional, não o protocolo. O que este projeto entrega é **credencial bem guardada +
um gate de configuração**.

Autenticação de chamador só passa a fazer sentido com transporte HTTP, com a chave
viajando na requisição. Essa camada não está implementada aqui.

## Testes

```bash
uv run pytest        # 33 testes, contra SQLite temporário
```

Cobrem o formato da chave, o não-vazamento do segredo no arquivo do banco, o
mascaramento, a validação (incluindo chave de outro usuário), a contagem de chamadas ao
bcrypt, a migração do `lookup_hash` e a revogação.

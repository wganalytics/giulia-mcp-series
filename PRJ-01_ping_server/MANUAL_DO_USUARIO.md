# Manual do Usuário: Ping Server (MCP)

## 🎯 Visão Geral
O **Ping Server** é um pequeno servidor que atua como um "médico de conectividade" para a sua Inteligência Artificial. Ele permite que ferramentas de IA (como o Claude Desktop) descubram instantaneamente se outros computadores, servidores ou sites estão "vivos" e funcionando rapidamente.

**Benefício Principal:** Se você estiver pedindo para a IA investigar por que um site está fora do ar, ela poderá usar esta ferramenta internamente para "bater na porta" do servidor e relatar a velocidade de resposta.

## 🚀 Como Acessar

Ao contrário de sites comuns, você não acessa este sistema pelo navegador (Chrome). Ele é uma extensão que você acopla diretamente ao seu cliente de Inteligência Artificial.

1. Abra as configurações do **Claude Desktop**.
2. Adicione este servidor no seu arquivo de configuração apontando para a pasta onde ele está instalado (`src/ping_server.py`).
3. O servidor se comunicará silenciosamente por trás das cortinas usando canais de texto (stdio).

## ⚙️ Funcionalidades Principais
Quando acoplado à sua IA, ela ganha os seguintes "superpoderes":
- **Verificar Própria Saúde (`ping`):** A IA consegue saber se a ferramenta está online.
- **Teste de Conexão Real (`check_host`):** A IA consegue testar a conexão TCP com qualquer IP e porta no mundo, retornando o tempo exato (milissegundos) que levou para conectar.

## 📖 Exemplo de Uso (Pela sua IA)

Você não precisará digitar comandos difíceis, basta pedir para a sua IA (ex: Claude):

1. **Seu comando:** *"Claude, pode verificar se o servidor 1.1.1.1 está no ar?"*
2. **O que a IA faz:** Ela chama a ferramenta silenciosamente no fundo `check_host("1.1.1.1", 443)`.
3. **A Resposta:** O Claude te responderá: *"Sim, o servidor 1.1.1.1 está operante e me respondeu super rápido, em 12.3 milissegundos!"*

## ⚠️ Restrições e Limites
> [!WARNING]
> - A ferramenta de teste de latência (TCP) não substitui um monitoramento avançado de rede (como Zabbix/Datadog). Ela é apenas para verificações pontuais rápidas.
> - Se você testar uma porta que esteja protegida por firewall, a ferramenta dirá que não conseguiu conectar ou que houve "timeout" (demorou muito).

## 🛠️ Solução de Problemas (Troubleshooting)

- **A IA diz que não encontrou a ferramenta:**
  - *O que significa:* O servidor MCP não subiu junto com o Claude Desktop.
  - *Como resolver:* Verifique no arquivo `claude_desktop_config.json` se o caminho para o arquivo `src/ping_server.py` está escrito corretamente no seu computador.

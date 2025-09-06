# Carteira Automatizada com Actual Budget + Google Sheets

📂 Estrutura do Projeto
```
AQUI/
├── run_export.py          # Script principal (ETL)
├── Dockerfile             # Container otimizado
├── docker-compose.yml     # Orquestração Docker
├── entrypoint.sh          # Fluxo de execução
├── requirements.txt       # Dependências Python
├── .env.example           # Template de configuração
├── dashboard.gs           # Script Apps Script para dashboard
├── atualizador/           # Módulo de download do Actual Budget
│   ├── download-budget.js # Script Node.js para baixar dados
│   └── data/              # Base SQLite
└── .github/workflows/     # Automação GitHub Actions
```

## 📊 Visão Geral

Automatiza a extração de dados do **Actual Budget** (self-hosted + Pluggy), processa e envia para uma planilha **Google Sheets**. Dashboard interativo em **Apps Script**.

## 🚀 Passo a Passo de Configuração

Passo 0: Configurando a Fonte de Dados (Actual Budget + Pluggy)

Pré-requisito: ter o Actual Budget recebendo transações via Pluggy antes de seguir com deploy/integrações.

* Guia rápido (vídeo): [https://youtu.be/PjJ0F8GIHTs](https://youtu.be/PjJ0F8GIHTs)
* Regras de categorização automática (leia isso): [https://actualbudget.org/docs/budgeting/rules/](https://actualbudget.org/docs/budgeting/rules/)

### 1 Deploy no Fly.io

O Fly.io é a plataforma de hospedagem onde rodaremos o Actual Budget.  
➡️ **Importante:** É necessário criar uma conta e informar um cartão de crédito.  

Nossa sugestão é usar um **cartão virtual temporário** — assim você evita cobranças indesejadas, mesmo que por algum motivo estoure o limite gratuito (o que é muito improvável rodando apenas o Actual).

#### 1.1 Criar conta no Fly.io
- Acesse [fly.io](https://fly.io) e crie sua conta.
- Cadastre um cartão (pode ser virtual/temporário).  
- Dentro do limite gratuito (até ~5 USD/mês) você não terá cobrança real.

#### 1.2. Instalar o Fly CLI

**macOS / Linux:**
```bash
curl -L https://fly.io/install.sh | sh
````

**Windows (PowerShell):**

```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

#### 1.3. Login

```bash
fly auth login
```

#### 1.4. Criar a aplicação

Use a imagem oficial do Actual Budget:

```bash
fly launch --image actualbudget/actual-server:latest
```

Durante o processo, você pode definir o nome do app e a região de deploy.

#### 1.5. Acessar e configurar

Depois do deploy, abra a URL gerada no navegador.

* Defina a senha de administrador.
* Importe um orçamento existente ou crie um novo.

#### 1.6. Atualizações futuras

Quando sair uma nova versão do Actual Budget, basta rodar:

```bash
fly deploy --image actualbudget/actual-server:latest --app nome-do-app
```

#### 1.7. Economia de recursos (opcional)

Para desligar a instância automaticamente quando não estiver em uso e religar sob demanda, adicione ao `fly.toml`:

```toml
[[services]]
  auto_start_machines = true
  auto_stop_machines = true
```

Isso ajuda a manter os custos abaixo do limite de U$5

✅ Pronto! Agora você tem seu Actual Budget rodando no Fly.io com praticamente nenhum custo para uso pessoal.


### 2. Configurar o Google Cloud (Sheets + Drive)

* No Google Cloud Console, crie um projeto.
* Ative `Google Sheets API` e `Google Drive API`.
* Crie uma Conta de Serviço (APIs e Serviços > Credenciais > Conta de Serviço) e baixe o JSON.
* No JSON, copie `client_email` e compartilhe a planilha com esse e‑mail (Editor).

### 3. Configuração do projeto local / repositório

* Clone o repo e copie o `.env`:

  ```bash
  git clone https://github.com/AndreLobo1/AQUI.git
  cd AQUI
  cp .env.example .env
  ```
* Preencha `.env` com: `ACTUAL_SERVER_URL`, `ACTUAL_SYNC_ID`, `ACTUAL_PASSWORD`, `SPREADSHEET_NAME`, `GOOGLE_CREDENTIALS_FILE`.
* Coloque o JSON das credenciais na raiz e renomeie para o nome definido em `GOOGLE_CREDENTIALS_FILE`.

### 4. Automação com GitHub Actions (recomendado)

* Gere a string Base64 da sua credencial JSON (não envie o JSON cru):

  ```bash
  base64 credenciais.json > credenciais.b64
  cat credenciais.b64
  ```

  Copie o conteúdo gerado.
* No GitHub: Settings > Secrets and variables > Actions. Crie:

  * `DOT_ENV_FILE` (valor = conteúdo do `.env`)
  * `GOOGLE_CREDENTIALS_JSON` (valor = conteúdo Base64 do JSON)
* Confira `.github/workflows/sync.yml` para ajustar horário (cron).

### 5. Dashboard no Google Sheets (Apps Script)

* Abra a planilha, Extensões > Apps Script.
* Cole o conteúdo de `dashboard.gs` (do repositório).
* Se o editor pedir, ative também a API do Google Drive.
* Salve, autorize as permissões e recarregue a planilha.
* Use o menu `📊 Dashboard > Atualizar Tela`.

### 6 . Executar localmente (opcional)

Use esta seção apenas se quiser testar/desenvolver sem deploy no Fly. Não é obrigatório quando o Actual já está no Fly.

* Build da imagem:

  ```bash
  docker-compose build --no-cache
  ```
* Executar uma sincronização manual:

  ```bash
  docker-compose run --rm carteira
  ```

### Custos (resumo rápido)

- **Pluggy:** apesar do site falar em 14 dias grátis, para uso pessoal a API é gratuita por tempo indeterminado.

- **Fly.io:** a hospedagem é gratuita enquanto o consumo não ultrapassar US$5/mês. Rodando apenas o Actual Budget dificilmente você chegará perto desse limite.

- **Google Apps Script:** totalmente gratuito para automações simples como o dashboard.

- **GitHub Actions:** gratuito em repositórios públicos. Mesmo em privados, o fluxo diário deste projeto não gera custo.

Ou seja: todo o sistema roda sem custos para uso pessoal.

# Carteira Automatizada com Actual Budget e Google Sheets

## 📊 Visão Geral

Este projeto automatiza a extração de dados financeiros do **Actual Budget** (aplicativo de gestão financeira baseado em Open Finance), processa-os e os carrega automaticamente em uma planilha do **Google Sheets** para análise e visualização. O sistema resolve o problema de sincronização manual entre diferentes plataformas financeiras, automatizando o processo de extração, transformação e carregamento (ETL) de dados financeiros.

## ✨ Funcionalidades

- **🔄 Sincronização Automática**: Conecta-se ao Actual Budget e baixa os dados mais recentes
- **📊 Categorização de Transações**: Extrai e organiza transações por categoria
- **🎨 Formatação Condicional**: Aplica cores automáticas baseadas nos valores (verde para positivos, vermelho para negativos)
- **📋 Separação Inteligente**: Divide transações em "Válidas" e "Excluídas" (como saldos iniciais)
- **💰 Cálculo de Saldos**: Calcula e exibe saldos atuais de todas as contas
- **🔒 Segurança**: Usa variáveis de ambiente para proteger credenciais
- **🐳 Containerização**: Executa em ambiente Docker isolado e portável
- **🤖 Automação**: GitHub Actions para execução diária automática

## ⚙️ Arquitetura e Fluxo de Dados

```
Actual Budget (Self-Hosted) 
    ↓ (API Sync)
Container Docker (Node.js + Python)
    ↓ (Processamento ETL)
Google Sheets API
    ↓ (Carregamento)
Planilha Google Sheets (3 abas: Transações, Excluídas, Saldos)
```

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:

- **Docker e Docker Compose** - Para executar o projeto em containers
- **Git** - Para clonar o repositório
- **Uma instância do Actual Budget auto-hospedada** - Funcionando e acessível
- **Uma Conta Google** - Para criar credenciais da API e planilha

## 🚀 Guia de Instalação e Configuração

### Passo 0: Configurando a Fonte de Dados (Actual Budget + Pluggy)

**Pré-requisito principal:** Você precisa ter o Actual Budget funcionando e recebendo dados via Pluggy.

Para configurar sua instância do Actual Budget no Fly.io e conectá-la aos seus bancos com o Pluggy, siga o excelente guia em vídeo disponível em: **https://youtu.be/PjJ0F8GIHTs**

Após concluir os passos do vídeo e ter seu Actual recebendo as transações, retorne a este guia.

### 1. Clone o Repositório

```bash
git clone https://github.com/AndreLobo1/AQUI.git
cd AQUI
```

### 2. Configure o Actual Budget

Você precisará de duas informações do seu Actual Budget:

- **URL do servidor**: A URL onde seu Actual Budget está hospedado
- **Sync ID**: Encontre em `Configurações` > `Configurações Avançadas` > `Sync ID`

> 💡 **Dica**: O Sync ID é único para cada orçamento e é necessário para sincronizar os dados.

### 3. Obtenha as Credenciais da API do Google (Passo a Passo)

Este é o processo mais complexo, mas seguindo os passos abaixo você conseguirá:

#### 3.1. Acesse o Google Cloud Console
1. Vá para [Google Cloud Console](https://console.cloud.google.com/)
2. Faça login com sua conta Google

#### 3.2. Crie um Novo Projeto
1. Clique no seletor de projeto no topo
2. Clique em "Novo Projeto"
3. Dê um nome (ex: "Automação Planilhas")
4. Clique em "Criar"

#### 3.3. Crie uma Conta de Serviço
1. No menu lateral, vá para `APIs e Serviços` > `Credenciais`
2. Clique em `Criar Credenciais` > `Conta de Serviço`
3. Dê um nome (ex: "planilhas-automator")
4. Clique em `Criar e Continuar`
5. Pule as permissões (clique em `Continuar`)
6. Clique em `Concluído`

#### 3.4. Baixe a Chave JSON
1. Na lista de contas de serviço, clique na que você criou
2. Vá para a aba `Chaves`
3. Clique em `Adicionar Chave` > `Criar nova chave`
4. Selecione `JSON` e clique em `Criar`
5. **Salve o arquivo JSON** em local seguro

#### 3.5. Ative as APIs Necessárias
1. Vá para `APIs e Serviços` > `Biblioteca`
2. Procure por "Google Drive API" e clique em `Ativar`
3. Procure por "Google Sheets API" e clique em `Ativar`

#### 3.6. Configure Permissões na Planilha
1. **Abra o arquivo JSON** que você baixou
2. Encontre o campo `client_email` (algo como `...@...gserviceaccount.com`)
3. **Crie uma planilha** no Google Sheets ou use uma existente
4. **Compartilhe a planilha** com o e-mail da conta de serviço
5. **Dê permissão de Editor** para a conta de serviço

> ⚠️ **Importante**: Sem este passo, o script não conseguirá acessar sua planilha!

### 4. Configure as Variáveis de Ambiente

#### 4.1. Crie o Arquivo de Configuração
```bash
cp .env.example .env
```

#### 4.2. Coloque o Arquivo de Credenciais
- Coloque o arquivo `.json` que você baixou na **pasta raiz** do projeto
- Renomeie-o para algo simples (ex: `minhas-credenciais.json`)

#### 4.3. Configure as Variáveis
Abra o arquivo `.env` e preencha com suas informações:

```env
# ========================================
# CONFIGURAÇÕES DO ACTUAL BUDGET
# ========================================
ACTUAL_SERVER_URL=https://seu-actual.exemplo.com
ACTUAL_SYNC_ID=seu-sync-id-aqui
ACTUAL_PASSWORD=sua-senha-aqui

# ========================================
# CONFIGURAÇÕES DO GOOGLE SHEETS
# ========================================
SPREADSHEET_NAME=Minha Carteira
GOOGLE_CREDENTIALS_FILE=minhas-credenciais.json

# ========================================
# CONFIGURAÇÕES DO BANCO DE DADOS
# ========================================
SQLITE_DB_PATH=atualizador/data/My-Finances-2873fb3/db.sqlite
DATABASE_URL=sqlite:///app/data/budget.sqlite

# ========================================
# CONFIGURAÇÕES DE EXPORTAÇÃO
# ========================================
EXPORT_FORMAT=json
EXPORT_PATH=/app/exports
```

> 🔒 **Segurança**: O arquivo `.env` não será commitado no Git, mantendo suas credenciais seguras.

## ▶️ Como Executar

### Construir a Imagem Docker
```bash
docker-compose build --no-cache
```
> Este comando constrói a imagem Docker do zero, instalando todas as dependências.

### Executar o Processo de Sincronização
```bash
docker-compose run --rm carteira
```
> Este comando executa o processo completo: baixa dados do Actual Budget e atualiza a planilha.

### Executar em Background (Opcional)
```bash
docker-compose up -d carteira
```
> Para executar em background (modo detached) e ver logs com `docker-compose logs -f carteira`

## 🤖 Automação com GitHub Actions (Faça o script rodar sozinho)

Esta é a maneira **recomendada** de automatizar o projeto para que ele rode diariamente na nuvem, **de graça**.

### Passo A: Configurando os Segredos no GitHub

As credenciais devem ser salvas nos "Secrets" do repositório:

1. **Vá em:** Settings > Secrets and variables > Actions
2. **Clique:** "New repository secret"
3. **Crie os dois segredos:**

**Secret `DOT_ENV_FILE`:**
- **Nome:** `DOT_ENV_FILE`
- **Valor:** Conteúdo completo do seu arquivo `.env`

**Secret `GOOGLE_CREDENTIALS_JSON`:**
- **Nome:** `GOOGLE_CREDENTIALS_JSON`
- **Valor:** String Base64 do seu arquivo JSON (veja Passo B)

### Passo B: A Importância de Codificar suas Credenciais (Base64)

**Por que isso é necessário:** Para evitar erros de formatação ao copiar e colar o conteúdo do arquivo `.json` (um problema que enfrentamos e resolvemos).

**Como fazer:**
1. **Vá para:** https://www.base64encode.org/
2. **Faça upload** do seu arquivo `.json` de credenciais
3. **Copie** a string Base64 de linha única resultante
4. **Cole** no valor do segredo `GOOGLE_CREDENTIALS_JSON`

### Passo C: Personalizando o Horário da Execução

O agendamento está definido no arquivo `.github/workflows/sync.yml`:

```yaml
schedule:
  - cron: '0 8 * * *'  # 8h da manhã no horário UTC
```

**O que significa:**
- `0 8 * * *` = Todos os dias às 8h UTC (5h da manhã no horário de Brasília)
- Para personalizar, use: https://crontab.guru/

### Passo D: Ativando e Monitorando

**Após enviar o arquivo `.yml` para o repositório:**
- ✅ A automação já estará ativa
- ✅ Execução diária automática às 8h UTC
- ✅ Execução manual disponível na aba "Actions"

**Notificações:**
- 📧 O GitHub envia e-mail automático ao dono do repositório
- ✅ Sucesso: "Sincronização executada com sucesso!"
- ❌ Falha: "Sincronização falhou!" com logs detalhados

## 📊 Criando o Dashboard Interativo (Google Apps Script)

O arquivo `dashboard.gs` no repositório contém um script para criar um painel dinâmico na planilha, permitindo análises avançadas e visualizações interativas dos seus dados financeiros.

### Instalando o Script do Dashboard

**Passo a Passo:**

1. **Abra sua Planilha Google Sheets**
   - Acesse a planilha onde os dados estão sendo sincronizados

2. **Acesse o Apps Script**
   - No menu superior, clique em **Extensões** > **Apps Script**

3. **Limpe o Editor**
   - Apague todo o código de exemplo que estiver no editor

4. **Cole o Script**
   - Abra o arquivo `dashboard.gs` do nosso repositório
   - Copie **todo o conteúdo** do arquivo
   - Cole no editor do Apps Script

5. **Salve o Projeto**
   - Clique em **Salvar** (ou Ctrl+S)
   - Dê um nome ao projeto (ex: "Dashboard Financeiro")

6. **Recarregue a Planilha**
   - Volte para a planilha e recarregue a página
   - Um novo menu **📊 Dashboard** aparecerá na barra superior

### Funcionalidades do Dashboard

Após a instalação, você terá acesso a:
- **Gráficos dinâmicos** baseados nos dados das transações
- **Filtros avançados** por período, categoria e conta
- **Análises de tendências** e gastos por mês
- **Relatórios personalizados** com exportação

## 📂 Estrutura do Projeto

```
AQUI/
├── 📄 run_export.py              # Script principal Python (unificado)
├── 🐳 Dockerfile                 # Configuração do container otimizado
├── 🐳 docker-compose.yml         # Orquestração dos serviços
├── 🚀 entrypoint.sh              # Script de inicialização do container
├── 📋 requirements.txt           # Dependências Python
├── 🔧 .env.example               # Template de variáveis de ambiente
├── 📄 dashboard.gs               # Script Google Apps Script para dashboard
├── 📁 atualizador/               # Módulo de download do Actual Budget
│   ├── 📄 download-budget.js     # Script Node.js para baixar dados
│   ├── 📄 package.json           # Dependências Node.js
│   └── 📁 data/                  # Dados baixados (SQLite)
├── 📁 .github/workflows/         # Automação GitHub Actions
│   └── 📄 sync.yml               # Workflow de sincronização automática
└── 📄 README.md                  # Este arquivo
```

### Principais Arquivos:

- **`run_export.py`**: Script Python unificado que processa dados e atualiza a planilha
- **`Dockerfile`**: Configuração otimizada com multi-stage build para imagem menor
- **`docker-compose.yml`**: Define o serviço e carrega variáveis de ambiente
- **`entrypoint.sh`**: Orquestra a execução: primeiro baixa dados, depois processa
- **`atualizador/download-budget.js`**: Conecta ao Actual Budget e baixa os dados
- **`.github/workflows/sync.yml`**: Automação diária com GitHub Actions
- **`dashboard.gs`**: Script Google Apps Script para criar dashboard interativo

## 🔧 Troubleshooting

### Erro: "Cannot find module '@actual-app/api'"
- Execute `docker-compose build --no-cache` para reconstruir a imagem

### Erro: "Planilha não encontrada"
- Verifique se o nome da planilha no `.env` está correto
- Confirme se a planilha foi compartilhada com a conta de serviço

### Erro: "Credenciais inválidas"
- Verifique se o arquivo JSON está na pasta raiz
- Confirme se o nome do arquivo no `.env` está correto
- Verifique se as APIs (Drive e Sheets) estão ativadas

### Erro: "Sync ID inválido"
- Confirme o Sync ID nas configurações do Actual Budget
- Verifique se a URL do servidor está correta

### Erro: "docker-compose: command not found"
- Use `docker compose` (com espaço) em vez de `docker-compose` (com hífen)
- Os runners modernos do GitHub Actions usam a sintaxe nova

### Erro: "Invalid JWT Signature"
- Verifique se as credenciais não expiraram
- Regenere o arquivo JSON no Google Cloud Console
- Use codificação Base64 para evitar problemas de formatação



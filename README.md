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

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/carteira-automatizada.git
cd carteira-automatizada
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
# Variáveis de Ambiente para o Projeto Carteira

# Nome do seu arquivo de credenciais do Google (sem .json)
GOOGLE_CREDENTIALS_FILE=minhas-credenciais.json

# Caminho para o banco de dados SQLite (geralmente não precisa mudar)
SQLITE_DB_PATH=atualizador/data/My-Finances-2873fb3/db.sqlite

# Nome exato da sua Planilha no Google Sheets
SPREADSHEET_NAME=Minha Carteira

# URL do seu servidor Actual Budget
ACTUAL_SERVER_URL=https://meu-actual.exemplo.com

# Sync ID do seu orçamento (encontre nas configurações do Actual)
ACTUAL_SYNC_ID=seu-sync-id-aqui

# Senha do seu orçamento (se tiver)
ACTUAL_PASSWORD=sua-senha-aqui
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
> Para executar em background e ver logs com `docker-compose logs -f carteira`

## 📂 Estrutura do Projeto

```
carteira-automatizada/
├── 📄 run_export.py              # Script principal Python (unificado)
├── 🐳 Dockerfile                 # Configuração do container otimizado
├── 🐳 docker-compose.yml         # Orquestração dos serviços
├── 🚀 entrypoint.sh              # Script de inicialização do container
├── 📋 requirements.txt           # Dependências Python
├── 🔧 .env.example               # Template de variáveis de ambiente
├── 📁 atualizador/               # Módulo de download do Actual Budget
│   ├── 📄 download-budget.js     # Script Node.js para baixar dados
│   ├── 📄 package.json           # Dependências Node.js
│   └── 📁 data/                  # Dados baixados (SQLite)
└── 📄 README.md                  # Este arquivo
```

### Principais Arquivos:

- **`run_export.py`**: Script Python unificado que processa dados e atualiza a planilha
- **`Dockerfile`**: Configuração otimizada com multi-stage build para imagem menor
- **`docker-compose.yml`**: Define o serviço e carrega variáveis de ambiente
- **`entrypoint.sh`**: Orquestra a execução: primeiro baixa dados, depois processa
- **`atualizador/download-budget.js`**: Conecta ao Actual Budget e baixa os dados

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

## 📈 Próximos Passos

Após a primeira execução bem-sucedida, você pode:

- **Automatizar execuções**: Configure um cron job ou GitHub Actions
- **Personalizar formatação**: Modifique cores e estilos no `run_export.py`
- **Adicionar filtros**: Implemente filtros personalizados para transações
- **Dashboard**: Crie gráficos e análises na planilha
# Documentação Técnica - Sistema de Automação de Orçamento Pessoal

## 1. Visão Geral do Projeto

Este projeto é um sistema de automação de orçamento pessoal que integra dados financeiros do **Actual Budget** (aplicativo de gestão financeira baseado em Open Finance) com **Google Sheets** para visualização e análise. O sistema resolve o problema de sincronização manual entre diferentes plataformas financeiras, automatizando o processo de extração, transformação e carregamento (ETL) de dados financeiros.

O projeto utiliza uma arquitetura containerizada com **Docker** para garantir portabilidade e consistência entre ambientes, combinando tecnologias **Node.js** (para download de dados via API do Actual Budget) e **Python** (para processamento e exportação para Google Sheets). A integração com **Google Sheets API** permite a criação de dashboards automatizados com formatação avançada, cores condicionais e filtros dinâmicos.

**Principais tecnologias utilizadas:**
- **Docker & Docker Compose** - Containerização e orquestração
- **Node.js** - Download de dados via Actual Budget API
- **Python 3** - Processamento de dados e integração com Google Sheets
- **SQLite** - Armazenamento local de dados financeiros
- **Google Sheets API** - Visualização e dashboard
- **Actual Budget API** - Fonte de dados financeiros

## 2. Arquitetura e Fluxo de Dados

O fluxo de dados segue uma arquitetura ETL (Extract, Transform, Load) com as seguintes etapas:

### Passo a Passo do Fluxo de Dados:

1. **Extração (Extract)**
   - O script Node.js `download-budget.js` conecta-se ao servidor Actual Budget em `https://carteiraflyio.fly.dev`
   - Utiliza o Sync ID `4f676946-1eb8-4174-8499-a23502230680` para baixar o orçamento completo
   - Os dados são salvos localmente em SQLite no diretório `atualizador/data/My-Finances-2873fb3/`

2. **Transformação (Transform)**
   - O script Python `export_actual_to_sheets.py` conecta-se ao banco SQLite local
   - Executa queries SQL para extrair transações, categorias e contas
   - Aplica formatação de datas (YYYYMMDD → DD/MM/YYYY)
   - Converte valores de centavos para reais (÷100)
   - Separa transações válidas das excluídas (sem categoria ou "starting balances")
   - Calcula saldos por conta considerando tipos diferentes (credit, checking, savings)

3. **Carregamento (Load)**
   - Autentica-se no Google Sheets usando credenciais de service account
   - Cria/atualiza três abas na planilha "Carteira":
     - **Transações**: Dados válidos com formatação avançada
     - **Excluídas**: Transações sem categoria ou saldos iniciais
     - **Saldos**: Resumo de saldos por conta
   - Aplica formatação condicional com cores baseadas em valores
   - Configura filtros automáticos e congela cabeçalhos

4. **Processamento Adicional**
   - O script `export_balance.py` executa cálculo adicional de saldos
   - Atualiza especificamente a aba "Saldos" com informações detalhadas por tipo de conta

## 3. Estrutura de Pastas e Arquivos

```
CarteiraFlyIo/
├── atualizador/                    # Componente Node.js para download
│   ├── data/                      # Dados SQLite baixados
│   │   └── My-Finances-2873fb3/   # Diretório específico do orçamento
│   │       ├── db.sqlite          # Banco principal com transações
│   │       ├── cache.sqlite       # Cache de sincronização
│   │       └── metadata.json      # Metadados do orçamento
│   ├── download-budget.js         # Script principal de download
│   ├── package.json               # Dependências Node.js
│   └── node_modules/              # Dependências instaladas
├── venv/                          # Ambiente virtual Python (Windows)
├── Dockerfile                     # Configuração da imagem Docker
├── docker-compose.yml             # Orquestração de containers
├── entrypoint.sh                  # Script de inicialização do container
├── requirements.txt               # Dependências Python
├── export_actual_to_sheets.py     # Script principal de exportação
├── export_balance.py              # Script de cálculo de saldos
├── carteira-463704-*.json         # Credenciais Google Service Account
├── minhacarteira-464217-*.json    # Credenciais alternativas
├── atualizar-orcamento.bat        # Script legado Windows
└── fly.toml                       # Configuração de deploy Fly.io
```

### Descrição dos Arquivos Relevantes:

- **`/Dockerfile`**: Define a imagem base (Node 20 + Debian), instala Python 3 e dependências, configura o ambiente de execução
- **`/docker-compose.yml`**: Orquestra o serviço `carteira` com volumes para persistência e cache de node_modules
- **`/entrypoint.sh`**: Script bash que executa a sequência completa: download → exportação → cálculo de saldos
- **`/requirements.txt`**: Lista dependências Python (gspread, oauth2client, pandas, google-api-python-client)
- **`/export_actual_to_sheets.py`**: Script principal que processa dados SQLite e exporta para Google Sheets com formatação avançada
- **`/export_balance.py`**: Script complementar que calcula e atualiza saldos detalhados por tipo de conta
- **`/atualizador/download-budget.js`**: Script Node.js que baixa dados do Actual Budget via API usando @actual-app/api
- **`/carteira-xxxxxxxx.json`**: Arquivos de credenciais do Google Service Account para autenticação na API do Google Sheets

## 4. Análise Detalhada dos Componentes

### 4.1. Ambiente de Container (Docker)

#### **`Dockerfile`**
- **`FROM node:20-bullseye`**: Imagem base com Node.js 20 e Debian Bullseye
- **`RUN apt-get update && apt-get install -y python3 python3-pip sqlite3`**: Instala Python 3, pip3 e SQLite3 no container
- **`WORKDIR /app`**: Define `/app` como diretório de trabalho
- **`COPY atualizador/package*.json ./atualizador/`**: Copia arquivos de dependências Node.js
- **`RUN cd atualizador && npm install`**: Instala dependências Node.js (@actual-app/api)
- **`COPY requirements.txt ./`**: Copia arquivo de dependências Python
- **`RUN pip3 install --no-cache-dir -r requirements.txt`**: Instala bibliotecas Python (gspread, oauth2client, etc.)
- **`COPY . .`**: Copia todo o projeto para o container
- **`RUN chmod +x /app/entrypoint.sh`**: Dá permissão de execução ao script de entrada
- **`ENTRYPOINT ["/app/entrypoint.sh"]`**: Define o script que será executado ao iniciar o container

#### **`docker-compose.yml`**
- **Serviço `carteira`**: Define o container principal
- **`build: .`**: Constrói a imagem usando o Dockerfile local
- **`volumes`**:
  - `./:/app`: Monta o diretório atual no container (desenvolvimento)
  - `node_modules_cache:/app/atualizador/node_modules`: Cache persistente para node_modules (performance)
- **`working_dir: /app`**: Define diretório de trabalho
- **`stdin_open: true` e `tty: true`**: Permite interação com o container

### 4.2. Orquestração

#### **`entrypoint.sh`**
O script executa a sequência exata de comandos na seguinte ordem:

1. **`cd /app/atualizador`**: Navega para diretório do componente Node.js
2. **`node download-budget.js`**: Baixa dados do Actual Budget via API
3. **`cd /app`**: Retorna ao diretório raiz
4. **`python3 export_actual_to_sheets.py`**: Processa e exporta dados principais
5. **`python3 export_balance.py`**: Calcula e atualiza saldos detalhados

**Por que essa ordem é importante:**
- O download deve acontecer primeiro para garantir dados atualizados
- A exportação principal deve ocorrer antes do cálculo de saldos
- Cada script depende dos dados processados pelo anterior

### 4.3. Scripts de Extração e Carga (Python)

#### **`export_actual_to_sheets.py`**

**Principal responsabilidade:** Processar dados financeiros do SQLite e exportar para Google Sheets com formatação avançada.

**Conexão com SQLite:**
```python
conn = sqlite3.connect("atualizador/data/My-Finances-2873fb3/db.sqlite")
```
Utiliza a view `v_transactions` que já faz JOIN entre transações, categorias e contas.

**Processamento e limpeza de dados:**
- **Formatação de datas**: Converte YYYYMMDD para DD/MM/YYYY
- **Conversão de valores**: Divide por 100 para converter centavos em reais
- **Tratamento de categorias**: Substitui valores nulos por "Sem Categoria"
- **Separação de dados**: Filtra transações válidas das excluídas (sem categoria ou "starting balances")

**Lógica de formatação avançada:**
- **Cores condicionais**: Escala de verde/vermelho baseada em valores (6 níveis de intensidade)
- **Formatação monetária**: Padrão brasileiro com separadores de milhares
- **Congelamento de painéis**: Primeira linha sempre visível
- **Filtros automáticos**: Aplicados na área de dados
- **Auto-redimensionamento**: Colunas ajustadas automaticamente
- **Remoção de abas antigas**: Limpa "Página1" e "Dashboard" automaticamente

#### **`export_balance.py`**

**Por que existe separadamente:** Foca especificamente no cálculo preciso de saldos por tipo de conta, aplicando regras de negócio específicas para diferentes tipos de contas financeiras.

**Cálculo de saldos por tipo de conta:**
- **Contas de crédito/cheque/poupança** (`credit`, `checking`, `savings`): Aplica sinal negativo às transações (saídas = saldo negativo)
- **Outras contas** (investimentos): Mantém valor bruto das transações
- **Fórmula aplicada**: `SUM(amount)` com sinal baseado no tipo da conta

**Aba alimentada:** Atualiza especificamente a aba "Saldos" com colunas:
- Nome da Conta
- Tipo da Conta  
- Saldo Atual (formatado em reais brasileiros)

## 5. Como Executar o Projeto

### Pré-requisitos:
- **Docker** e **Docker Compose** instalados
- Arquivo de credenciais do Google Service Account (`carteira-463704-*.json`) no diretório raiz
- Acesso à internet para download de dados e upload para Google Sheets
- Planilha "Carteira" criada no Google Sheets com permissões para o service account

### Comandos para Execução:

#### **1. Construir a imagem Docker:**
```bash
docker-compose build --no-cache
```
**O que faz:** Reconstrói a imagem Docker do zero, ignorando cache, garantindo que todas as dependências sejam instaladas corretamente.

#### **2. Executar o processo completo:**
```bash
docker-compose run --rm carteira
```
**O que faz:** 
- Executa o container `carteira` uma única vez
- Remove o container automaticamente após execução (`--rm`)
- Executa toda a sequência: download → processamento → exportação
- Mostra logs em tempo real do processo

#### **3. Executar em modo interativo (desenvolvimento):**
```bash
docker-compose run --rm carteira bash
```
**O que faz:** Abre um shell bash dentro do container para debug e desenvolvimento.

## 6. Análise do Script Legado (Windows)

#### **`atualizar-orcamento.bat`**

**Processo anterior à dockerização:**
1. Navegava para diretório `atualizador` e executava `node download-budget.js`
2. Ativava ambiente virtual Python local (`.venv\Scripts\activate.bat`)
3. Instalava dependências Python manualmente via pip
4. Executava scripts Python sequencialmente

**Vantagens da migração para Docker:**
- **Portabilidade**: Funciona em qualquer sistema operacional com Docker
- **Isolamento**: Ambiente completamente isolado, sem conflitos de dependências
- **Consistência**: Mesmo ambiente em desenvolvimento e produção
- **Facilidade de deploy**: Pode ser executado em qualquer servidor com Docker
- **Versionamento**: Imagem Docker versionada garante reprodutibilidade
- **Escalabilidade**: Fácil orquestração com Docker Compose
- **Manutenção**: Não requer instalação manual de dependências no sistema host
- **Backup**: Estado do container pode ser versionado e replicado

A dockerização transformou um processo manual e dependente do ambiente Windows em uma solução robusta, portável e facilmente automatizável.

---

**Nota para Desenvolvedores:** Este sistema foi projetado para ser executado de forma autônoma, ideal para automação via cron jobs ou CI/CD pipelines. A arquitetura modular permite fácil manutenção e extensão de funcionalidades.

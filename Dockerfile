# ========================================
# ESTÁGIO 1: BUILDER - Ferramentas de Build
# ========================================
FROM python:3.11-slim-bullseye AS builder

# Instala dependências do sistema necessárias para build
RUN apt-get update && apt-get install -y \
    curl \
    sqlite3 \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos de dependências primeiro (otimiza cache de camadas)
COPY atualizador/package*.json ./atualizador/
COPY requirements.txt ./

# Instala dependências Node.js
RUN cd atualizador && npm ci --only=production

# Instala dependências Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY atualizador/ ./atualizador/
COPY run_export.py ./
COPY entrypoint.sh ./

# Dá permissão de execução para o entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# ========================================
# ESTÁGIO 2: FINAL - Imagem de Produção
# ========================================
FROM python:3.11-slim-bullseye AS final

# Instala dependências necessárias para a aplicação
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Define diretório de trabalho
WORKDIR /app

# Cria diretórios necessários
RUN mkdir -p /app/data /app/exports

# Copia apenas os artefatos necessários do estágio builder
COPY --from=builder /app/atualizador/node_modules ./atualizador/node_modules
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app/atualizador/ ./atualizador/
COPY --from=builder /app/run_export.py ./
COPY --from=builder /app/entrypoint.sh ./

# Define entrypoint do container
ENTRYPOINT ["/app/entrypoint.sh"]

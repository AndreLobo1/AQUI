#!/bin/bash
set -e

echo "[+] Iniciando atualização do orçamento..."

# 1. Baixar dados via Node.js
cd /app/atualizador
node download-budget.js

# 2. Executar script Python unificado
cd /app
python3 run_export.py

echo "✅ Processo finalizado com sucesso!"

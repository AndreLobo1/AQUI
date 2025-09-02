#!/usr/bin/env python3
"""
Script de verificação do ambiente
"""
import os
import json
import sqlite3

def test_environment():
    print("🔍 Verificando ambiente...")
    
    # Verificar arquivo .env
    if os.path.exists('.env'):
        print("✅ Arquivo .env encontrado")
    else:
        print("❌ Arquivo .env não encontrado")
    
    # Verificar arquivo de credenciais
    cred_file = 'carteira-463704-17648b3647e8.json'
    if os.path.exists(cred_file):
        print(f"✅ Arquivo de credenciais encontrado: {cred_file}")
        try:
            with open(cred_file, 'r') as f:
                data = json.load(f)
                print(f"✅ JSON válido - project_id: {data.get('project_id', 'N/A')}")
        except Exception as e:
            print(f"❌ Erro ao ler JSON: {e}")
    else:
        print(f"❌ Arquivo de credenciais não encontrado: {cred_file}")
    
    # Verificar diretório data
    if os.path.exists('data'):
        print("✅ Diretório data encontrado")
        files = os.listdir('data')
        if files:
            print(f"📁 Arquivos em data: {files}")
        else:
            print("📁 Diretório data está vazio")
    else:
        print("❌ Diretório data não encontrado")
    
    # Verificar diretório atualizador/data
    if os.path.exists('atualizador/data'):
        print("✅ Diretório atualizador/data encontrado")
        for root, dirs, files in os.walk('atualizador/data'):
            for file in files:
                print(f"📄 {os.path.join(root, file)}")
    else:
        print("❌ Diretório atualizador/data não encontrado")

if __name__ == "__main__":
    test_environment()

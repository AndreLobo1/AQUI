import sqlite3
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import *
from dotenv import load_dotenv
import time

# Carrega variáveis de ambiente
load_dotenv()

# Configurações
SPREADSHEET_NAME = os.getenv('SPREADSHEET_NAME', 'Carteira')
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'carteira-463704-17648b3647e8.json')
SQLITE_DB = os.getenv('SQLITE_DB_PATH', 'atualizador/data/My-Finances-2873fb3/db.sqlite')

# Cabeçalhos
cabecalho_transacoes = ["DATA", "CONTA", "CATEGORIA", "VALOR (R$)", "NOTAS"]
cabecalho_excluidas = ["DATA", "CONTA", "CATEGORIA", "VALOR (R$)", "NOTAS"]
cabecalho_saldos = ["CONTA", "SALDO ATUAL (R$)"]

# Cores para formatação condicional
VERDE_CLARO = Color(0.8, 1, 0.8)      # Valores positivos pequenos
VERDE_MEDIO = Color(0.6, 0.9, 0.6)    # Valores positivos médios
VERDE_FORTE = Color(0.4, 0.8, 0.4)    # Valores positivos grandes
VERMELHO_CLARO = Color(1, 0.8, 0.8)   # Valores negativos pequenos
VERMELHO_MEDIO = Color(1, 0.6, 0.6)   # Valores negativos médios
VERMELHO_FORTE = Color(1, 0.4, 0.4)   # Valores negativos grandes

def formatar_data(data_str):
    """Formata data de YYYYMMDD para DD/MM/YYYY"""
    if not data_str or len(str(data_str).strip()) != 8:
        return "---"
    try:
        data_str = str(data_str)
        return f"{data_str[6:8]}/{data_str[4:6]}/{data_str[0:4]}"
    except:
        return "---"

def ler_transacoes():
    """Lê transações do banco SQLite"""
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            t.date,
            c.name AS categoria,
            a.name AS conta,
            t.amount,
            t.notes
        FROM v_transactions t
        LEFT JOIN categories c ON c.id = t.category AND c.tombstone = 0
        LEFT JOIN accounts a ON a.id = t.account AND a.tombstone = 0
        WHERE t.tombstone = 0
        ORDER BY t.date DESC
    """)
    dados = cursor.fetchall()
    conn.close()
    return dados

def ler_saldos():
    """Lê saldos das contas do banco SQLite"""
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            a.name,
            SUM(CASE WHEN a.type IN ('credit', 'checking', 'savings') THEN -t.amount ELSE t.amount END)/100.0
        FROM accounts a
        LEFT JOIN transactions t ON t.acct = a.id AND t.tombstone = 0
        WHERE a.tombstone = 0 AND a.closed = 0
        GROUP BY a.id
    """)
    saldos = cursor.fetchall()
    conn.close()
    return saldos

def preparar_dados_planilha(dados):
    """Prepara dados para envio à planilha"""
    return [[str(item) if not isinstance(item, (int, float)) else float(item) for item in linha] for linha in dados]

def remover_filtros(worksheet):
    """Remove todos os filtros da planilha"""
    try:
        worksheet.clear_basic_filter()
    except Exception as e:
        print(f"⚠️ Não foi possível remover filtros: {str(e)}")

def limpar_colunas_extras(worksheet, num_colunas_dados):
    """Remove formatação das colunas extras, mas não as deleta"""
    if worksheet.col_count > num_colunas_dados:
        format_cell_range(worksheet, 
                        f'{chr(65 + num_colunas_dados)}1:{chr(90)}1000',
                        CellFormat(
                            backgroundColor=Color(1, 1, 1),
                            textFormat=TextFormat()
                        ))

def aplicar_escala_cores_valor(worksheet, coluna, num_linhas):
    """Aplica escala de cores variando a intensidade com o valor"""
    if num_linhas == 0:
        return
        
    rules = get_conditional_format_rules(worksheet)
    rules.clear()
    
    intervalo = f"{coluna}2:{coluna}{num_linhas+1}"
    
    rules.append(ConditionalFormatRule(
        ranges=[GridRange.from_a1_range(intervalo, worksheet)],
        booleanRule=BooleanRule(
            condition=BooleanCondition('NUMBER_GREATER_THAN_EQ', ['1000']),
            format=CellFormat(backgroundColor=VERDE_FORTE)
    )))
    
    rules.append(ConditionalFormatRule(
        ranges=[GridRange.from_a1_range(intervalo, worksheet)],
        booleanRule=BooleanRule(
            condition=BooleanCondition('NUMBER_GREATER_THAN_EQ', ['500']),
            format=CellFormat(backgroundColor=VERDE_MEDIO)
    )))
    
    rules.append(ConditionalFormatRule(
        ranges=[GridRange.from_a1_range(intervalo, worksheet)],
        booleanRule=BooleanRule(
            condition=BooleanCondition('NUMBER_GREATER', ['0']),
            format=CellFormat(backgroundColor=VERDE_CLARO)
    )))
    
    rules.append(ConditionalFormatRule(
        ranges=[GridRange.from_a1_range(intervalo, worksheet)],
        booleanRule=BooleanRule(
            condition=BooleanCondition('NUMBER_LESS', ['-1000']),
            format=CellFormat(backgroundColor=VERMELHO_FORTE)
    )))
    
    rules.append(ConditionalFormatRule(
        ranges=[GridRange.from_a1_range(intervalo, worksheet)],
        booleanRule=BooleanRule(
            condition=BooleanCondition('NUMBER_LESS', ['-500']),
            format=CellFormat(backgroundColor=VERMELHO_MEDIO)
    )))
    
    rules.append(ConditionalFormatRule(
        ranges=[GridRange.from_a1_range(intervalo, worksheet)],
        booleanRule=BooleanRule(
            condition=BooleanCondition('NUMBER_LESS', ['0']),
            format=CellFormat(backgroundColor=VERMELHO_CLARO)
    )))
    
    rules.save()

def aplicar_escala_cores_valor_simples(worksheet, coluna, num_linhas):
    """Aplica cores simples: verde para positivo, vermelho para negativo"""
    if num_linhas == 0:
        return

    rules = get_conditional_format_rules(worksheet)
    rules.clear()

    intervalo = f"{coluna}2:{coluna}{num_linhas+1}"

    # Verde para valores > 0
    rules.append(ConditionalFormatRule(
        ranges=[GridRange.from_a1_range(intervalo, worksheet)],
        booleanRule=BooleanRule(
            condition=BooleanCondition('NUMBER_GREATER', ['0']),
            format=CellFormat(backgroundColor=VERDE_MEDIO)
        )
    ))

    # Vermelho para valores < 0
    rules.append(ConditionalFormatRule(
        ranges=[GridRange.from_a1_range(intervalo, worksheet)],
        booleanRule=BooleanRule(
            condition=BooleanCondition('NUMBER_LESS', ['0']),
            format=CellFormat(backgroundColor=VERMELHO_MEDIO)
        )
    ))

    rules.save()

def formatar_aba(worksheet, num_colunas, num_linhas, colunas_valor):
    """Formatação comum para todas as abas"""
    header_format = CellFormat(
        backgroundColor=Color(0.06, 0.32, 0.54),
        textFormat=TextFormat(bold=True, fontSize=12, foregroundColor=Color(1, 1, 1)),
        horizontalAlignment='CENTER',
        verticalAlignment='MIDDLE'
    )
    
    money_format = CellFormat(
        numberFormat=NumberFormat(type='NUMBER', pattern='#,##0.00;[RED]-#,##0.00')
    )
    
    format_cell_range(worksheet, f'A1:{chr(64 + num_colunas)}1', header_format)
    
    for coluna in colunas_valor:
        format_cell_range(worksheet, f'{coluna}2:{coluna}', money_format)
    
    remover_filtros(worksheet)
    
    worksheet.freeze(rows=1)
    
    # Limpa especificamente a coluna C se for a aba Saldos
    if worksheet.title == "Saldos":
        format_cell_range(worksheet, 'C1:C1000', CellFormat(
            backgroundColor=Color(1, 1, 1),
            textFormat=TextFormat()
        ))
    else:
        limpar_colunas_extras(worksheet, num_colunas)
    
    for coluna in colunas_valor:
        if worksheet.title == "Saldos":
            print(f"🎨 Aplicando cores condicionais na coluna {coluna} da aba Saldos")
            aplicar_escala_cores_valor_simples(worksheet, coluna, num_linhas)
        else:
            aplicar_escala_cores_valor(worksheet, coluna, num_linhas)
    
    # Ajusta largura das colunas
    try:
        if worksheet.title == "Saldos":
            # Para aba Saldos, ajusta largura manualmente
            worksheet.columns_auto_resize(0, 2)  # Apenas 2 colunas
        else:
            worksheet.columns_auto_resize(0, num_colunas)
    except Exception as e:
        print(f"⚠️ Ajuste de colunas falhou: {str(e)}")

    # Ativa filtro básico na área usada
    try:
        if worksheet.title == "Saldos":
            # Para aba Saldos, filtro apenas de A1 até B9
            intervalo = f"A1:B{num_linhas + 1}"
        else:
            intervalo = f"A1:{chr(64 + num_colunas)}{num_linhas + 1}"
        worksheet.set_basic_filter(intervalo)
    except Exception as e:
        print(f"⚠️ Não foi possível aplicar filtro: {e}")

def enviar_para_planilha(gc, aba_nome, cabecalho, dados, colunas_valor):
    """Envia dados para uma aba específica da planilha"""
    try:
        sh = gc.open(SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        print(f"❌ Planilha '{SPREADSHEET_NAME}' não encontrada.")
        return

    try:
        worksheet = sh.worksheet(aba_nome)
        worksheet.clear()
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sh.add_worksheet(title=aba_nome, rows=1000, cols=len(cabecalho))
    
    # Remover abas antigas, se existirem
    for aba in ["Página1", "Dashboard"]:
        try:
            sh.del_worksheet(sh.worksheet(aba))
            print(f"ℹ️ Aba '{aba}' removida")
        except:
            pass
    
    dados_planilha = preparar_dados_planilha(dados)
    
    # Atualiza cabeçalho
    worksheet.update(values=[cabecalho], range_name='A1')
    time.sleep(1)
    
    # Atualiza dados, se houver
    if dados_planilha:
        worksheet.update(values=dados_planilha, range_name=f'A2:{chr(65+len(cabecalho)-1)}{len(dados_planilha)+1}')
    
    # Aplica formatação
    formatar_aba(worksheet, len(cabecalho), len(dados_planilha), colunas_valor)
    
    print(f"✅ Aba '{aba_nome}' atualizada com {len(dados_planilha)} registros.")

def upload_transactions_to_sheet(gc):
    """Processa e envia transações para a planilha"""
    print("📊 Processando transações...")
    
    transacoes_brutas = ler_transacoes()
    transacoes_validas = []
    transacoes_excluidas = []
    
    for data_str, categoria, conta, valor, notas in transacoes_brutas:
        linha = [
            formatar_data(data_str),
            conta or "",
            categoria or "Sem Categoria",
            float(valor)/100 if valor else 0.0,
            notas or ""
        ]
        
        if not categoria or categoria.strip().lower() == "starting balances":
            transacoes_excluidas.append(linha)
        else:
            transacoes_validas.append(linha)
    
    # Enviar para as abas
    enviar_para_planilha(gc, "Transações", cabecalho_transacoes, transacoes_validas, ['D'])
    enviar_para_planilha(gc, "Excluídas", cabecalho_excluidas, transacoes_excluidas, ['D'])
    
    print("✅ Transações processadas com sucesso!")

def upload_balances_to_sheet(gc):
    """Processa e envia saldos para a planilha"""
    print("💰 Processando saldos...")
    
    saldos_brutos = ler_saldos()
    saldos = []
    for item in saldos_brutos:
        if len(item) >= 2:
            nome, saldo = item[:2]
            saldo = float(saldo) if saldo is not None else 0.0
            saldos.append([nome, saldo])
        else:
            saldos.append([item[0], 0.0])

    # Enviar para a aba Saldos
    enviar_para_planilha(gc, "Saldos", cabecalho_saldos, saldos, ['B'])
    
    print("✅ Saldos processados com sucesso!")

def main():
    """Função principal que orquestra todo o processo de exportação"""
    print("🚀 Iniciando processo de exportação...")
    
    # Verificar se o arquivo de credenciais existe
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ Arquivo de credenciais não encontrado: {CREDENTIALS_FILE}")
        print("📁 Verificando arquivos na pasta atual:")
        for file in os.listdir('.'):
            if file.endswith('.json'):
                print(f"   - {file}")
        return
    
    # Verificar se o arquivo SQLite existe
    if not os.path.exists(SQLITE_DB):
        print(f"❌ Banco SQLite não encontrado: {SQLITE_DB}")
        print("📁 Verificando arquivos na pasta atualizador/data:")
        if os.path.exists('atualizador/data'):
            for root, dirs, files in os.walk('atualizador/data'):
                for file in files:
                    print(f"   - {os.path.join(root, file)}")
        return
    
    # Autenticação no Google Sheets (executada apenas uma vez)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        gc = gspread.authorize(credentials)
    except Exception as e:
        print(f"❌ Erro ao carregar credenciais: {str(e)}")
        print(f"📄 Verificando conteúdo do arquivo {CREDENTIALS_FILE}:")
        try:
            with open(CREDENTIALS_FILE, 'r') as f:
                content = f.read()
                print(f"   Primeiras 100 caracteres: {content[:100]}")
        except Exception as read_error:
            print(f"   Erro ao ler arquivo: {str(read_error)}")
        return
    
    print(f"✅ Conectado ao Google Sheets: {SPREADSHEET_NAME}")
    
    # Processa e envia transações
    upload_transactions_to_sheet(gc)
    
    # Processa e envia saldos
    upload_balances_to_sheet(gc)
    
    print("🎉 Processo de exportação concluído com sucesso!")

if __name__ == "__main__":
    main()

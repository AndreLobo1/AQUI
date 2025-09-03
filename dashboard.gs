/**
 * Dashboard Financeiro - Aba Home com filtros, gráficos e listas
 * Autor: Você + assistência
 * Funcionalidades: dropdowns, gráficos, atualização automática
 *
 * Versão com melhorias:
 * - Bloco de transações movido uma coluna para a esquerda (começando em D).
 */

// Executado ao abrir a planilha
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('📊 Dashboard')
    .addItem('Atualizar Tela', 'atualizarHome')
    .addItem('Configurar Dropdowns', 'configurarDropdowns')
    .addToUi();

  configurarAbaHome();
  configurarDropdowns();
  atualizarHome();
}

// Cria ou limpa a aba Home
function configurarAbaHome() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let homeSheet = ss.getSheetByName('Home');

  if (!homeSheet) {
    homeSheet = ss.insertSheet('Home', ss.getNumSheets());
  }

  homeSheet.clear();

  // === SEÇÃO "SELECIONE O MÊS E ANO" ===
  homeSheet.getRange('A3:B3').merge().setValue('Selecione o mês e ano')
    .setFontWeight('bold').setHorizontalAlignment('center').setFontSize(14).setBackground('#e0e0e0');
  homeSheet.getRange('A3:B8').setBorder(true, true, true, true, false, false);

  // Campos Mês e Ano
  homeSheet.getRange('A4').setValue('Mês:');
  homeSheet.getRange('A5').setValue('Ano:');
  homeSheet.getRange('A4:A5').setHorizontalAlignment('center');

  // Resumo Financeiro
  homeSheet.getRange('A6').setValue('Entradas');
  homeSheet.getRange('A7').setValue('Saídas');
  homeSheet.getRange('A8').setValue('Balanço');
  homeSheet.getRange('A6:A8').setBackground('#f0f0f0');
  homeSheet.getRange('A6:A8').setHorizontalAlignment('center').setFontWeight('bold');

  // Valores do Resumo
  homeSheet.getRange('B6:B8').setNumberFormat('R$ #,##0.00').setHorizontalAlignment('center');
  homeSheet.getRange('B6').setBackground('#c8e6c9');
  homeSheet.getRange('B7').setBackground('#ffcdd2');
  homeSheet.getRange('B8').setBackground('white');

  // Título com Nome do Mês
  homeSheet.getRange('A1:B1').merge().setValue('')
    .setFontWeight('bold').setFontSize(16)
    .setHorizontalAlignment('center').setBackground('#e0e0e0');

  // === TÍTULOS E CABEÇALHOS DAS LISTAS (NOVAS POSIÇÕES) ===
  // *** NOVO: Posição D14:H14 ***
  homeSheet.getRange('D14:H14').merge().setValue('Transações de Entrada')
    .setFontWeight('bold').setFontSize(14).setBackground('#2e7d32').setFontColor('white').setHorizontalAlignment('center');
  // *** NOVO: Posição J14:N14 ***
  homeSheet.getRange('J14:N14').merge().setValue('Transações de Saída')
    .setFontWeight('bold').setFontSize(14).setBackground('#c62828').setFontColor('white').setHorizontalAlignment('center');

  const cabecalho = ['Data', 'Conta', 'Categoria', 'Notas', 'Valor'];
  // *** NOVO: Posição D15:H15 ***
  homeSheet.getRange('D15:H15').setValues([cabecalho])
    .setFontWeight('bold').setBackground('#f0f0f0').setHorizontalAlignment('center');
  // *** NOVO: Posição J15:N15 ***
  homeSheet.getRange('J15:N15').setValues([cabecalho])
    .setFontWeight('bold').setBackground('#f0f0f0').setHorizontalAlignment('center');

  // === AJUSTE DE LARGURA DAS COLUNAS (NOVAS POSIÇÕES) ===
  const colWidths = {
    4:90, 5:130, 6:140, 7:150, 8:100, // Colunas de Entrada (D-H)
    9:30, // Coluna de respiro (I)
    10:90, 11:130, 12:140, 13:150, 14:100 // Colunas de Saída (J-N)
  };
  for (let col in colWidths) { homeSheet.setColumnWidth(col, colWidths[col]); }
  homeSheet.autoResizeColumns(1, 2);

  // === BORDAS DAS TABELAS ===
  const maxRows = homeSheet.getMaxRows();
  const rangeEntradas = homeSheet.getRange('D14:H' + maxRows);
  const rangeSaidas = homeSheet.getRange('J14:N' + maxRows);
  rangeEntradas.setBorder(true, true, true, true, true, true);
  rangeEntradas.setBorder(true, true, true, true, false, false, 'black', SpreadsheetApp.BorderStyle.SOLID_THICK);
  rangeSaidas.setBorder(true, true, true, true, true, true);
  rangeSaidas.setBorder(true, true, true, true, false, false, 'black', SpreadsheetApp.BorderStyle.SOLID_THICK);
  homeSheet.getRange('D14:H14').setBorder(null, null, true, null, null, false, 'black', SpreadsheetApp.BorderStyle.SOLID_THICK);
  homeSheet.getRange('D15:H15').setBorder(null, null, true, null, null, false, 'black', SpreadsheetApp.BorderStyle.SOLID_THICK);
  homeSheet.getRange('J14:N14').setBorder(null, null, true, null, null, false, 'black', SpreadsheetApp.BorderStyle.SOLID_THICK);
  homeSheet.getRange('J15:N15').setBorder(null, null, true, null, null, false, 'black', SpreadsheetApp.BorderStyle.SOLID_THICK);
  
  // Formatação de moeda (NOVAS POSIÇÕES)
  homeSheet.getRange('H16:H' + maxRows).setNumberFormat('R$ #,##0.00');
  homeSheet.getRange('N16:N' + maxRows).setNumberFormat('R$ #,##0.00');
}


// Configura dropdowns com meses e anos disponíveis
function configurarDropdowns() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const homeSheet = ss.getSheetByName('Home');
  const transacoesSheet = ss.getSheetByName('Transações');
  if (!transacoesSheet) { SpreadsheetApp.getUi().alert('❌ Erro: Aba "Transações" não encontrada.'); return; }
  const dados = transacoesSheet.getDataRange().getValues();
  const linhas = dados.slice(1);
  const mesesSet = new Set();
  const anosSet = new Set();
  for (const linha of linhas) {
    const dataValor = linha[0];
    if (dataValor instanceof Date) {
      mesesSet.add(dataValor.getMonth() + 1);
      anosSet.add(dataValor.getFullYear());
    } else if (typeof dataValor === 'string' && dataValor.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
        const partes = dataValor.split('/');
        const mes = parseInt(partes[1], 10);
        const ano = parseInt(partes[2], 10);
        if (!isNaN(mes) && mes >= 1 && mes <= 12) mesesSet.add(mes);
        if (!isNaN(ano)) anosSet.add(ano);
    }
  }
  const meses = [...mesesSet].sort((a, b) => a - b);
  const anos = [...anosSet].sort((a, b) => a - b);
  if (meses.length === 0 || anos.length === 0) { SpreadsheetApp.getUi().alert('⚠️ Nenhum dado válido encontrado na aba "Transações".'); return; }
  const mesCell = homeSheet.getRange('B4');
  const anoCell = homeSheet.getRange('B5');
  mesCell.setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(meses).setAllowInvalid(false).build());
  if (!mesCell.getValue() || !meses.includes(mesCell.getValue())) { mesCell.setValue(Math.max(...meses)); }
  anoCell.setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(anos).setAllowInvalid(false).build());
  if (!anoCell.getValue() || !anos.includes(anoCell.getValue())) { anoCell.setValue(Math.max(...anos)); }
}

// Atualiza toda a aba Home com base no mês/ano selecionado
function atualizarHome() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const homeSheet = ss.getSheetByName('Home');
  const transacoesSheet = ss.getSheetByName('Transações');
  if (!homeSheet || !transacoesSheet) return;
  const mes = homeSheet.getRange('B4').getValue();
  const ano = homeSheet.getRange('B5').getValue();
  if (!mes || !ano) return;
  const dados = transacoesSheet.getDataRange().getValues();
  const linhas = dados.slice(1);
  const [idxData, idxConta, idxCat, idxValor, idxNotas] = [0, 1, 2, 3, 4];
  const filtradas = linhas.filter(l => {
    const dataValor = l[idxData];
    if (!dataValor) return false;
    if (dataValor instanceof Date) {
        return dataValor.getMonth() + 1 === mes && dataValor.getFullYear() === ano;
    } else if (typeof dataValor === 'string' && dataValor.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
        const partes = dataValor.split('/');
        return parseInt(partes[1], 10) === mes && parseInt(partes[2], 10) === ano;
    }
    return false;
  });
  const entradas = filtradas.filter(t => t[idxValor] > 0);
  const saidas = filtradas.filter(t => t[idxValor] < 0);
  const totalEntradas = entradas.reduce((s, t) => s + t[idxValor], 0);
  const totalSaidas = saidas.reduce((s, t) => s + t[idxValor], 0);
  const balanco = totalEntradas + totalSaidas;
  
  homeSheet.getRange('B6').setValue(totalEntradas);
  homeSheet.getRange('B7').setValue(totalSaidas);
  homeSheet.getRange('B8').setValue(balanco);

  const cellBalanço = homeSheet.getRange('B8');
  if (balanco > 0) { cellBalanço.setBackground('#c8e6c9'); }
  else if (balanco < 0) { cellBalanço.setBackground('#ffcdd2'); }
  else { cellBalanço.setBackground('white'); }
  cellBalanço.setFontColor('black');

  const nomesMeses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
  homeSheet.getRange('A1:B1').setValue(`${nomesMeses[mes - 1]} ${ano}`);
  const indices = [idxData, idxConta, idxCat, idxNotas, idxValor];
  
  // *** NOVO: Células iniciais D16 e J16 ***
  atualizarLista(homeSheet, 'D16', entradas, indices);
  atualizarLista(homeSheet, 'J16', saidas, indices);
  
  recriarGraficos(homeSheet, entradas, saidas, idxCat, idxValor, totalEntradas, totalSaidas, balanco);
}

// Atualiza listas de transações
function atualizarLista(sheet, startCellA1, dados, indices) {
    const startRange = sheet.getRange(startCellA1);
    const startRow = startRange.getRow();
    const startCol = startRange.getColumn();
    const clearRange = sheet.getRange(startRow, startCol, sheet.getMaxRows() - startRow + 1, 5);
    clearRange.clearContent(); 
    if (dados.length === 0) {
        sheet.getRange(startRow, startCol, 1, 5).merge().setValue('Nenhuma transação neste período.').setHorizontalAlignment('center');
        return;
    }
    const [idxData, idxConta, idxCat, idxNotas, idxValor] = indices;
    const valores = dados.map(d => [d[idxData], d[idxConta], d[idxCat], d[idxNotas], d[idxValor]]);
    sheet.getRange(startRow, startCol, valores.length, valores[0].length).setValues(valores);
}

// Recria gráficos
function recriarGraficos(sheet, entradas, saidas, idxCat, idxValor, totalEnt, totalSai, balanco) {
  sheet.getCharts().forEach(chart => sheet.removeChart(chart));
  
  const LINHA_BASE = sheet.getMaxRows() - 100 > 200 ? sheet.getMaxRows() - 100 : 200;
  function agrupar(arr) {
    const map = {};
    arr.forEach(t => { const cat = t[idxCat] || 'Outros'; map[cat] = (map[cat] || 0) + Math.abs(t[idxValor]); });
    return Object.entries(map);
  }

  // Gráficos de Rosca
  const dadosEntradas = agrupar(entradas);
  if (dadosEntradas.length > 0) {
    sheet.getRange(LINHA_BASE, 7, dadosEntradas.length, 2).setValues(dadosEntradas);
    const chart = sheet.newChart().setChartType(Charts.ChartType.PIE)
      .addRange(sheet.getRange(LINHA_BASE, 7, dadosEntradas.length, 2))
      // *** NOVO: Posição na coluna 4 (D) ***
      .setPosition(1, 4, 0, 0).setOption('title', 'Entradas por Categoria')
      .setOption('pieHole', 0.4).setOption('width', 620).setOption('height', 285).build();
    sheet.insertChart(chart);
  }
  const dadosSaidas = agrupar(saidas);
  if (dadosSaidas.length > 0) {
    sheet.getRange(LINHA_BASE, 12, dadosSaidas.length, 2).setValues(dadosSaidas);
    const chart = sheet.newChart().setChartType(Charts.ChartType.PIE)
      .addRange(sheet.getRange(LINHA_BASE, 12, dadosSaidas.length, 2))
      // *** NOVO: Posição na coluna 10 (J) ***
      .setPosition(1, 10, 0, 0).setOption('title', 'Saídas por Categoria')
      .setOption('pieHole', 0.4).setOption('width', 620).setOption('height', 285).build();
    sheet.insertChart(chart);
  }

  // Cash Flow
  const cashData = [['Entradas', totalEnt], ['Saídas', -totalSai]];
  const cashRange = sheet.getRange(LINHA_BASE, 1, 2, 2);
  cashRange.setValues(cashData);
  const cashChart = sheet.newChart().setChartType(Charts.ChartType.COLUMN)
    .addRange(cashRange)
    .setPosition(11, 1, 0, 0)
    .setOption('title', 'Cash Flow Mensal').setOption('vAxis.title', 'Valor (R$)')
    .setOption('width', 300).setOption('height', 400).build();
  sheet.insertChart(cashChart);
}


// Atualiza automaticamente ao mudar mês ou ano
function onEdit(e) {
  const { range } = e;
  const sheet = range.getSheet();
  if (sheet.getName() === 'Home' && ['B4', 'B5'].includes(range.getA1Notation())) {
    atualizarHome();
  }
}
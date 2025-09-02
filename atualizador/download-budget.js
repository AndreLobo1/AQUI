const api = require('@actual-app/api');

async function main() {
  // Configurações
  const serverURL = process.env.ACTUAL_SERVER_URL || 'https://carteiraflyio.fly.dev'; 
  const syncId = process.env.ACTUAL_SYNC_ID || '4f676946-1eb8-4174-8499-a23502230680'; // Este é o ID correto pra download
  const password = process.env.ACTUAL_PASSWORD || 'El!z@be7h1272@'; // Sua senha do app web
  const dataDir = './data';

  // Inicializa conexão
  await api.init({
    serverURL,
    password,
    dataDir,
  });

  console.log(`📥 Baixando orçamento...`);
  try {
    // Baixa o orçamento com o Sync ID
    await api.downloadBudget(syncId, {
      password // Se seu orçamento for criptografado
    });
    console.log(`✅ Banco baixado em: ${dataDir}/${syncId}.sqlite`);
  } catch (err) {
    console.error(`❌ Erro ao baixar orçamento:`, err.message);
  } finally {
    await api.shutdown();
  }
}

main().catch(console.error);
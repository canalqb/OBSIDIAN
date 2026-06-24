/**
 * Obsidian to NotebookLM Pipeline
 * Script para mesclar notas do Obsidian em um único arquivo .txt
 * 
 * Baseado em: https://www.canalqb.com.br/2026/06/seo-claude-code-notebooklm-obsidian.html
 */

// CONFIGURAÇÃO
// Substitua pelo ID da pasta do seu vault no Google Drive
const ID_PASTA_OBSIDIAN = 'SEU_ID_DE_PASTA_AQUI';

// Nome do arquivo de saída
const NOME_ARQUIVO_SAIDA = 'Obsidian_Master.txt';

/**
 * Função principal: mescla todas as notas .md do vault em um único .txt
 */
function mesclarObsidianParaTxt() {
  try {
    // Obtém a pasta raiz do vault
    const pastaRaiz = DriveApp.getFolderById(ID_PASTA_OBSIDIAN);
    
    // Inicializa o conteúdo com cabeçalho
    let conteudo = 'EXPORT OBSIDIAN VAULT — ' + new Date().toLocaleString('pt-BR') + '\n\n';
    
    // Função recursiva para coletar conteúdo de todas as subpastas
    function coletarConteudo(pasta) {
      // Processa arquivos .md na pasta atual
      const arquivos = pasta.getFiles();
      while (arquivos.hasNext()) {
        const arquivo = arquivos.next();
        if (arquivo.getName().endsWith('.md')) {
          const titulo = arquivo.getName().replace('.md', '');
          const texto = arquivo.getBlob().getDataAsString();
          conteudo += '--- NOTA: ' + titulo + ' ---\n' + texto + '\n\n';
        }
      }
      
      // Processa subpastas recursivamente
      const subpastas = pasta.getFolders();
      while (subpastas.hasNext()) {
        coletarConteudo(subpastas.next());
      }
    }
    
    // Executa a coleta de conteúdo
    coletarConteudo(pastaRaiz);
    
    // Verifica se o arquivo já existe e atualiza, ou cria novo
    const existentes = DriveApp.getFilesByName(NOME_ARQUIVO_SAIDA);
    if (existentes.hasNext()) {
      existentes.next().setContent(conteudo);
      console.log('Arquivo atualizado: ' + NOME_ARQUIVO_SAIDA);
    } else {
      DriveApp.createFile(NOME_ARQUIVO_SAIDA, conteudo, MimeType.PLAIN_TEXT);
      console.log('Arquivo criado: ' + NOME_ARQUIVO_SAIDA);
    }
    
    console.log('Vault exportado com sucesso!');
    
  } catch (error) {
    console.error('Erro ao mesclar Obsidian:', error);
    throw error;
  }
}

/**
 * Função para teste manual
 * Execute esta função para testar sem configurar o trigger
 */
function testeMesclagem() {
  console.log('Iniciando teste de mesclagem...');
  mesclarObsidianParaTxt();
  console.log('Teste concluído!');
}

/**
 * Função para obter estatísticas do vault
 * Retorna número de notas e tamanho total
 */
function obterEstatisticasVault() {
  const pastaRaiz = DriveApp.getFolderById(ID_PASTA_OBSIDIAN);
  let contadorNotas = 0;
  let tamanhoTotal = 0;
  
  function contarArquivos(pasta) {
    const arquivos = pasta.getFiles();
    while (arquivos.hasNext()) {
      const arquivo = arquivos.next();
      if (arquivo.getName().endsWith('.md')) {
        contadorNotas++;
        tamanhoTotal += arquivo.getSize();
      }
    }
    
    const subpastas = pasta.getFolders();
    while (subpastas.hasNext()) {
      contarArquivos(subpastas.next());
    }
  }
  
  contarArquivos(pastaRaiz);
  
  console.log('Estatísticas do Vault:');
  console.log('- Notas: ' + contadorNotas);
  console.log('- Tamanho total: ' + (tamanhoTotal / 1024).toFixed(2) + ' KB');
  console.log('- Tamanho médio por nota: ' + (tamanhoTotal / contadorNotas / 1024).toFixed(2) + ' KB');
  
  return {
    notas: contadorNotas,
    tamanhoKB: (tamanhoTotal / 1024).toFixed(2)
  };
}

/**
 * Função para mesclar apenas uma pasta específica
 * Útil para vaults grandes que precisam ser divididos
 */
function mesclarPastaEspecifica(idPasta, nomeArquivo) {
  try {
    const pasta = DriveApp.getFolderById(idPasta);
    let conteudo = 'EXPORT PASTA: ' + pasta.getName() + ' — ' + new Date().toLocaleString('pt-BR') + '\n\n';
    
    const arquivos = pasta.getFiles();
    while (arquivos.hasNext()) {
      const arquivo = arquivos.next();
      if (arquivo.getName().endsWith('.md')) {
        const titulo = arquivo.getName().replace('.md', '');
        const texto = arquivo.getBlob().getDataAsString();
        conteudo += '--- NOTA: ' + titulo + ' ---\n' + texto + '\n\n';
      }
    }
    
    const existentes = DriveApp.getFilesByName(nomeArquivo);
    if (existentes.hasNext()) {
      existentes.next().setContent(conteudo);
    } else {
      DriveApp.createFile(nomeArquivo, conteudo, MimeType.PLAIN_TEXT);
    }
    
    console.log('Pasta exportada: ' + nomeArquivo);
    
  } catch (error) {
    console.error('Erro ao mesclar pasta:', error);
    throw error;
  }
}

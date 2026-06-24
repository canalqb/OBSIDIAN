# Obsidian + NotebookLM Pipeline

Automatize sua pesquisa com IA integrando Obsidian, NotebookLM e Google Apps Script.

## 📋 Visão Geral

Este projeto implementa o pipeline gratuito descrito no artigo [SEO: Claude Code + NotebookLM + Obsidian](https://www.canalqb.com.br/2026/06/seo-claude-code-notebooklm-obsidian.html) do CanalQb.

### O que faz

- Sincroniza notas do Obsidian com Google Drive
- Mescla todas as notas `.md` em um único arquivo `.txt`
- Atualiza automaticamente via Google Apps Script
- Integra com NotebookLM para pesquisa com IA

## 🚀 Funcionalidades

- ✅ Exportação automática do vault Obsidian para `.txt`
- ✅ Trigger automático no Google Apps Script
- ✅ Integração com NotebookLM via Google Drive
- ✅ Suporte para até 400 notas (validado)
- ✅ Limite de 500.000 palavras por fonte

## 📁 Estrutura do Projeto

```
obsidian-notebooklm-pipeline/
├── google-apps-script/
│   └── Code.js              # Script de mesclagem do Obsidian
├── docs/
│   └── configuracoes.txt    # Template de configuração
├── .gitignore              # Arquivos ignorados no Git
├── README.md               # Este arquivo
└── config.example.txt      # Exemplo de configuração (não commitar dados reais)
```

## 🛠️ Instalação

### Pré-requisitos

- Conta Google com acesso ao [Google Drive](https://drive.google.com)
- Acesso ao [NotebookLM](https://notebooklm.google.com)
- Obsidian instalado
- Extensão [NotebookLM Tools](https://chrome.google.com/webstore) para Chrome

### Passo 1: Sincronizar Obsidian com Google Drive

1. Coloque sua pasta do vault Obsidian dentro do Google Drive
2. Se usa Obsidian Sync, crie uma segunda pasta para automação
3. Copie as notas relevantes para essa pasta

### Passo 2: Configurar Google Apps Script

1. Acesse [script.google.com](https://script.google.com)
2. Crie um novo projeto
3. Copie o código de `google-apps-script/Code.js`
4. Substitua `SEU_ID_DE_PASTA_AQUI` pelo ID da sua pasta no Drive
5. Salve e teste a função `mesclarObsidianParaTxt`

### Passo 3: Configurar Trigger Automático

1. No Apps Script, clique no ícone de relógio (Triggers)
2. Adicione novo trigger para `mesclarObsidianParaTxt`
3. Configure para executar a cada 1 hora ou em alteração de arquivo

### Passo 4: Integrar com NotebookLM

1. Acesse [notebooklm.google.com](https://notebooklm.google.com)
2. Crie um notebook novo
3. Adicione o arquivo `Obsidian_Master.txt` do Google Drive como fonte
4. Instale a extensão NotebookLM Tools no Chrome
5. Use o botão de refresh para atualizar fontes automaticamente

## ⚙️ Configuração

Copie `config.example.txt` para `config.txt` e preencha suas variáveis:

```bash
cp config.example.txt config.txt
```

**Importante:** Nunca commitar `config.txt` com dados reais. Use apenas `config.example.txt` como template.

## 📝 Variáveis de Configuração

### Google Drive
- `ID_DA_PASTA_OBSIDIAN`: ID da pasta do vault no Google Drive
- `NOME_ARQUIVO_SAIDA`: Nome do arquivo .txt gerado (padrão: Obsidian_Master.txt)

### Google Apps Script
- `URL_SCRIPT`: URL do projeto no Apps Script
- `FUNCAO_TRIGGER`: Nome da função (mesclarObsidianParaTxt)
- `FREQUENCIA_TRIGGER`: Frequência de execução

### NotebookLM
- `URL_NOTEBOOKLM`: URL do notebook criado
- `NOME_NOTEBOOK`: Nome do notebook

## 🔒 Segurança

- **Nunca** commitar dados sensíveis (API keys, IDs reais, tokens)
- Use arquivos `.example` para templates
- Adicione arquivos com dados reais ao `.gitignore`
- Revise permissões do Apps Script

## 📊 Limites

- **Máximo de notas**: 400 (validado pelo CanalQb)
- **Máximo de palavras**: 500.000 por fonte no NotebookLM
- Para vaults maiores, divida em múltiplos arquivos por pasta temática

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fork o projeto
2. Criar uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abrir um Pull Request

## 📄 Licença

Este projeto é baseado no conteúdo do [CanalQb](https://www.canalqb.com.br) e está disponível para uso educacional.

## 🔗 Referências

- [Artigo Original](https://www.canalqb.com.br/2026/06/seo-claude-code-notebooklm-obsidian.html)
- [Canal YouTube: CanalQb](https://www.youtube.com/@CanalQb)
- [Google Apps Script](https://script.google.com)
- [NotebookLM](https://notebooklm.google.com)

## 💡 Dicas

1. Teste com um pequeno número de notas antes de processar o vault completo
2. Faça backup do seu vault antes de qualquer automação
3. Verifique se a pasta do Obsidian está sincronizada com o Google Drive
4. Use a extensão NotebookLM Tools para atualizar fontes sem recriar o notebook

## 📧 Suporte

Para dúvidas, consulte o artigo original do CanalQb ou abra uma issue neste repositório.

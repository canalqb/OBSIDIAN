# Substituição do Google Apps Script por Python

## Por Que Python em Vez de Apps Script?

O Google Apps Script API requer autenticação e permissões separadas que não foram configuradas no projeto. Além disso, o Apps Script tem limitações de execução e não pode ser facilmente integrado com outros scripts Python.

## Solução: Script Python `merge_notes.py`

Criamos um script Python que faz exatamente o que o Apps Script faria:

### Funcionalidades
- Lê todos os arquivos `.md` do Obsidian no Google Drive
- Percorre subpastas recursivamente
- Mescla todo o conteúdo em um único arquivo `Obsidian_Master.txt`
- Atualiza o arquivo no Drive usando OAuth

### Vantagens
- ✅ Usa as mesmas credenciais OAuth já configuradas
- ✅ Integração perfeita com outros scripts Python
- ✅ Sem limitações de tempo do Apps Script
- ✅ Pode ser executado localmente ou em GitHub Actions
- ✅ Mais flexível e extensível

## Como Usar

### Execução Direta
```bash
cd c:\Users\Qb\Desktop\obsidian\obsidian-notebooklm-pipeline
$env:GOOGLE_CLIENT_ID="..."
$env:GOOGLE_CLIENT_SECRET="..."
$env:GOOGLE_REFRESH_TOKEN="..."
python scripts/merge_notes.py --folder-id 1Eikf5MOwCNopr-FS976lheYlUprvWEx-
```

### Via Auto Sync
```bash
python scripts/auto_sync.py --folder-id 1Eikf5MOwCNopr-FS976lheYlUprvWEx- --notebook-id 999a0463-0274-49fe-8fb7-f242338f4a2d
```

## Diferenças do Apps Script Original

| Apps Script | Python (merge_notes.py) |
|------------|-------------------------|
| Requer Apps Script API | Usa Drive API (já configurada) |
| Executa no Google Cloud | Executa localmente |
| Limitado a 6 min | Sem limitação de tempo |
| JavaScript | Python |
| Trigger manual/cron | Pode ser agendado via GitHub Actions |

## Automação com GitHub Actions

Para automação completa, crie um workflow no GitHub:

```yaml
name: Sync Obsidian to NotebookLM

on:
  schedule:
    - cron: '0 */2 * * *'  # A cada 2 horas
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Sync Obsidian
        env:
          GOOGLE_CLIENT_ID: ${{ secrets.GOOGLE_CLIENT_ID }}
          GOOGLE_CLIENT_SECRET: ${{ secrets.GOOGLE_CLIENT_SECRET }}
          GOOGLE_REFRESH_TOKEN: ${{ secrets.GOOGLE_REFRESH_TOKEN }}
        run: python scripts/auto_sync.py --folder-id ${{ secrets.OBSIDIAN_VAULT_FOLDER_ID }}
```

## Status do Apps Script

O arquivo `google-apps-script/Code.js` ainda está disponível no repositório como referência, mas não é mais necessário para o funcionamento do sistema.

## Próximos Passos

1. Adicione notas `.md` à sua pasta do Obsidian no Drive
2. Execute `python scripts/merge_notes.py` para testar
3. Configure GitHub Actions para automação
4. Use NotebookLM Tools para atualizar fontes automaticamente

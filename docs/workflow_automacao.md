# Workflow de Automação Completo

## Fluxo Automatizado

```
Claude Code → Obsidian_Master.txt → NotebookLM → Outputs no Drive
     ↓              ↓                   ↓              ↓
  (API REST)    (GitHub Actions)   (notebooklm-py)   (Drive API)
```

## Como Funciona

### 1. Claude Code Alimenta Obsidian_Master.txt

**Via API REST (Recomendado):**
```bash
# API deve estar rodando
python scripts/obsidian_api.py

# Claude envia conteúdo para http://localhost:5000/add
```

**Via CLI:**
```bash
python scripts/add_to_obsidian.py --content "Pesquisa sobre IA" --source "Claude Code"
```

### 2. GitHub Actions Detecta Mudanças

**Workflow:** `.github/workflows/sync-notebooklm.yml`

**Executa:** A cada 6 horas (cron: `0 */6 * * *`)

**Passos:**
1. Verifica se `Obsidian_Master.txt` teve mudanças (hash MD5)
2. Se houver mudanças → sincroniza com NotebookLM
3. Salva outputs do NotebookLM no Drive

### 3. Sincronização com NotebookLM

**Script:** `scripts/sync_to_notebooklm.py`

**Usa:** `notebooklm-py` (API não oficial)

**Função:**
- Adiciona/atualiza `Obsidian_Master.txt` como fonte no notebook
- NotebookLM processa o conteúdo

### 4. Salvar Outputs no Drive

**Script:** `scripts/save_notebooklm_outputs.py`

**Salva:**
- Respostas do NotebookLM como arquivos `.txt`
- Resumos do notebook
- Cria pasta `NotebookLM_Outputs` no Drive

## Configuração do GitHub

### Secrets Necessários

Adicione estes secrets no GitHub (Settings → Secrets and variables → Actions):

```
GOOGLE_CLIENT_ID=<seu_client_id>
GOOGLE_CLIENT_SECRET=<seu_client_secret>
GOOGLE_REFRESH_TOKEN=<seu_refresh_token>
OBSIDIAN_VAULT_FOLDER_ID=1Eikf5MOwCNopr-FS976lheYlUprvWEx-
NOTEBOOKLM_NOTEBOOK_ID=999a0463-0274-49fe-8fb7-f242338f4a2d
```

**Nota:** As credenciais OAuth devem ser obtidas do Google Cloud Console (veja `configuracoes_pipeline.txt`).

### Ativar Workflow

1. Vá para: https://github.com/canalqb/OBSIDIAN/actions
2. Clique em "Sync Obsidian to NotebookLM"
3. Clique em "Enable workflow"
4. O workflow executará automaticamente a cada 6 horas

## Execução Manual

Para testar o workflow manualmente:

```bash
# No GitHub Actions
1. Vá para Actions tab
2. Selecione "Sync Obsidian to NotebookLM"
3. Clique em "Run workflow"
4. Selecione branch e clique em "Run workflow"
```

## Fluxo Completo Exemplo

### 1. Claude Adiciona Conteúdo

```python
# Claude Code executa:
import requests

response = requests.post(
    'http://localhost:5000/add',
    json={
        'content': 'Pesquisa sobre IA em 2026: tendências, aplicações e empresas líderes',
        'source': 'Claude Code'
    }
)
```

### 2. GitHub Actions Executa (6 horas depois)

```
✅ Detecta mudança no Obsidian_Master.txt
✅ Sincroniza com NotebookLM
✅ NotebookLM processa conteúdo
✅ Salva outputs no Drive
```

### 3. Outputs Disponíveis no Drive

```
📁 NotebookLM_Outputs/
   ├── response_20240624_120000_0.txt
   ├── response_20240624_120000_1.txt
   └── summary_20240624_120000.txt
```

## Limitações

### NotebookLM API Não Oficial

- `notebooklm-py` usa engenharia reversa nos endpoints do NotebookLM
- Pode parar de funcionar se o Google mudar a API
- **Alternativa:** Use extensão NotebookLM Tools (Chrome) manualmente

### Solução de Fallback

Se `notebooklm-py` falhar, o workflow ainda:
1. ✅ Detecta mudanças
2. ✅ Salva outputs (se disponíveis)
3. ⚠️ Notifica para atualização manual

## Monitoramento

### Verificar Status do Workflow

```bash
# Via GitHub CLI
gh run list --workflow=sync-notebooklm.yml

# Ver logs específicos
gh run view <run-id>
```

### Verificar Outputs no Drive

Acesse: https://drive.google.com/drive/folders/1Eikf5MOwCNopr-FS976lheYlUprvWEx-

Procure pasta: `NotebookLM_Outputs/`

## Próximos Passos

1. Configure os secrets no GitHub
2. Ative o workflow
3. Teste com uma atualização do Claude
4. Verifique outputs no Drive
5. Ajuste frequência se necessário (atualmente 6 horas)

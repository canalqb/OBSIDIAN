# Obsidian → NotebookLM Pipeline v2.0

Pipeline de automação de conteúdo: agentes de IA enviam informações para o
`Obsidian_Master.txt`, o GitHub Actions sincroniza a cada 6 horas com o
NotebookLM que gera vídeo/áudio, salvando os resultados no Google Drive.

## Arquitetura

```
Agentes de IA (Claude, ChatGPT, Manus, n8n...)
        │
        ▼  (2 opções)
┌───────────────────────────┬──────────────────────────────┐
│  OPÇÃO A: GitHub API      │  OPÇÃO B: Flask API local    │
│  send_to_obsidian.py      │  obsidian_api.py :5000       │
│  • Funciona de qualquer   │  • Requer servidor rodando   │
│    lugar (nuvem ou local) │  • Bom para automações       │
│  • Dispara pipeline       │    locais (n8n, Zapier local)│
│    automaticamente        │                              │
└───────────────┬───────────┴──────────┬───────────────────┘
                │                      │
                ▼                      ▼
         Obsidian_Master.txt (Google Drive)
                │
                ▼
         GitHub Actions (a cada 6h ou push)
                │
                ├── check_changes.py   → detecta mudanças (modifiedTime)
                ├── sync_to_notebooklm.py → envia para NotebookLM
                ├── save_notebooklm_video.py → gera vídeo/áudio
                └── save_notebooklm_outputs.py → salva no Drive
```

## Estrutura de arquivos

```
obsidian-notebooklm-pipeline/
├── .github/workflows/
│   └── sync-notebooklm.yml      ← Pipeline CI/CD (6h + push)
├── scripts/
│   ├── drive_client.py          ← Cliente Google Drive centralizado (NOVO)
│   ├── logger.py                ← Logging estruturado JSONL (NOVO)
│   ├── send_to_obsidian.py      ← Envio via GitHub API — agentes externos (NOVO)
│   ├── add_to_obsidian.py       ← Envio via Drive — agentes locais
│   ├── obsidian_api.py          ← Flask REST API com auth + validação
│   ├── merge_notes.py           ← Mescla .md → Obsidian_Master.txt
│   ├── check_changes.py         ← Detecção de mudanças (modifiedTime)
│   ├── sync_to_notebooklm.py    ← Sync com NotebookLM
│   ├── save_notebooklm_video.py ← Geração de vídeo/áudio
│   └── save_notebooklm_outputs.py ← Salva outputs no Drive
├── google-apps-script/
│   └── Code.js                  ← Alternativa ao merge_notes.py (legado)
├── logs/                        ← Gerado automaticamente (ignorado no git)
│   ├── agent_activity.jsonl     ← Log de cada agente
│   └── pipeline_runs.jsonl      ← Log do pipeline
├── .env.example                 ← Template de variáveis de ambiente
├── .gitignore
├── requirements.txt
└── README.md
```

## Configuração inicial

### 1. Variáveis de ambiente

Copie `.env.example` para `.env` e preencha:

```bash
cp .env.example .env
```

Variáveis obrigatórias:

| Variável | Descrição |
|----------|-----------|
| `GOOGLE_CLIENT_ID` | OAuth Client ID do Google Cloud |
| `GOOGLE_CLIENT_SECRET` | OAuth Client Secret |
| `GOOGLE_REFRESH_TOKEN` | Token OAuth (gerado via `auth/generate_refresh_token.py`) |
| `OBSIDIAN_VAULT_FOLDER_ID` | ID da pasta do Obsidian no Google Drive |
| `NOTEBOOKLM_NOTEBOOK_ID` | ID do notebook no NotebookLM |
| `GITHUB_TOKEN` | PAT com permissão `contents:write` (para send_to_obsidian.py) |
| `GITHUB_REPO_OWNER` | Dono do repositório (ex: `canalqb`) |
| `GITHUB_REPO_NAME` | Nome do repositório (ex: `OBSIDIAN`) |
| `API_SECRET_KEY` | Chave aleatória para autenticar agentes na Flask API |

### 2. Secrets no GitHub

Adicione em **Settings → Secrets → Actions**:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REFRESH_TOKEN`
- `OBSIDIAN_VAULT_FOLDER_ID`
- `NOTEBOOKLM_NOTEBOOK_ID`
- `NOTEBOOKLM_OUTPUTS_FOLDER_ID`

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

Para NotebookLM (API não oficial — pode quebrar):
```bash
pip install notebooklm-py
```

## Como os agentes enviam conteúdo

### Opção A: Via GitHub API (recomendado para agentes externos)

Funciona de qualquer lugar, sem servidor local. O pipeline dispara automaticamente.

```bash
# Linha de comando
python scripts/send_to_obsidian.py \
  --content "Novo dado sobre Bitcoin: preço atingiu 100k" \
  --source "Claude"

# Lendo de arquivo
python scripts/send_to_obsidian.py --file pesquisa.md --source "Manus"

# Simulação (sem commit)
python scripts/send_to_obsidian.py --content "teste" --source "Dev" --dry-run
```

**Para agentes que usam chamadas HTTP diretas (n8n, Make, Zapier):**

```http
PUT https://api.github.com/repos/{owner}/{repo}/contents/Obsidian_Master.txt
Authorization: Bearer {GITHUB_TOKEN}
Content-Type: application/json

{
  "message": "feat(obsidian): [NomeAgente] adiciona conteúdo",
  "content": "<base64 do novo conteúdo>",
  "sha": "<sha atual do arquivo>"
}
```

### Opção B: Via Flask API local

Inicie o servidor:
```bash
python scripts/obsidian_api.py
# ou em produção:
gunicorn -w 2 -b 0.0.0.0:5000 scripts.obsidian_api:app
```

Endpoints:

```http
# Health check
GET http://localhost:5000/health

# Adicionar conteúdo (JSON)
POST http://localhost:5000/add
X-API-Key: {API_SECRET_KEY}
Content-Type: application/json

{"content": "Texto aqui", "source": "NomeAgente"}

# Adicionar conteúdo (texto puro)
POST http://localhost:5000/add/text
X-API-Key: {API_SECRET_KEY}
X-Source: NomeAgente

Texto aqui

# Ver logs de atividade
GET http://localhost:5000/logs?limit=20

# Ver estatísticas por agente
GET http://localhost:5000/stats
```

### Opção C: Via linha de comando (local)

```bash
python scripts/add_to_obsidian.py \
  --content "Pesquisa sobre airdrops: projeto X tem 50k usuários" \
  --source "CLI"
```

## Pipeline GitHub Actions

O workflow `sync-notebooklm.yml` executa:

1. **A cada 6 horas** (cron automático)
2. **A cada push** em `Obsidian_Master.txt` (quando agente usa Opção A)
3. **Manualmente** via GitHub Actions UI (com opção de forçar sync)

Etapas do pipeline:

| Etapa | Script | Falha crítica? |
|-------|--------|----------------|
| Detectar mudanças | `check_changes.py` | Sim |
| Sync NotebookLM | `sync_to_notebooklm.py` | Não (continue-on-error) |
| Gerar Audio Overview | `save_notebooklm_video.py` | Não |
| Gerar Video Overview | `save_notebooklm_video.py` | Não |
| Salvar outputs | `save_notebooklm_outputs.py` | Não |
| Download media | `save_notebooklm_video.py` | Não |

As etapas de NotebookLM usam `continue-on-error: true` porque a API é não oficial.

## Monitoramento e logs

Todos os logs ficam em `logs/` (ignorado pelo git):

```bash
# Ver últimas ações dos agentes
tail -f logs/agent_activity.jsonl | python -m json.tool

# Ver runs do pipeline
cat logs/pipeline_runs.jsonl

# Via API
curl http://localhost:5000/logs?limit=50
curl http://localhost:5000/stats
```

Cada linha do log tem:
```json
{
  "ts": "2026-06-24T10:30:00+00:00",
  "source": "Claude",
  "status": "success",
  "chars_added": 342,
  "content_preview": "Pesquisa sobre Bitcoin...",
  "content_hash": "a1b2c3d4e5f6g7h8"
}
```

## Segurança

- Nunca commite credenciais reais — use `.env` (está no `.gitignore`)
- O arquivo `.env.example` contém apenas valores de exemplo
- A Flask API exige `X-API-Key` em todos os endpoints POST
- O `send_to_obsidian.py` valida conteúdo antes de commitar
- Anti-duplicata por hash SHA256 — bloqueia envios repetidos
- Limite de 100k chars por envio e 5MB para o arquivo total

## Limites

| Item | Limite |
|------|--------|
| Conteúdo por envio | 100.000 chars |
| Tamanho do Obsidian_Master.txt | 5 MB |
| Notas .md suportadas | 400+ (testado) |
| Palavras por fonte no NotebookLM | 500.000 |

## Referências

- [CanalQb](https://www.canalqb.com.br) — Canal de tecnologia e automação
- [NotebookLM](https://notebooklm.google.com)
- [Google Drive API](https://developers.google.com/drive)
- [GitHub Contents API](https://docs.github.com/en/rest/repos/contents)

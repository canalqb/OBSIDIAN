# Seção de Configuração para Post Blogger

## Conteúdo a ser adicionado ao post existente

---

## TL;DR:
- Sistema automatiza Claude → Obsidian → NotebookLM → Drive em 4 passos
- Fork do GitHub + 5 secrets = automação completa em 10 minutos
- GitHub Actions roda a cada 6 horas sem intervenção manual

---

## Como Configurar o Sistema Completo

A maioria configura errado desde o primeiro comando — e nem percebe. O erro não está no código. Está na ordem de execução — e levei 3 horas para perceber. Aqui no @CanalQb, validamos que seguir esta ordem exata evita 90% dos problemas.

### Passo 1: Fork do Repositório

1. Acesse: https://github.com/canalqb/OBSIDIAN
2. Clique em "Fork" no canto superior direito
3. Selecione sua conta como destino
4. Aguarde o fork ser criado (segundos)

### Passo 2: Configurar Secrets no GitHub

Vá para o seu repositório forkado → Settings → Secrets and variables → Actions → New repository secret

**5 Secrets Obrigatórios:**

```
GOOGLE_CLIENT_ID
- Valor: Seu Client ID do Google Cloud Console
- Como obter: Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client ID

GOOGLE_CLIENT_SECRET
- Valor: Seu Client Secret do Google Cloud Console
- Como obter: Mesmo local do Client ID

GOOGLE_REFRESH_TOKEN
- Valor: Seu Refresh Token OAuth
- Como obter: Execute o script scripts/auth/generate_refresh_token.py
- Importante: Este token permite renovação automática de acesso

OBSIDIAN_VAULT_FOLDER_ID
- Valor: 1Eikf5MOwCNopr-FS976lheYlUprvWEx-
- Este é o ID da pasta do Obsidian no Google Drive

NOTEBOOKLM_NOTEBOOK_ID
- Valor: 999a0463-0274-49fe-8fb7-f242338f4a2d
- Este é o ID do notebook existente no NotebookLM
```

### Passo 3: Ativar GitHub Actions

1. No seu repositório forkado, vá para "Actions"
2. Clique em "Sync Obsidian to NotebookLM"
3. Clique em "Enable workflow"
4. O workflow executará automaticamente a cada 6 horas

### Passo 4: Como Claude Alimenta o Sistema

**Opção A: Via API REST (Recomendado)**

```bash
# Iniciar API localmente
cd obsidian-notebooklm-pipeline
python scripts/obsidian_api.py

# Claude envia conteúdo para http://localhost:5000/add
```

**Opção B: Via CLI**

```bash
python scripts/add_to_obsidian.py --content "Seu conteúdo" --source "Claude Code"
```

### Passo 5: Fluxo Automatizado

```
Claude adiciona conteúdo → Obsidian_Master.txt atualizado
↓ (6 horas depois)
GitHub Actions detecta mudança (hash MD5)
↓
Sincroniza com NotebookLM (notebooklm-py)
↓
NotebookLM processa conteúdo
↓
Salva outputs no Drive (NotebookLM_Outputs/)
```

## Estrutura de Arquivos

```
obsidian-notebooklm-pipeline/
├── .github/workflows/
│   └── sync-notebooklm.yml    # Workflow GitHub Actions
├── scripts/
│   ├── add_to_obsidian.py      # Adiciona conteúdo via CLI
│   ├── obsidian_api.py         # API REST para agentes
│   ├── merge_notes.py          # Mescla notas (substitui Apps Script)
│   ├── check_changes.py        # Detecta mudanças via hash
│   ├── sync_to_notebooklm.py   # Sincroniza com NotebookLM
│   └── save_notebooklm_outputs.py # Salva outputs no Drive
├── docs/
│   ├── agentes_integracao.md   # Integração Claude, Ollama, ChatGPT, Manus
│   ├── workflow_automacao.md   # Guia completo de automação
│   └── exemplo_completo.md     # Exemplo prático
└── requirements.txt            # Dependências Python
```

## Troubleshooting

**Erro: "Variáveis OAuth não configuradas"**
- Verifique se os 3 secrets OAuth estão configurados no GitHub
- Local: Settings → Secrets and variables → Actions

**Erro: "Arquivo Obsidian_Master.txt não encontrado"**
- Execute manualmente: python scripts/auto_sync.py
- Isso criará o arquivo na pasta do Drive

**Workflow não executa automaticamente**
- Verifique se está habilitado: Actions → Sync Obsidian to NotebookLM → Enable workflow
- Verifique se os secrets estão configurados corretamente

**notebooklm-py falha**
- É uma API não oficial (engenharia reversa)
- Se falhar, use extensão NotebookLM Tools (Chrome) manualmente
- O sistema ainda salva outputs mesmo se a sincronização falhar

## Segurança

- ✅ Credenciais nunca são commitadas no repositório
- ✅ Apenas placeholders em arquivos de exemplo
- ✅ Secrets são armazenados criptografados no GitHub
- ✅ API REST roda localmente (localhost)
- ✅ .gitignore bloqueia arquivos sensíveis

## Próximos Passos

1. Fork do repositório
2. Configure os 5 secrets no GitHub
3. Ative o workflow
4. Teste adicionando conteúdo via Claude
5. Verifique outputs no Drive após 6 horas

O sistema está pronto para automação completa. Claude alimenta, GitHub processa, NotebookLM analisa, Drive armazena — tudo sem intervenção manual.

# Seção de Configuração - Formato Texto para Blogger

## Copie e cole este conteúdo no seu post existente

---

🔧 Como Configurar o Sistema Completo

A maioria configura errado desde o primeiro comando — e nem percebe. O erro não estava no código. Estava na ordem de execução — e levei 3 horas para perceber. Aqui no @CanalQb, validamos que seguir esta ordem exata evita 90% dos problemas.

**Passo 1: Fork do Repositório**

Acesse https://github.com/canalqb/OBSIDIAN, clique em "Fork" no canto superior direito e selecione sua conta. O processo leva segundos.

**Passo 2: Configurar Secrets no GitHub**

Vá para o seu repositório forkado → Settings → Secrets and variables → Actions → New repository secret. Configure estes 5 secrets obrigatórios:

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

**Passo 3: Ativar GitHub Actions**

No seu repositório forkado, vá para "Actions", clique em "Sync Obsidian to NotebookLM", depois em "Enable workflow". O workflow executará automaticamente a cada 6 horas. Você também pode executar manualmente clicando em "Run workflow" para testar.

**Passo 4: Como Claude Alimenta o Sistema**

Você tem duas opções:

Opção A - Via API REST (Recomendada):
- Inicie a API localmente com: python scripts/obsidian_api.py
- Claude envia conteúdo para: http://localhost:5000/add

Opção B - Via CLI:
- Execute: python scripts/add_to_obsidian.py --content "Seu conteúdo" --source "Claude Code"

**Passo 5: Fluxo Automatizado**

O sistema funciona em 5 etapas:

1. Claude adiciona conteúdo → Obsidian_Master.txt atualizado
2. 6 horas depois → GitHub Actions detecta mudança (hash MD5)
3. Sincroniza com NotebookLM (notebooklm-py)
4. NotebookLM processa conteúdo
5. Salva outputs no Drive (NotebookLM_Outputs/)

Tudo acontece sem intervenção manual.

⚠️ Importante: Credenciais nunca são commitadas no repositório. Apenas placeholders em arquivos de exemplo. Secrets são armazenados criptografados no GitHub. O repositório público contém apenas dados seguros.

---

## Perguntas para Adicionar ao FAQ

**Como fazer fork do repositório corretamente?**

Acesse https://github.com/canalqb/OBSIDIAN, clique em "Fork" no canto superior direito e selecione sua conta. Isso cria uma cópia do repositório na sua conta GitHub que você pode personalizar sem afetar o original. O processo leva segundos.

**Quais secrets são obrigatórios no GitHub?**

Você precisa configurar 5 secrets: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN (obtidos do Google Cloud Console), OBSIDIAN_VAULT_FOLDER_ID (1Eikf5MOwCNopr-FS976lheYlUprvWEx-) e NOTEBOOKLM_NOTEBOOK_ID (999a0463-0274-49fe-8fb7-f242338f4a2d). Configure em Settings → Secrets and variables → Actions.

**Posso alterar a frequência de execução do GitHub Actions?**

Sim. Edite o arquivo .github/workflows/sync-notebooklm.yml no seu fork. A linha cron: '0 */6 * * *' define a frequência atual (6 horas). Você pode mudar para '0 */1 * * *' (1 hora), '0 */12 * * *' (12 horas) ou qualquer outra frequência. Veja crontab.guru para ajuda com sintaxe cron.

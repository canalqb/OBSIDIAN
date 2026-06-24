# Seção para Adicionar ao Post Existente

## Adicione esta seção após o conteúdo atual do post

---

<div style="background:#f8f9fa;border-left:4px solid #28a745;padding:20px;border-radius:8px;margin:30px 0">
<h3 style="margin:0 0 15px 0;color:#333;font-size:1.1em">🔧 Como Configurar o Sistema Completo</h3>
</div>

<p>A maioria configura errado desde o primeiro comando — e nem percebe. O erro não estava no código. Estava na ordem de execução — e levei 3 horas para perceber. Aqui no @CanalQb, validamos que seguir esta ordem exata evita 90% dos problemas.</p>

<h3 style="color:#333;margin:25px 0 15px 0">Passo 1: Fork do Repositório</h3>
<p>Acesse <a href="https://github.com/canalqb/OBSIDIAN" target="_blank" rel="noopener noreferrer">https://github.com/canalqb/OBSIDIAN</a>, clique em "Fork" no canto superior direito e selecione sua conta. O processo leva segundos.</p>

<h3 style="color:#333;margin:25px 0 15px 0">Passo 2: Configurar Secrets no GitHub</h3>
<p>Vá para o seu repositório forkado → Settings → Secrets and variables → Actions → New repository secret. Configure estes 5 secrets obrigatórios:</p>

<div class="post_cqb_codeblock">
<strong>GOOGLE_CLIENT_ID</strong>
- Valor: Seu Client ID do Google Cloud Console
- Como obter: Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client ID

<strong>GOOGLE_CLIENT_SECRET</strong>
- Valor: Seu Client Secret do Google Cloud Console
- Como obter: Mesmo local do Client ID

<strong>GOOGLE_REFRESH_TOKEN</strong>
- Valor: Seu Refresh Token OAuth
- Como obter: Execute o script scripts/auth/generate_refresh_token.py
- Importante: Este token permite renovação automática de acesso

<strong>OBSIDIAN_VAULT_FOLDER_ID</strong>
- Valor: 1Eikf5MOwCNopr-FS976lheYlUprvWEx-
- Este é o ID da pasta do Obsidian no Google Drive

<strong>NOTEBOOKLM_NOTEBOOK_ID</strong>
- Valor: 999a0463-0274-49fe-8fb7-f242338f4a2d
- Este é o ID do notebook existente no NotebookLM
</div>

<h3 style="color:#333;margin:25px 0 15px 0">Passo 3: Ativar GitHub Actions</h3>
<p>No seu repositório forkado, vá para "Actions", clique em "Sync Obsidian to NotebookLM", depois em "Enable workflow". O workflow executará automaticamente a cada 6 horas. Você também pode executar manualmente clicando em "Run workflow" para testar.</p>

<h3 style="color:#333;margin:25px 0 15px 0">Passo 4: Como Claude Alimenta o Sistema</h3>
<p>Você tem duas opções. A primeira é via API REST, que é a mais recomendada. Inicie a API localmente com <code>python scripts/obsidian_api.py</code> e Claude envia conteúdo para <code>http://localhost:5000/add</code>. A segunda opção é via CLI com <code>python scripts/add_to_obsidian.py --content "Seu conteúdo" --source "Claude Code"</code>.</p>

<h3 style="color:#333;margin:25px 0 15px 0">Passo 5: Fluxo Automatizado</h3>
<p>O sistema funciona em 5 etapas. Primeiro, Claude adiciona conteúdo e o Obsidian_Master.txt é atualizado. Seis horas depois, GitHub Actions detecta a mudança usando hash MD5. Em seguida, sincroniza com NotebookLM usando notebooklm-py. O NotebookLM processa o conteúdo. Finalmente, salva os outputs no Drive na pasta NotebookLM_Outputs/. Tudo acontece sem intervenção manual.</p>

<div style="background:rgba(255,193,7,0.15);border-left:4px solid #ffc107;padding:15px;border-radius:8px;color:#555;font-size:0.9em;margin:20px 0">
  <i class="fas fa-triangle-exclamation"></i> <strong>Importante:</strong>
  Credenciais nunca são commitadas no repositório. Apenas placeholders em arquivos de exemplo. Secrets são armazenados criptografados no GitHub. O repositório público contém apenas dados seguros.
</div>

---

## Adicione estas perguntas ao FAQ existente

<div class="post_faq_item">
  <h3 class="post_faq_question" role="button" aria-expanded="false" tabindex="0">
    <span>Como fazer fork do repositório corretamente?</span>
    <i class="fas fa-plus post_faq_icon" aria-hidden="true"></i>
  </h3>
  <div class="post_faq_answer" aria-hidden="true"><p>Acesse https://github.com/canalqb/OBSIDIAN, clique em "Fork" no canto superior direito e selecione sua conta. Isso cria uma cópia do repositório na sua conta GitHub que você pode personalizar sem afetar o original. O processo leva segundos.</p></div>
</div>

<div class="post_faq_item">
  <h3 class="post_faq_question" role="button" aria-expanded="false" tabindex="0">
    <span>Quais secrets são obrigatórios no GitHub?</span>
    <i class="fas fa-plus post_faq_icon" aria-hidden="true"></i>
  </h3>
  <div class="post_faq_answer" aria-hidden="true"><p>Você precisa configurar 5 secrets: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN (obtidos do Google Cloud Console), OBSIDIAN_VAULT_FOLDER_ID (1Eikf5MOwCNopr-FS976lheYlUprvWEx-) e NOTEBOOKLM_NOTEBOOK_ID (999a0463-0274-49fe-8fb7-f242338f4a2d). Configure em Settings → Secrets and variables → Actions.</p></div>
</div>

<div class="post_faq_item">
  <h3 class="post_faq_question" role="button" aria-expanded="false" tabindex="0">
    <span>Posso alterar a frequência de execução do GitHub Actions?</span>
    <i class="fas fa-plus post_faq_icon" aria-hidden="true"></i>
  </h3>
  <div class="post_faq_answer" aria-hidden="true"><p>Sim. Edite o arquivo .github/workflows/sync-notebooklm.yml no seu fork. A linha cron: '0 */6 * * *' define a frequência atual (6 horas). Você pode mudar para '0 */1 * * *' (1 hora), '0 */12 * * *' (12 horas) ou qualquer outra frequência. Veja crontab.guru para ajuda com sintaxe cron.</p></div>
</div>

---

## Atualize o JSON-LD FAQPage adicionando estas perguntas:

```json
{ "@type": "Question", "name": "Como fazer fork do repositório corretamente?", "acceptedAnswer": { "@type": "Answer", "text": "Acesse https://github.com/canalqb/OBSIDIAN, clique em Fork no canto superior direito e selecione sua conta. Isso cria uma cópia do repositório na sua conta GitHub." } },
{ "@type": "Question", "name": "Quais secrets são obrigatórios no GitHub?", "acceptedAnswer": { "@type": "Answer", "text": "Você precisa configurar 5 secrets: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN, OBSIDIAN_VAULT_FOLDER_ID e NOTEBOOKLM_NOTEBOOK_ID." } },
{ "@type": "Question", "name": "Posso alterar a frequência de execução do GitHub Actions?", "acceptedAnswer": { "@type": "Answer", "text": "Sim. Edite o arquivo .github/workflows/sync-notebooklm.yml no seu fork e altere a linha cron." } }
```

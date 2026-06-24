"""
Blogger Post Updater
Atualiza post do Blogger com documentação do projeto
"""

import os
from google.oauth2 import credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Configurações
BLOG_ID = "5982274115355506187"
POST_ID = "6744117048720374259"

def get_blogger_service():
    """Retorna serviço do Blogger autenticado"""
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
    
    creds = credentials.Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=['https://www.googleapis.com/auth/blogger']
    )
    
    creds.refresh(Request())
    
    return build('blogger', 'v3', credentials=creds)

def get_post_content(blog_id, post_id):
    """Lê conteúdo atual do post"""
    service = get_blogger_service()
    
    post = service.posts().get(
        blogId=blog_id,
        postId=post_id,
        view='ADMIN'
    ).execute()
    
    return post.get('content', '')

def update_post_content(blog_id, post_id, new_content):
    """Atualiza conteúdo do post"""
    service = get_blogger_service()
    
    # Primeiro obtém o post atual para preservar outros campos
    post = service.posts().get(
        blogId=blog_id,
        postId=post_id,
        view='ADMIN'
    ).execute()
    
    # Atualiza apenas o conteúdo
    post['content'] = new_content
    
    updated_post = service.posts().update(
        blogId=blog_id,
        postId=post_id,
        body=post
    ).execute()
    
    return updated_post

def generate_project_documentation():
    """Gera documentação do projeto para adicionar ao post"""
    doc = """
    
---

## 🚀 Projeto GitHub: Obsidian NotebookLM Pipeline

Repositório completo com scripts Python para automação do pipeline: https://github.com/canalqb/OBSIDIAN

### 📦 Estrutura do Projeto

```
obsidian-notebooklm-pipeline/
├── google-apps-script/
│   └── Code.js                    # Script Google Apps Script para mesclagem
├── scripts/
│   ├── auth/
│   │   ├── google_service_account.py    # Autenticação Service Account (leitura)
│   │   ├── google_oauth_token.py        # Gerador de token OAuth
│   │   └── generate_refresh_token.py   # Script simplificado para gerar refresh token
│   ├── obsidian_to_notebooklm.py        # Pipeline principal Python
│   └── test_credentials.py             # Teste de credenciais
├── docs/
│   └── configuracoes.txt                # Documentação de configuração
├── .env.example                         # Template de variáveis de ambiente
├── config.example.txt                   # Template de configuração
├── requirements.txt                     # Dependências Python
├── README.md                            # Documentação completa
└── LICENSE                              # Licença MIT
```

### 🔐 Autenticação Dual

O projeto implementa autenticação dual para máxima segurança:

- **Service Account**: Para leitura de dados do Google Drive, Blogger, YouTube
- **OAuth 2.0**: Para gravação de arquivos no Google Drive

### 📋 GitHub Secrets Obrigatórios

Configure os seguintes secrets em https://github.com/canalqb/OBSIDIAN/settings/secrets/actions:

1. `GOOGLE_CLIENT_ID` - Client ID do Google OAuth
2. `GOOGLE_CLIENT_SECRET` - Client Secret do Google OAuth
3. `GOOGLE_PROJECT_ID` - ID do projeto Google Cloud
4. `GOOGLE_SERVICE_ACCOUNT_EMAIL` - Email da Service Account
5. `GOOGLE_PRIVATE_KEY_ID` - ID da chave privada da Service Account
6. `GOOGLE_PRIVATE_KEY` - Chave privada completa da Service Account
7. `GOOGLE_API_KEY` - API Key do Google para Drive, Blogger, YouTube
8. `GOOGLE_REFRESH_TOKEN` - Refresh token OAuth 2.0
9. `OBSIDIAN_VAULT_FOLDER_ID` - ID da pasta do Obsidian no Google Drive
10. `NOTEBOOKLM_NOTEBOOK_ID` - ID do notebook no NotebookLM

### 🛠️ Como Usar

#### 1. Clone o repositório
```bash
git clone https://github.com/canalqb/OBSIDIAN.git
cd obsidian-notebooklm-pipeline
```

#### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

#### 3. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite .env com suas credenciais
```

#### 4. Gere o refresh token OAuth
```bash
python scripts/auth/generate_refresh_token.py
```

#### 5. Execute o pipeline
```bash
python scripts/obsidian_to_notebooklm.py --folder-id <OBSIDIAN_VAULT_FOLDER_ID>
```

### 📝 Scripts Disponíveis

#### `scripts/auth/google_service_account.py`
Autenticação usando Google Service Account para leitura de dados.

#### `scripts/auth/google_oauth_token.py`
Gerador de tokens OAuth 2.0 para autenticação de usuário.

#### `scripts/auth/generate_refresh_token.py`
Script simplificado para gerar refresh token OAuth.

#### `scripts/obsidian_to_notebooklm.py`
Pipeline principal que:
- Lê notas do Obsidian usando Service Account
- Mescla notas em único arquivo TXT
- Grava no Google Drive usando OAuth

#### `scripts/test_credentials.py`
Testa todas as credenciais configuradas.

### 🔧 Google Apps Script

O script `google-apps-script/Code.js` contém a função `mesclarObsidianParaTxt()` que:
- Percorre todas as subpastas do vault
- Une arquivos .md em único .txt
- Salva/atualiza no Google Drive
- Inclui funções de teste e estatísticas

### 📚 Documentação Completa

- `README.md` - Visão geral, instalação, configuração e uso
- `docs/configuracoes.txt` - Documentação detalhada de configuração
- `config.example.txt` - Template de configuração
- `.env.example` - Template de variáveis de ambiente

### 🎯 Status do Projeto

- ✅ Estrutura do repositório criada
- ✅ Google Apps Script implementado
- ✅ Scripts Python de autenticação criados
- ✅ Pipeline principal implementado
- ✅ Documentação completa
- ✅ GitHub Secrets documentados
- ✅ Publicado no GitHub

### 🔗 Links Úteis

- Repositório GitHub: https://github.com/canalqb/OBSIDIAN
- Artigo original: https://www.canalqb.com.br/2026/06/seo-claude-code-notebooklm-obsidian.html
- Google Cloud Console: https://console.cloud.google.com
- Google Apps Script: https://script.google.com
- NotebookLM: https://notebooklm.google.com

"""
    return doc

if __name__ == "__main__":
    print("="*70)
    print("📝 BLOGGER POST UPDATER")
    print("="*70)
    
    # Lê conteúdo atual
    print("\n📖 Lendo conteúdo atual do post...")
    current_content = get_post_content(BLOG_ID, POST_ID)
    print(f"✅ Conteúdo atual lido ({len(current_content)} caracteres)")
    
    # Gera nova documentação
    print("\n📝 Gerando documentação do projeto...")
    new_doc = generate_project_documentation()
    print(f"✅ Documentação gerada ({len(new_doc)} caracteres)")
    
    # Atualiza post
    print("\n💾 Atualizando post no Blogger...")
    updated_content = current_content + new_doc
    
    try:
        updated_post = update_post_content(BLOG_ID, POST_ID, updated_content)
        print(f"✅ Post atualizado com sucesso!")
        print(f"   URL: {updated_post.get('url', 'N/A')}")
        print(f"   Tamanho: {len(updated_content)} caracteres")
    except Exception as e:
        print(f"❌ Erro ao atualizar post: {e}")

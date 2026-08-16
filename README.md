# OBSIDIAN - Pipeline para Google Drive + NotebookLM

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

Pipeline completo para sincronização de notas Obsidian com Google Drive, NotebookLM e geração automática de vídeos via YouTube.

## 📋 Tabela de Arquivos

| Categoria | Arquivo | Descrição | Status |
|-----------|---------|-----------|--------|
| **Configuração** | `.env.example` | Template de variáveis de ambiente | ✅ |
| | `config.example.txt` | Documentação de configuração completa | ✅ |
| | `requirements.txt` | Dependências Python | ✅ |
| | `.gitignore` | Arquivos a ignorar no Git | ✅ |
| **README** | `README.md` | Este arquivo | ✅ |
| **Scripts Principais** | `pipeline_orchestrator.py` | Orquestrador principal do pipeline | ✅ |
| | `send_to_obsidian.py` | Envio de conteúdo via GitHub API | ✅ |
| | `obsidian_api.py` | API REST para agentes externos | ✅ |
| | `merge_notes.py` | Mescla notas em Obsidian_Master.txt | ✅ |
| | `auto_sync.py` | Sincronização automática | ✅ |
| **Google API** | `blogger_client.py` | Cliente API Blogger | ✅ |
| | `youtube_uploader.py` | Upload de vídeos YouTube | ✅ |
| | `sheets_client.py` | Cliente Google Sheets | ✅ |
| | `drive_client.py` | Cliente Google Drive | ✅ |
| **Utils** | `logger.py` | Sistema de logging centralizado | ✅ |
| | `check_pending_post.py` | Verifica posts pendentes | ✅ |
| | `test_credentials.py` | Testa credenciais | ✅ |
| **GitHub Actions** | `.github/workflows/sync-notebooklm.yml` | Workflow CI/CD | ✅ |
| **Documentação** | `docs/agentes_integracao.md` | Integração de agentes | ✅ |
| | `docs/workflow_automacao.md` | Fluxo de automação | ✅ |
| | `docs/exemplo_completo.md` | Exemplo completo | ✅ |
| | `docs/primeira_pesquisa.md` | Primeira pesquisa | ✅ |
| | `docs/pclaude.md` | Prompt mestre | ✅ |
| **Google Apps Script** | `google-apps-script/Code.js` | Script de mesclagem | ✅ |
| **Output** | `Obsidian_Master.txt` | Arquivo master de saída | ✅ |

## 🚀 Roadmap de Implementação

### Fase 1: Configuração Inicial ✅
- [x] Estrutura do projeto criada
- [x] Scripts principais funcionalmente testados
- [x] Integração com APIs do Google (Blogger, Drive, Sheets, YouTube)
- [x] API REST para agentes externos
- [x] GitHub Actions workflow configurado

### Fase 2: Dockerização ✅
- [x] Dockerfile criado
- [x] docker-compose.yml configurado
- [ ] Imagem Docker disponível
- [ ] Testes de containerização

### Fase 3: Otimização
- [ ] Cache de dependências
- [ ] Health checks
- [ ] Monitoramento
- [ ] Performance tuning

### Fase 4: Extensão
- [ ] Suporte a outras plataformas
- [ ] Webhooks adicionais
- [ ] Dashboard web
- [ ] Documentação em API

## 🧰 Novas Tecnologias Sugeridas

### Containerização
| Tecnologia | Uso | Benefícios |
|------------|-----|------------|
| **Docker** | Containerização do ambiente | Isolamento, portabilidade, replicabilidade |
| **Docker Compose** | Orquestração de serviços | Múltiplos containers, fácil deploy |
| **Gunicorn** | Servidor WSGI para Flask | Produção, múltiplas workers |

### Monitoramento
| Tecnologia | Uso | Benefícios |
|------------|-----|------------|
| **Prometheus** | Métricas do sistema | Monitoramento em tempo real |
| **Grafana** | Visualização de métricas | Dashboards customizados |
| **Sentry** | Tracking de erros | Debug avançado |

### CI/CD
| Tecnologia | Uso | Benefícios |
|------------|-----|------------|
| **GitHub Actions** | CI/CD atual | Já implementado |
| **Docker Hub** | Armazenamento de imagens | Deploy facilitado |
| **Railway/Render** | Deploy gratuito | Hosting simples |

### Infraestrutura
| Tecnologia | Uso | Benefícios |
|------------|-----|------------|
| **ngrok** | Túnel HTTPS | API acessível publicamente |
| **Caddy** | Reverse Proxy | SSL automático |
| **Redis** | Cache | Performance |

## 📦 Instalação

### Pré-requisitos
- Python 3.11+
- pip ou uv
- Conta Google com acesso ao Drive, Blogger, Sheets, YouTube
- GitHub account

### Passo a Passo

```bash
# 1. Clonar o repositório
git clone https://github.com/canalqb/OBSIDIAN.git
cd OBSIDIAN

# 2. Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.\.venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt
# ou com uv (mais rápido)
uv pip install -r requirements.txt

# 4. Configurar .env
cp .env.example .env
# Editar .env com suas credenciais

# 5. Gerar credenciais OAuth
python scripts/auth/generate_refresh_token.py

# 6. Testar configuração
python scripts/test_credentials.py

# 7. Iniciar API (opcional)
python scripts/obsidian_api.py
```

## 🏃‍♂️ Uso

### Opção 1: Usando a API REST (Recomendado)

```bash
# Iniciar a API
python scripts/obsidian_api.py

# Adicionar conteúdo via curl
curl -X POST http://localhost:5000/add \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua_chave_api" \
  -d '{"content": "Sua pesquisa sobre IA", "source": "Claude Code"}'
```

### Opção 2: Via CLI

```bash
# Adicionar conteúdo
python scripts/add_to_obsidian.py --content "Pesquisa sobre IA" --source "Claude Code"

# Merge de notas
python scripts/merge_notes.py --folder-id 1Eikf5MOwCNopr-FS976lheYlUprvWEx-

# Sync automático
python scripts/auto_sync.py --folder-id 1Eikf5MOwCNopr-FS976lheYlUprvWEx-
```

### Opção 3: Via GitHub Actions

1. Configure os secrets no GitHub:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_REFRESH_TOKEN`
   - `OBSIDIAN_VAULT_FOLDER_ID`
   - `NOTEBOOKLM_NOTEBOOK_ID`
   - `API_SECRET_KEY`

2. Acesse: https://github.com/canalqb/OBSIDIAN/actions
3. Execute o workflow `Sync Obsidian to NotebookLM`

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```bash
# Google OAuth
GOOGLE_CLIENT_ID=seu_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=seu_client_secret
GOOGLE_REFRESH_TOKEN=seu_refresh_token

# URLs
GOOGLE_REDIRECT_URI=http://localhost

# Pastas do Drive
OBSIDIAN_VAULT_FOLDER_ID=seu_pasta_obsidian_id

# NotebookLM
NOTEBOOKLM_NOTEBOOK_ID=seu_notebook_id

# Segurança
API_SECRET_KEY=sua_chave_aleatoria_min_32_caracteres
```

## 📊 Arquitetura

```
┌─────────────┐     POST    ┌──────────────┐     Push    ┌────────────────┐
│  Agente AI  │────────────▶│  API Flask   │────────────▶│ GitHub repo    │
│ (Claude)    │             │ (localhost)  │             │ Obsidian_*.txt │
└─────────────┘             └──────────────┘             └────────────────┘
                                                              │
                                                              ▼
                                                  ┌──────────────────────┐
                                                  │ GitHub Actions       │
                                                  │ (sync-notebooklm.yml)│
                                                  └──────────────────────┘
                                                              │
                     ┌──────────────────────────────────────────┼──────────────────────────────────────────┐
                     ▼                                          ▼                                          ▼
           ┌─────────────────┐                        ┌──────────────────┐                  ┌──────────────────┐
           │ NotebookLM API  │                        │  Drive API         │                  │ YouTube API      │
           │ (video gen)     │                        │  (save outputs)    │                  │ (upload)         │
           └─────────────────┘                        └──────────────────┘                  └──────────────────┘
                     │                                          │                                          │
                     ▼                                          ▼                                          ▼
           ┌─────────────────┐                        ┌──────────────────┐                  ┌──────────────────┐
           │ Video MP4       │─────────────────────────▶│ Drive (temp)       │──────────────────▶│ YouTube          │
           └─────────────────┘                        └──────────────────┘                  └──────────────────┘
                                                                  │
                                                                  ▼
                                                      ┌──────────────────┐
                                                      │ Update post with │
                                                      │ YouTube embed    │
                                                      └──────────────────┘
```

## 🧪 Testes

```bash
# Testar credenciais
python scripts/test_credentials.py

# Testar API (em outro terminal)
python scripts/obsidian_api.py
curl http://localhost:5000/health

# Testar upload
python scripts/youtube_uploader.py --file video.mp4 --title "Teste" --privacy private
```

## 📈 Métricas

O sistema registra automaticamente:
- Número de posts processados
- Tempo de execução
- Status de cada etapa
- Cache de conteúdo para evitar duplicatas

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-feature`
3. Faça commit das mudanças: `git commit -m 'Nova feature'`
4. Push para a branch: `git push origin feature/nova-feature`
5. Abra um Pull Request

## 📜 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📢 Créditos

- **Desenvolvedor:** CanalQb
- **Blog:** https://canalqb.com.br
- **YouTube:** @CanalQb
- **Documentação:** https://www.canalqb.com.br/2026/06/seo-claude-code-notebooklm-obsidian.html

## 🆘 Suporte

- Abra um issue no GitHub
- Consulte a documentação em `/docs`
- Visite: https://canalqb.com.br
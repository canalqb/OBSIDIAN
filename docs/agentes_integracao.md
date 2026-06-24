# Integração de Agentes com Obsidian_Master.txt

## Visão Geral

Este documento mostra como diferentes agentes de IA podem alimentar o `Obsidian_Master.txt` automaticamente.

## Métodos de Integração

### 1. API REST (Recomendado)

A API REST permite que qualquer agente envie conteúdo via HTTP.

**Iniciar API:**
```bash
cd c:\Users\Qb\Desktop\obsidian\obsidian-notebooklm-pipeline
# Configure as variáveis de ambiente (veja configuracoes_pipeline.txt)
pip install flask
python scripts/obsidian_api.py
```

**Endpoint:**
```
POST http://localhost:5000/add
Content-Type: application/json

{
  "content": "Seu conteúdo aqui",
  "source": "Nome do Agente"
}
```

### 2. Script CLI

Uso direto via linha de comando:
```bash
python scripts/add_to_obsidian.py --content "Seu conteúdo" --source "Nome do Agente"
```

## Integração por Agente

### Claude Code (Anthropic)

**Via API REST:**
```python
import requests

def claude_to_obsidian(content):
    response = requests.post(
        'http://localhost:5000/add',
        json={
            'content': content,
            'source': 'Claude Code'
        }
    )
    return response.json()
```

**No prompt do Claude:**
```
Quando gerar conteúdo importante, use esta função para salvar no Obsidian:
- URL: http://localhost:5000/add
- Método: POST
- Body: {"content": "seu conteúdo", "source": "Claude Code"}
```

### Ollama (Local)

**Via API REST:**
```bash
curl -X POST http://localhost:5000/add \
  -H "Content-Type: application/json" \
  -d '{"content": "Conteúdo do Ollama", "source": "Ollama"}'
```

**No prompt do Ollama:**
```
Quando terminar uma tarefa, envie o resultado para:
POST http://localhost:5000/add
Body: {"content": "resultado", "source": "Ollama"}
```

### ChatGPT (OpenAI)

**Via API REST:**
```python
import requests

def chatgpt_to_obsidian(content):
    response = requests.post(
        'http://localhost:5000/add',
        json={
            'content': content,
            'source': 'ChatGPT'
        }
    )
    return response.json()
```

**No prompt do ChatGPT:**
```
System: Você tem acesso a uma API local para salvar conteúdo no Obsidian.
Quando gerar insights importantes, use:
POST http://localhost:5000/add
Body: {"content": "insight", "source": "ChatGPT"}
```

### Manus AI

**Via API REST:**
```python
import requests

def manus_to_obsidian(content):
    response = requests.post(
        'http://localhost:5000/add',
        json={
            'content': content,
            'source': 'Manus AI'
        }
    )
    return response.json()
```

**No prompt do Manus:**
```
Use a função save_to_obsidian(content) para salvar resultados importantes.
Endpoint: http://localhost:5000/add
```

## Exemplos Práticos

### Exemplo 1: Pesquisa com Claude

```
Claude: Pesquise sobre "Inteligência Artificial em 2026"

Claude: [gera pesquisa detalhada]

Claude: Salvando pesquisa no Obsidian...
[POST para http://localhost:5000/add]
✅ Conteúdo salvo
```

### Exemplo 2: Análise com Ollama

```bash
ollama run llama2 "Analise este documento e resuma"
[Resultado]
curl -X POST http://localhost:5000/add \
  -d '{"content": "resumo", "source": "Ollama"}'
```

### Exemplo 3: Ideias com ChatGPT

```
ChatGPT: Gere 10 ideias para projeto

ChatGPT: [gera ideias]

ChatGPT: Salvando ideias no Obsidian...
[POST para http://localhost:5000/add]
✅ Conteúdo salvo
```

## Automação Avançada

### Webhook para GitHub Actions

Crie um webhook que recebe eventos e salva no Obsidian:

```python
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    content = f"GitHub Event: {data}"
    add_content_to_obsidian(content, "GitHub Webhook")
    return jsonify({"status": "success"})
```

### Integração com NotebookLM

Após adicionar conteúdo, execute o sync:

```bash
python scripts/auto_sync.py --folder-id 1Eikf5MOwCNopr-FS976lheYlUprvWEx-
```

## Segurança

- A API roda localmente (localhost)
- Configure firewall para restringir acesso
- Use autenticação se expor publicamente
- Valide conteúdo antes de salvar

## Troubleshooting

**API não responde:**
```bash
# Verifique se a API está rodando
curl http://localhost:5000/health
```

**Erro de autenticação:**
```bash
# Configure variáveis de ambiente
$env:GOOGLE_CLIENT_ID="..."
$env:GOOGLE_CLIENT_SECRET="..."
$env:GOOGLE_REFRESH_TOKEN="..."
```

**Arquivo não encontrado:**
```bash
# Execute o sync primeiro
python scripts/auto_sync.py --folder-id 1Eikf5MOwCNopr-FS976lheYlUprvWEx-
```

## Próximos Passos

1. Inicie a API: `python scripts/obsidian_api.py`
2. Configure seus agentes para usar o endpoint
3. Teste com um agente
4. Execute sync para atualizar NotebookLM

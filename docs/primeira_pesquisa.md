# Guia para Primeira Pesquisa

## Sistema Atual (Caminho Gratuito)

Nosso sistema atual usa:
- Google Apps Script para mesclar notas do Obsidian
- NotebookLM para análise
- NotebookLM Tools (Chrome) para atualização

## Passo a Passo para Primeira Pesquisa

### 1. Preparação do Obsidian

Crie notas no Obsidian sobre o tema que deseja pesquisar:

```markdown
# Tópico de Pesquisa

## Perguntas Principais
- O que você quer descobrir?
- Quais são as dúvidas principais?

## Contexto
- Por que isso é importante?
- Qual o objetivo da pesquisa?

## Fontes
- Liste fontes conhecidas
- Adicione links relevantes
```

### 2. Sincronizar com Google Drive

Certifique-se que sua pasta do Obsidian está sincronizada com o Google Drive.

### 3. Executar Google Apps Script

Acesse [script.google.com](https://script.google.com) e execute a função `mesclarObsidianParaTxt()`.

Isso criará/atualizará o arquivo `Obsidian_Master.txt` no seu Google Drive.

### 4. Adicionar ao NotebookLM

1. Acesse [notebooklm.google.com](https://notebooklm.google.com)
2. Crie um novo notebook
3. Adicione o arquivo `Obsidian_Master.txt` do Google Drive como fonte

### 5. Realizar Pesquisa

No NotebookLM, faça perguntas sobre suas notas:

```
"Quais são os principais pontos sobre [tópico]?"
"Resuma as fontes mencionadas"
"Quais são as conexões entre as diferentes notas?"
```

### 6. Atualizar com NotebookLM Tools

Quando adicionar novas notas ao Obsidian:

1. Execute o Google Apps Script novamente
2. Use a extensão NotebookLM Tools no Chrome
3. Clique no botão de refresh para atualizar as fontes

## Exemplo Prático

### Tópico: "Inteligência Artificial em 2026"

#### 1. Criar notas no Obsidian

**Nota 1: Tendências de IA**
```markdown
# Tendências de IA em 2026

## Principais Tendências
- Agentes de IA autônomos
- IA multimodal
- Computação de borda

## Empresas Líderes
- OpenAI
- Google
- Anthropic
```

**Nota 2: Aplicações Práticas**
```markdown
# Aplicações Práticas de IA

## Setores
- Saúde
- Educação
- Finanças

## Casos de Uso
- Diagnóstico médico
- Tutoria personalizada
- Análise de risco
```

#### 2. Sincronizar e Executar Script

Execute o Google Apps Script para mesclar as notas.

#### 3. Adicionar ao NotebookLM

Adicione o `Obsidian_Master.txt` como fonte.

#### 4. Fazer Perguntas

```
"Quais são as principais tendências de IA em 2026?"
"Como a IA está sendo aplicada na saúde?"
"Quais empresas estão liderando o mercado?"
```

## Teste Automatizado com Python

Também podemos testar usando o script Python:

```bash
cd c:\Users\Qb\Desktop\obsidian\obsidian-notebooklm-pipeline
python scripts/obsidian_to_notebooklm.py --folder-id <OBSIDIAN_VAULT_FOLDER_ID>
```

Este script:
- Lê notas do Obsidian via Service Account
- Mescla em arquivo TXT
- Grava no Google Drive via OAuth

## Próximo Nível: Fluxo YouMind

Para o fluxo avançado do YouMind (Skill Creator + NotebookLM-py), veja `docs/youmind_workflow.md`.

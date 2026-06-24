# Fluxo de Trabalho Avançado - YouMind

Este documento descreve o fluxo de trabalho avançado baseado no artigo do YouMind para criar um sistema de pesquisa que fica mais inteligente a cada uso.

## A Pilha de Tecnologias

### 1. Skill Creator
- Ferramenta para criar skills personalizadas no Claude Code
- Permite automatizar tarefas repetitivas
- Modulariza o fluxo de trabalho

### 2. Skill de Pesquisa no YouTube
- Pesquisa automatizada no YouTube
- Coleta informações relevantes
- Transcrição e análise de vídeos

### 3. NotebookLM-py
- Wrapper Python para NotebookLM API
- Integração programática com NotebookLM
- Processamento de documentos em escala

### 4. Skill do NotebookLM
- Automação de análise de documentos
- Geração de insights e sínteses
- Citação automática de fontes

### 5. Skill de Pipeline Combinada
- Orquestra todas as skills
- Fluxo de trabalho end-to-end
- Persistência no Obsidian

## Diferença do Nosso Projeto Atual

**Nosso Projeto (Caminho Gratuito):**
- Google Apps Script para mesclagem
- NotebookLM Tools (Chrome)
- Sincronização manual

**Fluxo YouMind (Caminho Avançado):**
- Skills Claude Code
- NotebookLM-py (API)
- Automação completa

## Implementação Futura

Para implementar este fluxo avançado, precisaremos:

1. **Instalar Skill Creator**
   ```bash
   # Via Claude Code
   ```

2. **Criar Skill de Pesquisa YouTube**
   - Configurar busca por tópicos
   - Extrair transcrições
   - Salvar no Obsidian

3. **Instalar NotebookLM-py**
   ```bash
   pip install notebooklm-py
   ```

4. **Criar Skill NotebookLM**
   - Upload de documentos
   - Análise automática
   - Geração de respostas

5. **Pipeline Combinado**
   - Orquestrar todas as skills
   - Persistir resultados no Obsidian
   - Criar sistema de aprendizado

## Status Atual

- ✅ Google Apps Script implementado
- ✅ Autenticação Google configurada
- ✅ Scripts Python básicos criados
- ⏳ Skill Creator (pendente)
- ⏳ NotebookLM-py (pendente)
- ⏳ Skills avançadas (pendente)

## Próximos Passos

1. Testar fluxo básico atual
2. Implementar NotebookLM-py
3. Criar skills personalizadas
4. Integrar pipeline completo

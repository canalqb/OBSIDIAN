# Skill: Gerar Post para Blogger (@CanalQb)

## Quando usar

Use esta skill quando o usuario pedir para criar um post, artigo ou
conteudo para o blog canalqb.com.br.

## Template Obrigatorio

O HTML gerado deve seguir EXATAMENTE esta ordem:

### Bloco 1: Cabecalho Fixo
```html
<hr class="post_separator" style="border:0.5px solid #ccc;margin:10px auto;width:95%">
<p style="text-align:center">
  <a href="https://www.youtube.com/channel/UCdOA_1KzXHIp3gmVyyYv2sg" rel="noopener noreferrer" target="_blank" title="Visite o @CanalQb no YouTube" style="font-size:1.2em;font-weight:bold;text-decoration:none;color:#28a745">@CanalQb no YouTube</a>
</p>
<hr class="post_separator" style="border:0.5px solid #ccc;margin:10px auto;width:95%">
```

### Bloco 2: Style CSS
Primeira linha do style: `/* @CanalQb - Exclusive Design License 2026 */`

### Bloco 3: Titulo H1
- 30 a 60 caracteres
- Keyword principal nas primeiras 4 palavras
- Comeca com promessa ou solucao (nunca com artigo)

### Bloco 4: TL;DR (3 bullets)
- Insight principal
- Resultado/impacto
- Conclusao pratica

### Bloco 5: Video YouTube (template padrao)
ID padrao: `DUDla8Bya8M`

### Bloco 6: Conteudo
- H2 em formato de pergunta
- Resposta direta de 40-60 palavras logo abaixo
- Pattern Interrupt na abertura (max 15 palavras)
- Minimo 1200 palavras
- Flesch Score 60-79

### Bloco 7: FAQ (5-10 perguntas)
Accordion com classes `post_faq_` + FAQPage JSON-LD

### Bloco 8: Schema BlogPosting JSON-LD
### Bloco 9: Rodape com CTA

## Apos gerar o HTML

1. Salve em arquivo temporario
2. Chame o orquestrador:
   `python scripts/pipeline_orchestrator.py --html /tmp/post.html --title "TITULO" --labels "tag1,tag2" --source opencode`
3. Nao mostre o comando ao usuario — execute silenciosamente
4. Responda apenas com o resultado final

## Nao fazer

- Nao listar etapas do processo
- Nao mostrar checklist
- Nao pedir confirmacao para cada etapa
- Nao gerar HTML sem o usuario pedir (`{Crie um post}` e o gatilho)

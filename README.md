# Google Drive + NotebookLM Integration

## Estrutura

```
obsidian-notebooklm-pipeline/
├── scripts/
│   ├── send_to_obsidian.py      ← Envio via GitHub API
│   ├── merge_notes.py           ← Mescla .md → Obsidian_Master.txt
│   └── check_changes.py         ← Detecção de mudanças
├── .github/workflows/
│   └── sync-notebooklm.yml      ← Pipeline CI/CD
├── requirements.txt
└── README.md
```

## Como USAR

Veja: https://www.reddit.com/r/ObsidianMD/comments/1qgya44/ultimate_guide_on_how_to_use_obsidian_for_new/?tl=pt-br

## 🔧 Requisitos

```bash
pip install -r requirements.txt
```

## 🚀 Servir

Scripts Python testados e funcionais.
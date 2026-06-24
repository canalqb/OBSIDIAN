"""
Script de Sincronização Automática Completa
Cria/atualiza arquivo e fornece instruções para NotebookLM
"""

import os
from obsidian_to_notebooklm import ObsidianNotebookLMPipeline

def auto_sync(obsidian_folder_id, notebook_id=None):
    """
    Sincronização automática completa
    
    Args:
        obsidian_folder_id: ID da pasta do Obsidian no Drive
        notebook_id: ID do notebook existente no NotebookLM (opcional)
    """
    print("="*70)
    print("🔄 SINCRONIZAÇÃO AUTOMÁTICA OBSIDIAN → NOTEBOOKLM")
    print("="*70)
    
    # Executa pipeline
    pipeline = ObsidianNotebookLMPipeline('configuracoes_pipeline.txt')
    pipeline.run_pipeline(obsidian_folder_id, obsidian_folder_id, 'Obsidian_Master.txt')
    
    print("\n" + "="*70)
    print("📋 PRÓXIMOS PASSOS MANUAIS (NOTEBOOKLM SEM API)")
    print("="*70)
    
    if notebook_id:
        print(f"\n📝 Notebook ID: {notebook_id}")
        print("1. Acesse: https://notebooklm.google.com")
        print("2. Abra o notebook existente")
        print("3. Clique em 'Add source'")
        print("4. Selecione 'Google Drive'")
        print("5. Adicione o arquivo 'Obsidian_Master.txt' da pasta do Obsidian")
    else:
        print("\n1. Acesse: https://notebooklm.google.com")
        print("2. Crie ou abra seu notebook")
        print("3. Clique em 'Add source'")
        print("4. Selecione 'Google Drive'")
        print("5. Adicione o arquivo 'Obsidian_Master.txt'")
    
    print("\n💡 DICA: Use a extensão NotebookLM Tools (Chrome) para atualizar automaticamente")
    print("="*70)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto Sync Obsidian to NotebookLM')
    parser.add_argument('--folder-id', required=True, help='ID da pasta do Obsidian')
    parser.add_argument('--notebook-id', help='ID do notebook existente no NotebookLM')
    
    args = parser.parse_args()
    
    # Usa notebook ID do config se não especificado
    notebook_id = args.notebook_id if args.notebook_id else "999a0463-0274-49fe-8fb7-f242338f4a2d"
    
    auto_sync(args.folder_id, notebook_id)

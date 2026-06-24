"""
Script para sincronizar Obsidian_Master.txt com NotebookLM
Usa notebooklm-py (API não oficial) para atualizar fontes
"""

import os
from google.oauth2 import credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

def sync_to_notebooklm(folder_id, notebook_id):
    """
    Sincroniza Obsidian_Master.txt com NotebookLM
    
    Args:
        folder_id: ID da pasta do Obsidian no Drive
        notebook_id: ID do notebook no NotebookLM
    """
    print("🔄 Sincronizando com NotebookLM...")
    
    try:
        # Import notebooklm-py
        from notebooklm import NotebookLM
        
        # Configurações OAuth
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
        
        if not all([client_id, client_secret, refresh_token]):
            print("❌ Variáveis OAuth não configuradas")
            return False
        
        # Cria credenciais
        creds = credentials.Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        # Renova token
        creds.refresh(Request())
        
        # Conecta ao Drive para obter o arquivo
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Busca o arquivo Obsidian_Master.txt
        query = f"name='Obsidian_Master.txt' and '{folder_id}' in parents"
        results = drive_service.files().list(q=query).execute()
        files = results.get('files', [])
        
        if not files:
            print("❌ Arquivo Obsidian_Master.txt não encontrado")
            return False
        
        file_id = files[0]['id']
        
        # Inicializa NotebookLM
        nlm = NotebookLM()
        
        # Adiciona/atualiza fonte no notebook
        print(f"📝 Atualizando fonte no notebook {notebook_id}")
        nlm.add_source_to_notebook(
            notebook_id=notebook_id,
            source_type='drive',
            source_id=file_id
        )
        
        print("✅ Sincronização com NotebookLM concluída")
        return True
        
    except ImportError:
        print("⚠️ notebooklm-py não instalado. Execute: pip install notebooklm-py")
        print("💡 Alternativa: Use extensão NotebookLM Tools (Chrome) manualmente")
        return False
    except Exception as e:
        print(f"❌ Erro ao sincronizar com NotebookLM: {e}")
        print("💡 NotebookLM API não oficial pode ter mudado. Use extensão manualmente.")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Sincroniza com NotebookLM')
    parser.add_argument('--notebook-id', required=True, help='ID do notebook no NotebookLM')
    
    args = parser.parse_args()
    
    folder_id = os.getenv('OBSIDIAN_VAULT_FOLDER_ID')
    
    success = sync_to_notebooklm(folder_id, args.notebook_id)
    
    import sys
    sys.exit(0 if success else 1)

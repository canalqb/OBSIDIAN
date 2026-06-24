"""
Script para adicionar conteúdo ao Obsidian_Master.txt
Permite que agentes (Claude, Ollama, ChatGPT, Manus) alimentem o arquivo
"""

import os
import sys
from google.oauth2 import credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload
import io
from datetime import datetime

def add_content_to_obsidian(content, source="Unknown Agent", folder_id=None):
    """
    Adiciona conteúdo ao Obsidian_Master.txt no Google Drive
    
    Args:
        content: Conteúdo a ser adicionado
        source: Nome do agente/fonte
        folder_id: ID da pasta onde está o arquivo
    """
    # Configurações OAuth
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        print("❌ Variáveis OAuth não configuradas")
        return False
    
    try:
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
        
        # Conecta ao Drive
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Busca o arquivo Obsidian_Master.txt
        query = f"name='Obsidian_Master.txt'"
        if folder_id:
            query += f" and '{folder_id}' in parents"
        
        results = drive_service.files().list(q=query).execute()
        files = results.get('files', [])
        
        if not files:
            print("❌ Arquivo Obsidian_Master.txt não encontrado")
            return False
        
        file_id = files[0]['id']
        
        # Lê conteúdo atual
        request = drive_service.files().get_media(fileId=file_id)
        file_content = request.execute()
        
        current_content = file_content.decode('utf-8') if isinstance(file_content, bytes) else str(file_content)
        
        # Adiciona novo conteúdo
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_section = f"\n\n--- NOVO CONTEÚDO [{source}] - {timestamp} ---\n{content}\n"
        
        updated_content = current_content + new_section
        
        # Atualiza arquivo
        fh = io.BytesIO(updated_content.encode('utf-8'))
        media = MediaIoBaseUpload(
            fh,
            mimetype='text/plain',
            resumable=True
        )
        
        drive_service.files().update(
            fileId=file_id,
            media_body=media,
            fields='id'
        ).execute()
        
        print(f"✅ Conteúdo adicionado por {source}")
        print(f"   Tamanho: {len(updated_content)} caracteres")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar conteúdo: {e}")
        return False


def main():
    """Uso via linha de comando"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Adiciona conteúdo ao Obsidian_Master.txt')
    parser.add_argument('--content', required=True, help='Conteúdo a ser adicionado')
    parser.add_argument('--source', default='CLI', help='Nome do agente/fonte')
    parser.add_argument('--folder-id', default='1Eikf5MOwCNopr-FS976lheYlUprvWEx-', help='ID da pasta')
    
    args = parser.parse_args()
    
    success = add_content_to_obsidian(args.content, args.source, args.folder_id)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

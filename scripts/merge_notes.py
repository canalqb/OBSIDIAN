"""
Script Python que substitui Google Apps Script
Lê notas do Obsidian no Drive e mescla em arquivo TXT
"""

import os
from google.oauth2 import credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload
import io
from datetime import datetime


def merge_obsidian_notes(folder_id, output_filename='Obsidian_Master.txt'):
    """
    Mescla todas as notas .md do Obsidian em um único arquivo TXT
    
    Args:
        folder_id: ID da pasta do Obsidian no Drive
        output_filename: Nome do arquivo de saída
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
        
        print(f"📖 Lendo notas da pasta: {folder_id}")
        
        # Busca todos os arquivos .md recursivamente
        all_notes = []
        
        def list_files(folder_id, path=""):
            query = f"'{folder_id}' in parents and name contains '.md'"
            results = drive_service.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            
            for file in files:
                # Lê conteúdo do arquivo
                request = drive_service.files().get_media(fileId=file['id'])
                content = request.execute()
                
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                
                all_notes.append({
                    'name': file['name'],
                    'path': path,
                    'content': str(content)
                })
                print(f"   ✅ {file['name']}")
            
            # Busca subpastas
            query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder'"
            results = drive_service.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            
            for folder in folders:
                list_files(folder['id'], f"{path}{folder['name']}/")
        
        list_files(folder_id)
        
        if not all_notes:
            print("⚠️ Nenhuma nota .md encontrada")
            return False
        
        # Mescla conteúdo
        print(f"\n🔄 Mesclando {len(all_notes)} notas...")
        
        merged_content = f"EXPORT OBSIDIAN VAULT — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for note in all_notes:
            title = note['name'].replace('.md', '')
            content = note['content']
            path = note['path']
            
            merged_content += f"--- NOTA: {title} ({path}) ---\n"
            merged_content += f"{content}\n\n"
        
        print(f"✅ Conteúdo mesclado ({len(merged_content)} caracteres)")
        
        # Verifica se arquivo já existe
        query = f"name='{output_filename}' and '{folder_id}' in parents"
        results = drive_service.files().list(q=query).execute()
        existing_files = results.get('files', [])
        
        file_metadata = {
            'name': output_filename,
            'mimeType': 'text/plain',
            'parents': [folder_id]
        }
        
        # Usa MediaIoBaseUpload para upload direto
        fh = io.BytesIO(merged_content.encode('utf-8'))
        media = MediaIoBaseUpload(
            fh,
            mimetype='text/plain',
            resumable=True
        )
        
        if existing_files:
            # Atualiza arquivo existente
            file_id = existing_files[0]['id']
            drive_service.files().update(
                fileId=file_id,
                media_body=media,
                fields='id'
            ).execute()
            print(f"✅ Arquivo atualizado: {output_filename}")
        else:
            # Cria novo arquivo
            drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            print(f"✅ Arquivo criado: {output_filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao mesclar notas: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Mescla notas do Obsidian')
    parser.add_argument('--folder-id', required=True, help='ID da pasta do Obsidian')
    parser.add_argument('--output', default='Obsidian_Master.txt', help='Nome do arquivo de saída')
    
    args = parser.parse_args()
    
    success = merge_obsidian_notes(args.folder_id, args.output)
    
    if success:
        print("\n🎉 Processo concluído com sucesso!")
        print("💡 Execute o auto_sync para atualizar o NotebookLM")
    else:
        print("\n❌ Processo falhou")

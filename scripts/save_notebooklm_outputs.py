"""
Script para salvar outputs do NotebookLM no Google Drive
Captura respostas, áudios e outros outputs gerados
"""

import os
from google.oauth2 import credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload
import io
from datetime import datetime

def save_notebooklm_outputs(folder_id):
    """
    Salva outputs do NotebookLM no Drive
    
    Args:
        folder_id: ID da pasta onde salvar os outputs
    """
    print("💾 Salvando outputs do NotebookLM...")
    
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
        
        # Conecta ao Drive
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Inicializa NotebookLM
        nlm = NotebookLM()
        
        # Obtém notebook ID
        notebook_id = os.getenv('NOTEBOOKLM_NOTEBOOK_ID')
        
        if not notebook_id:
            print("❌ NOTEBOOKLM_NOTEBOOK_ID não configurado")
            return False
        
        # Obtém outputs do notebook
        print(f"📝 Obtendo outputs do notebook {notebook_id}")
        
        # Obtém todas as fontes e respostas
        notebook_data = nlm.get_notebook(notebook_id)
        
        # Cria pasta para outputs se não existir
        outputs_folder_name = "NotebookLM_Outputs"
        query = f"name='{outputs_folder_name}' and '{folder_id}' in parents and mimeType='application/vnd.google-apps.folder'"
        results = drive_service.files().list(q=query).execute()
        folders = results.get('files', [])
        
        if not folders:
            # Cria pasta
            folder_metadata = {
                'name': outputs_folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [folder_id]
            }
            folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
            outputs_folder_id = folder['id']
            print(f"📁 Pasta criada: {outputs_folder_name}")
        else:
            outputs_folder_id = folders[0]['id']
            print(f"📁 Pasta existente: {outputs_folder_name}")
        
        # Salva respostas como arquivos de texto
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if 'responses' in notebook_data:
            for i, response in enumerate(notebook_data['responses']):
                filename = f"response_{timestamp}_{i}.txt"
                content = f"Resposta {i+1}\n{'='*50}\n\n{response.get('text', '')}"
                
                file_metadata = {
                    'name': filename,
                    'mimeType': 'text/plain',
                    'parents': [outputs_folder_id]
                }
                
                fh = io.BytesIO(content.encode('utf-8'))
                media = MediaIoBaseUpload(fh, mimetype='text/plain', resumable=True)
                
                drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                
                print(f"✅ Salvo: {filename}")
        
        # Salva resumo do notebook
        summary_filename = f"summary_{timestamp}.txt"
        summary_content = f"NotebookLM Summary - {timestamp}\n{'='*50}\n\n"
        summary_content += f"Notebook ID: {notebook_id}\n"
        summary_content += f"Fontes: {len(notebook_data.get('sources', []))}\n"
        summary_content += f"Respostas: {len(notebook_data.get('responses', []))}\n\n"
        
        file_metadata = {
            'name': summary_filename,
            'mimeType': 'text/plain',
            'parents': [outputs_folder_id]
        }
        
        fh = io.BytesIO(summary_content.encode('utf-8'))
        media = MediaIoBaseUpload(fh, mimetype='text/plain', resumable=True)
        
        drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        print(f"✅ Salvo: {summary_filename}")
        print("✅ Outputs do NotebookLM salvos com sucesso")
        return True
        
    except ImportError:
        print("⚠️ notebooklm-py não instalado. Execute: pip install notebooklm-py")
        return False
    except Exception as e:
        print(f"❌ Erro ao salvar outputs: {e}")
        print("💡 NotebookLM API não oficial pode ter mudado. Verifique manualmente.")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Salva outputs do NotebookLM')
    parser.add_argument('--folder-id', required=True, help='ID da pasta do Obsidian')
    
    args = parser.parse_args()
    
    success = save_notebooklm_outputs(args.folder_id)
    
    import sys
    sys.exit(0 if success else 1)

import os
import asyncio
import io
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload

async def save_notebooklm_outputs(folder_id):
    print("Salvando outputs do NotebookLM...")
    try:
        from notebooklm import NotebookLMClient
    except ImportError:
        print("notebooklm-py nao instalado")
        return False
    auth_json = os.getenv('NOTEBOOKLM_AUTH_JSON')
    if auth_json:
        os.environ['NOTEBOOKLM_AUTH_JSON'] = auth_json
    try:
        async with NotebookLMClient.from_storage() as client:
            notebook_id = os.getenv('NOTEBOOKLM_NOTEBOOK_ID')
            if not notebook_id:
                print("NOTEBOOKLM_NOTEBOOK_ID nao configurado")
                return False
            nb = await client.notebooks.get(notebook_id)
            print("Notebook:", nb.id)
            client_id = os.getenv('GOOGLE_CLIENT_ID')
            client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
            refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
            if not all([client_id, client_secret, refresh_token]):
                print("Variaveis OAuth nao configuradas")
                return False
            creds = Credentials(
                token=None, refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id, client_secret=client_secret,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            creds.refresh(Request())
            drive_service = build('drive', 'v3', credentials=creds)
            outputs_folder_name = "NotebookLM_Outputs"
            query = "name='%s' and '%s' in parents and mimeType='application/vnd.google-apps.folder'" % (outputs_folder_name, folder_id)
            results = drive_service.files().list(q=query).execute()
            folders = results.get('files', [])
            if not folders:
                folder_metadata = {
                    'name': outputs_folder_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [folder_id]
                }
                folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
                outputs_folder_id = folder['id']
                print("Pasta criada:", outputs_folder_name)
            else:
                outputs_folder_id = folders[0]['id']
                print("Pasta existente:", outputs_folder_name)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            summary_content = "Notebook: %s\nNotebook ID: %s\nTimestamp: %s\n" % (nb.id, notebook_id, timestamp)
            fh = io.BytesIO(summary_content.encode('utf-8'))
            media = MediaIoBaseUpload(fh, mimetype='text/plain', resumable=True)
            file_metadata = {
                'name': 'summary_%s.txt' % timestamp,
                'mimeType': 'text/plain',
                'parents': [outputs_folder_id]
            }
            drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print("Outputs salvos com sucesso")
            return True
    except Exception as e:
        print("Erro ao salvar outputs:", str(e))
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder-id', required=True)
    args = parser.parse_args()
    success = asyncio.run(save_notebooklm_outputs(args.folder_id))
    import sys
    sys.exit(0 if success else 1)

import os
import asyncio
import io
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload

def get_drive_service():
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
    if not all([client_id, client_secret, refresh_token]):
        print("Variaveis OAuth nao configuradas")
        return None
    creds = Credentials(
        token=None, refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id, client_secret=client_secret,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    creds.refresh(Request())
    return build('drive', 'v3', credentials=creds)

async def save_notebooklm_artifacts_to_drive(notebook_id, drive_folder_id):
    print("Salvando outputs do NotebookLM no Drive...")
    try:
        from notebooklm import NotebookLMClient
    except ImportError:
        print("notebooklm-py nao instalado")
        return None
    auth_json = os.getenv('NOTEBOOKLM_AUTH_JSON')
    if auth_json:
        os.environ['NOTEBOOKLM_AUTH_JSON'] = auth_json
    try:
        async with NotebookLMClient.from_storage() as client:
            nb = await client.notebooks.get(notebook_id)
            print("Notebook encontrado:", nb.id)
            artifacts = await client.artifacts.list(notebook_id)
            print("Artifacts encontrados:", len(artifacts))
            drive_service = get_drive_service()
            if not drive_service:
                return None
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            saved_count = 0
            for art in artifacts:
                name = art.get('title') or art.get('id', 'artifact')
                fname = "%s_%s" % (timestamp, name)
                temp_path = "/tmp/" + fname
                try:
                    await client.artifacts.download(notebook_id, art['id'], temp_path)
                    if os.path.exists(temp_path):
                        file_metadata = {'name': fname, 'parents': [drive_folder_id]}
                        from googleapiclient.http import MediaFileUpload
                        media = MediaFileUpload(temp_path, resumable=True)
                        drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                        print("Salvo no Drive:", fname)
                        os.remove(temp_path)
                        saved_count += 1
                except Exception as e:
                    print("Erro ao processar artifact", name, ":", str(e))
            print("Total salvos:", saved_count)
            return True
    except Exception as e:
        print("Erro ao salvar artifacts:", str(e))
        return None

async def generate_audio_overview(notebook_id, instructions=""):
    try:
        from notebooklm import NotebookLMClient
    except ImportError:
        print("notebooklm-py nao instalado")
        return None
    auth_json = os.getenv('NOTEBOOKLM_AUTH_JSON')
    if auth_json:
        os.environ['NOTEBOOKLM_AUTH_JSON'] = auth_json
    try:
        async with NotebookLMClient.from_storage() as client:
            print("Gerando Audio Overview...")
            status = await client.artifacts.generate_audio(notebook_id, instructions=instructions)
            print("Audio Overview iniciado (Task ID:", status.task_id, ")")
            await client.artifacts.wait_for_completion(notebook_id, status.task_id)
            print("Audio Overview gerado com sucesso!")
            return True
    except Exception as e:
        print("Erro ao gerar audio overview:", str(e))
        return None

async def generate_video_overview(notebook_id, instructions=""):
    try:
        from notebooklm import NotebookLMClient
    except ImportError:
        print("notebooklm-py nao instalado")
        return None
    auth_json = os.getenv('NOTEBOOKLM_AUTH_JSON')
    if auth_json:
        os.environ['NOTEBOOKLM_AUTH_JSON'] = auth_json
    try:
        async with NotebookLMClient.from_storage() as client:
            print("Gerando Video Overview...")
            status = await client.artifacts.generate_video(notebook_id, instructions=instructions)
            print("Video Overview iniciado (Task ID:", status.task_id, ")")
            await client.artifacts.wait_for_completion(notebook_id, status.task_id)
            print("Video Overview gerado com sucesso!")
            return True
    except Exception as e:
        print("Erro ao gerar video overview:", str(e))
        return None

if __name__ == "__main__":
    import sys
    notebook_id = os.getenv('NOTEBOOKLM_NOTEBOOK_ID')
    drive_folder_id = os.getenv('NOTEBOOKLM_OUTPUTS_FOLDER_ID')
    print("NotebookLM Video/Audio Overview -> Google Drive")
    print("=" * 50)
    action = sys.argv[1] if len(sys.argv) > 1 else "download"
    instructions = sys.argv[2] if len(sys.argv) > 2 else ""
    if action == "download":
        asyncio.run(save_notebooklm_artifacts_to_drive(notebook_id, drive_folder_id))
    elif action == "generate-audio":
        asyncio.run(generate_audio_overview(notebook_id, instructions))
    elif action == "generate-video":
        asyncio.run(generate_video_overview(notebook_id, instructions))
    elif action == "full":
        print("Pipeline completo: gerar e salvar")
        asyncio.run(generate_audio_overview(notebook_id, instructions))
        asyncio.run(save_notebooklm_artifacts_to_drive(notebook_id, drive_folder_id))
    else:
        print("Uso:")
        print("  python save_notebooklm_video.py download")
        print("  python save_notebooklm_video.py generate-audio")
        print("  python save_notebooklm_video.py generate-video")
        print("  python save_notebooklm_video.py full")

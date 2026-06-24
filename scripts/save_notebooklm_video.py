"""
Script para baixar e salvar vídeos/audio overviews do NotebookLM no Google Drive
"""

import os
import asyncio
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from notebooklm import NotebookLMClient

async def save_notebooklm_artifacts_to_drive(notebook_id, drive_folder_id):
    """
    Baixa vídeos/audio overviews do NotebookLM e salva no Google Drive
    
    Args:
        notebook_id: ID do notebook no NotebookLM
        drive_folder_id: ID da pasta no Google Drive para salvar os arquivos
    """
    # Configurações OAuth para Drive
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        print("❌ Variáveis OAuth não configuradas")
        return None
    
    try:
        # Conecta ao NotebookLM usando notebooklm-py
        async with await NotebookLMClient.from_storage() as client:
            # Obtém o notebook
            notebooks = await client.notebooks.list()
            notebook = None
            for nb in notebooks:
                if nb.id == notebook_id:
                    notebook = nb
                    break
            
            if not notebook:
                print(f"❌ Notebook {notebook_id} não encontrado")
                return None
            
            print(f"✅ Notebook encontrado: {notebook.title}")
            
            # Lista audio overviews existentes
            audio_artifacts = await client.artifacts.list_audio(notebook_id)
            print(f"🎵 Audio Overviews encontrados: {len(audio_artifacts)}")
            
            # Lista video overviews existentes
            video_artifacts = await client.artifacts.list_video(notebook_id)
            print(f"🎬 Video Overviews encontrados: {len(video_artifacts)}")
            
            # Configura credenciais do Drive
            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            creds.refresh(Request())
            
            drive_service = build('drive', 'v3', credentials=creds)
            
            # Baixa e salva audio overviews
            for audio in audio_artifacts:
                filename = f"{notebook.title}_audio_{audio.id}.mp3"
                temp_path = f"/tmp/{filename}"
                
                print(f"📥 Baixando audio: {filename}")
                await client.artifacts.download_audio(notebook_id, temp_path)
                
                # Upload para o Drive
                file_metadata = {
                    'name': filename,
                    'parents': [drive_folder_id]
                }
                
                media = drive_service.media_file_upload(
                    temp_path,
                    mimetype='audio/mpeg',
                    resumable=True
                )
                
                file = drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                
                print(f"✅ Áudio salvo no Drive (ID: {file.get('id')})")
                os.remove(temp_path)
            
            # Baixa e salva video overviews
            for video in video_artifacts:
                filename = f"{notebook.title}_video_{video.id}.mp4"
                temp_path = f"/tmp/{filename}"
                
                print(f"📥 Baixando vídeo: {filename}")
                await client.artifacts.download_video(notebook_id, temp_path)
                
                # Upload para o Drive
                file_metadata = {
                    'name': filename,
                    'parents': [drive_folder_id]
                }
                
                media = drive_service.media_file_upload(
                    temp_path,
                    mimetype='video/mp4',
                    resumable=True
                )
                
                file = drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                
                print(f"✅ Vídeo salvo no Drive (ID: {file.get('id')})")
                os.remove(temp_path)
            
            print(f"\n✅ Todos os artifacts salvos no Drive")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao salvar artifacts: {e}")
        import traceback
        traceback.print_exc()
        return None

async def generate_audio_overview(notebook_id, instructions=""):
    """
    Gera um audio overview para o notebook usando notebooklm-py
    
    Args:
        notebook_id: ID do notebook no NotebookLM
        instructions: Instruções personalizadas para o audio (opcional)
    """
    try:
        async with await NotebookLMClient.from_storage() as client:
            print("🎬 Gerando Audio Overview...")
            
            # Gera o audio overview
            status = await client.artifacts.generate_audio(
                notebook_id,
                instructions=instructions
            )
            
            print(f"✅ Audio Overview iniciado (Task ID: {status.task_id})")
            print("⏳ Aguardando conclusão...")
            
            # Aguarda a conclusão
            await client.artifacts.wait_for_completion(notebook_id, status.task_id)
            
            print("✅ Audio Overview gerado com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao gerar audio overview: {e}")
        import traceback
        traceback.print_exc()
        return None

async def generate_video_overview(notebook_id, instructions=""):
    """
    Gera um video overview para o notebook usando notebooklm-py
    
    Args:
        notebook_id: ID do notebook no NotebookLM
        instructions: Instruções personalizadas para o vídeo (opcional)
    """
    try:
        async with await NotebookLMClient.from_storage() as client:
            print("🎬 Gerando Video Overview...")
            
            # Gera o video overview
            status = await client.artifacts.generate_video(
                notebook_id,
                instructions=instructions
            )
            
            print(f"✅ Video Overview iniciado (Task ID: {status.task_id})")
            print("⏳ Aguardando conclusão...")
            
            # Aguarda a conclusão
            await client.artifacts.wait_for_completion(notebook_id, status.task_id)
            
            print("✅ Video Overview gerado com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao gerar video overview: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    import sys
    
    notebook_id = os.getenv('NOTEBOOKLM_NOTEBOOK_ID', '999a0463-0274-49fe-8fb7-f242338f4a2d')
    drive_folder_id = os.getenv('NOTEBOOKLM_OUTPUTS_FOLDER_ID', '1Eikf5MOwCNopr-FS976lheYlUprvWEx-')
    
    print("🎬 NotebookLM Video/Audio Overview → Google Drive")
    print("=" * 50)
    
    # Verifica argumentos de linha de comando
    action = sys.argv[1] if len(sys.argv) > 1 else "download"
    instructions = sys.argv[2] if len(sys.argv) > 2 else ""
    
    if action == "download":
        # Apenas baixa artifacts existentes
        asyncio.run(save_notebooklm_artifacts_to_drive(notebook_id, drive_folder_id))
    elif action == "generate-audio":
        # Gera audio overview
        asyncio.run(generate_audio_overview(notebook_id, instructions))
    elif action == "generate-video":
        # Gera video overview
        asyncio.run(generate_video_overview(notebook_id, instructions))
    elif action == "full":
        # Gera e baixa
        print("🔄 Pipeline completo: gerar e salvar")
        asyncio.run(generate_audio_overview(notebook_id, instructions))
        asyncio.run(save_notebooklm_artifacts_to_drive(notebook_id, drive_folder_id))
    else:
        print("Uso:")
        print("  python save_notebooklm_video.py download          # Baixa artifacts existentes")
        print("  python save_notebooklm_video.py generate-audio     # Gera audio overview")
        print("  python save_notebooklm_video.py generate-video     # Gera video overview")
        print("  python save_notebooklm_video.py full               # Gera e baixa")
        print("\nVariáveis de ambiente:")
        print("  NOTEBOOKLM_NOTEBOOK_ID")
        print("  NOTEBOOKLM_OUTPUTS_FOLDER_ID")

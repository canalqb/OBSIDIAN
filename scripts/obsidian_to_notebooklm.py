"""
Obsidian to NotebookLM Pipeline - Python Implementation
Lê notas do Obsidian usando Service Account e grava usando OAuth/API
"""

import os
import json
from pathlib import Path
from datetime import datetime
from google.oauth2 import credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

class ObsidianNotebookLMPipeline:
    """Pipeline para integrar Obsidian com NotebookLM"""
    
    def __init__(self, config_path='configuracoes_pipeline.txt'):
        """
        Inicializa pipeline
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.service_account_creds = None
        self.oauth_creds = None
        self._setup_authentication()
    
    def _load_config(self):
        """Carrega configurações do arquivo"""
        config = {}
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse simplificado - na prática usar regex ou parser adequado
        lines = content.split('\n')
        for line in lines:
            if ':' in line and not line.strip().startswith('-') and not line.strip().startswith('='):
                key, value = line.split(':', 1)
                config[key.strip()] = value.strip()
        
        return config
    
    def _setup_authentication(self):
        """Configura autenticação dual (Service Account + OAuth)"""
        # Service Account para leitura
        try:
            self.service_account_creds = service_account.Credentials.from_service_account_file(
                'service_account.json',
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            print("✅ Service Account configurado para leitura")
        except Exception as e:
            print(f"⚠️ Erro ao configurar Service Account: {e}")
        
        # OAuth para gravação
        try:
            if os.path.exists('token.json'):
                self.oauth_creds = credentials.Credentials.from_authorized_user_file(
                    'token.json',
                    scopes=['https://www.googleapis.com/auth/drive']
                )
                print("✅ OAuth configurado para gravação")
        except Exception as e:
            print(f"⚠️ Erro ao configurar OAuth: {e}")
    
    def read_obsidian_notes(self, folder_id=None):
        """
        Lê notas do Obsidian usando Service Account
        
        Args:
            folder_id: ID da pasta no Google Drive
        
        Returns:
            Lista de notas com conteúdo
        """
        if not self.service_account_creds:
            raise Exception("Service Account não configurado")
        
        drive_service = build('drive', 'v3', credentials=self.service_account_creds)
        
        query = ""
        if folder_id:
            query += f"'{folder_id}' in parents"
        query += " and name contains '.md'"
        
        results = drive_service.files().list(
            q=query,
            pageSize=100,
            fields="nextPageToken, files(id, name, size)"
        ).execute()
        
        files = results.get('files', [])
        notes = []
        
        for file in files:
            try:
                content = self._read_file_content(drive_service, file['id'])
                notes.append({
                    'id': file['id'],
                    'name': file['name'],
                    'content': content
                })
                print(f"📖 Lido: {file['name']}")
            except Exception as e:
                print(f"❌ Erro ao ler {file['name']}: {e}")
        
        return notes
    
    def _read_file_content(self, drive_service, file_id):
        """Lê conteúdo de arquivo do Drive"""
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        fh.seek(0)
        return fh.read().decode('utf-8')
    
    def merge_notes_to_txt(self, notes, output_filename='Obsidian_Master.txt'):
        """
        Mescla notas em único arquivo TXT
        
        Args:
            notes: Lista de notas
            output_filename: Nome do arquivo de saída
        
        Returns:
            Conteúdo mesclado
        """
        header = f'EXPORT OBSIDIAN VAULT — {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n\n'
        content = header
        
        for note in notes:
            title = note['name'].replace('.md', '')
            note_content = f'--- NOTA: {title} ---\n{note["content"]}\n\n'
            content += note_content
        
        return content
    
    def write_to_drive(self, content, filename, folder_id=None):
        """
        Grava arquivo no Google Drive usando OAuth/API
        
        Args:
            content: Conteúdo do arquivo
            filename: Nome do arquivo
            folder_id: ID da pasta (opcional)
        """
        if not self.oauth_creds:
            raise Exception("OAuth não configurado")
        
        drive_service = build('drive', 'v3', credentials=self.oauth_creds)
        
        # Verifica se arquivo já existe
        query = f"name='{filename}'"
        if folder_id:
            query += f" and '{folder_id}' in parents"
        
        results = drive_service.files().list(q=query).execute()
        existing_files = results.get('files', [])
        
        file_metadata = {
            'name': filename,
            'mimeType': 'text/plain'
        }
        
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        media = MediaFileUpload(
            f'temp_{filename}',
            mimetype='text/plain',
            resumable=True
        )
        
        # Salva conteúdo temporário
        with open(f'temp_{filename}', 'w', encoding='utf-8') as f:
            f.write(content)
        
        if existing_files:
            # Atualiza arquivo existente
            file_id = existing_files[0]['id']
            file = drive_service.files().update(
                fileId=file_id,
                media_body=media,
                fields={'id'}
            ).execute()
            print(f"✅ Arquivo atualizado: {filename}")
        else:
            # Cria novo arquivo
            file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields={'id'}
            ).execute()
            print(f"✅ Arquivo criado: {filename}")
        
        # Remove arquivo temporário
        os.remove(f'temp_{filename}')
        
        return file
    
    def run_pipeline(self, obsidian_folder_id, output_filename='Obsidian_Master.txt'):
        """
        Executa pipeline completo
        
        Args:
            obsidian_folder_id: ID da pasta do Obsidian no Drive
            output_filename: Nome do arquivo de saída
        """
        print("🚀 Iniciando pipeline Obsidian → NotebookLM")
        print("="*60)
        
        # 1. Lê notas usando Service Account
        print("\n📖 Lendo notas do Obsidian...")
        notes = self.read_obsidian_notes(obsidian_folder_id)
        print(f"✅ {len(notes)} notas lidas")
        
        # 2. Mescla notas
        print("\n🔄 Mesclando notas...")
        merged_content = self.merge_notes_to_txt(notes, output_filename)
        print(f"✅ Conteúdo mesclado ({len(merged_content)} caracteres)")
        
        # 3. Grava no Drive usando OAuth
        print("\n💾 Gravando no Google Drive...")
        self.write_to_drive(merged_content, output_filename)
        print("✅ Arquivo gravado com sucesso")
        
        print("\n" + "="*60)
        print("🎉 Pipeline concluído com sucesso!")
        print("="*60)


def main():
    """Função principal para execução via linha de comando"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Obsidian to NotebookLM Pipeline')
    parser.add_argument('--config', default='configuracoes_pipeline.txt', help='Caminho do arquivo de configuração')
    parser.add_argument('--folder-id', required=True, help='ID da pasta do Obsidian no Google Drive')
    parser.add_argument('--output', default='Obsidian_Master.txt', help='Nome do arquivo de saída')
    
    args = parser.parse_args()
    
    # Executa pipeline
    pipeline = ObsidianNotebookLMPipeline(args.config)
    pipeline.run_pipeline(args.folder_id, args.output)


if __name__ == "__main__":
    main()

"""
Google Service Account Authentication
Para leitura de dados do Google Drive, Blogger, YouTube
"""

import json
import os
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Configurações
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/blogger.readonly',
    'https://www.googleapis.com/auth/youtube.readonly'
]

class GoogleServiceAccountAuth:
    """Autenticação usando Google Service Account"""
    
    def __init__(self, credentials_path=None):
        """
        Inicializa autenticação com Service Account
        
        Args:
            credentials_path: Caminho para o arquivo JSON de credenciais
                            Se None, usa variável de ambiente ou arquivo padrão
        """
        if credentials_path is None:
            credentials_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_CREDENTIALS')
            if credentials_path is None:
                credentials_path = 'service_account.json'
        
        self.credentials_path = credentials_path
        self.credentials = None
        self._authenticate()
    
    def _authenticate(self):
        """Autentica usando o arquivo de credenciais"""
        try:
            self.credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=SCOPES
            )
            print("✅ Autenticação Service Account realizada com sucesso")
        except Exception as e:
            print(f"❌ Erro na autenticação: {e}")
            raise
    
    def get_drive_service(self):
        """Retorna serviço do Google Drive"""
        return build('drive', 'v3', credentials=self.credentials)
    
    def get_blogger_service(self):
        """Retorna serviço do Blogger"""
        return build('blogger', 'v3', credentials=self.credentials)
    
    def get_youtube_service(self):
        """Retorna serviço do YouTube"""
        return build('youtube', 'v3', credentials=self.credentials)
    
    def list_drive_files(self, folder_id=None, file_type=None):
        """
        Lista arquivos do Google Drive
        
        Args:
            folder_id: ID da pasta para listar (opcional)
            file_type: Tipo de arquivo para filtrar (ex: 'md', 'txt')
        
        Returns:
            Lista de arquivos
        """
        drive_service = self.get_drive_service()
        
        query = ""
        if folder_id:
            query += f"'{folder_id}' in parents"
        if file_type:
            if query:
                query += " and "
            query += f"name contains '.{file_type}'"
        
        results = drive_service.files().list(
            q=query,
            pageSize=100,
            fields="nextPageToken, files(id, name, mimeType, size)"
        ).execute()
        
        files = results.get('files', [])
        print(f"📁 Encontrados {len(files)} arquivos")
        return files
    
    def download_file(self, file_id, output_path):
        """
        Baixa arquivo do Google Drive
        
        Args:
            file_id: ID do arquivo
            output_path: Caminho para salvar o arquivo
        """
        drive_service = self.get_drive_service()
        
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.FileIO(output_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"⬇️ Download progresso: {int(status.progress() * 100)}%")
        
        print(f"✅ Arquivo salvo em: {output_path}")
    
    def get_file_content(self, file_id):
        """
        Obtém conteúdo de arquivo de texto do Drive
        
        Args:
            file_id: ID do arquivo
        
        Returns:
            Conteúdo do arquivo como string
        """
        drive_service = self.get_drive_service()
        
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        fh.seek(0)
        content = fh.read().decode('utf-8')
        return content


def create_service_account_json(config_path):
    """
    Cria arquivo JSON de Service Account a partir do arquivo de configuração
    
    Args:
        config_path: Caminho para o arquivo de configuração
    """
    # Lê o arquivo de configuração e extrai informações
    # Use variáveis de ambiente ou arquivo de configuração externo
    project_id = os.getenv('GOOGLE_PROJECT_ID')
    private_key_id = os.getenv('GOOGLE_PRIVATE_KEY_ID')
    private_key = os.getenv('GOOGLE_PRIVATE_KEY')
    client_email = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL')
    
    if not all([project_id, private_key_id, private_key, client_email]):
        print("❌ Variáveis de ambiente não configuradas")
        print("Configure: GOOGLE_PROJECT_ID, GOOGLE_PRIVATE_KEY_ID, GOOGLE_PRIVATE_KEY, GOOGLE_SERVICE_ACCOUNT_EMAIL")
        return
    
    service_account_config = {
        "type": "service_account",
        "project_id": project_id,
        "private_key_id": private_key_id,
        "private_key": private_key,
        "client_email": client_email,
        "client_id": os.getenv('GOOGLE_CLIENT_ID', ''),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email}",
        "universe_domain": "googleapis.com"
    }
    
    # Salva como JSON
    with open('service_account.json', 'w') as f:
        json.dump(service_account_config, f, indent=2)
    
    print("✅ Arquivo service_account.json criado")


if __name__ == "__main__":
    # Exemplo de uso
    print("🔐 Google Service Account Authentication")
    
    # Cria arquivo JSON de credenciais
    create_service_account_json('../configuracoes_pipeline.txt')
    
    # Inicializa autenticação
    auth = GoogleServiceAccountAuth('service_account.json')
    
    # Lista arquivos do Drive
    files = auth.list_drive_files()
    for file in files:
        print(f"  - {file['name']} ({file['id']})")

"""
Script para detectar mudanças no Obsidian_Master.txt
Usa hash do arquivo para detectar alterações
"""

import os
import hashlib
from google.oauth2 import credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import json

def get_file_hash(drive_service, file_id):
    """Calcula hash MD5 do conteúdo do arquivo"""
    try:
        request = drive_service.files().get_media(fileId=file_id)
        content = request.execute()
        
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    except:
        return None

def check_changes(folder_id):
    """
    Verifica se Obsidian_Master.txt teve mudanças
    
    Args:
        folder_id: ID da pasta do Obsidian no Drive
    
    Returns:
        True se houve mudanças, False caso contrário
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
        query = f"name='Obsidian_Master.txt' and '{folder_id}' in parents"
        results = drive_service.files().list(q=query).execute()
        files = results.get('files', [])
        
        if not files:
            print("⚠️ Arquivo Obsidian_Master.txt não encontrado")
            return False
        
        file_id = files[0]['id']
        
        # Calcula hash atual
        current_hash = get_file_hash(drive_service, file_id)
        
        if not current_hash:
            print("❌ Erro ao calcular hash do arquivo")
            return False
        
        # Lê hash anterior (salvo em arquivo local)
        hash_file = '.last_hash.txt'
        last_hash = None
        
        if os.path.exists(hash_file):
            with open(hash_file, 'r') as f:
                last_hash = f.read().strip()
        
        # Compara hashes
        if current_hash != last_hash:
            print(f"✅ Mudanças detectadas no Obsidian_Master.txt")
            print(f"   Hash anterior: {last_hash}")
            print(f"   Hash atual: {current_hash}")
            
            # Salva novo hash
            with open(hash_file, 'w') as f:
                f.write(current_hash)
            
            # Define output para GitHub Actions
            if os.getenv('GITHUB_OUTPUT'):
                with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
                    f.write(f'has_changes=true\n')
                    f.write(f'current_hash={current_hash}\n')
            
            return True
        else:
            print("✅ Nenhuma mudança detectada no Obsidian_Master.txt")
            
            # Define output para GitHub Actions
            if os.getenv('GITHUB_OUTPUT'):
                with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
                    f.write(f'has_changes=false\n')
            
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar mudanças: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Verifica mudanças no Obsidian_Master.txt')
    parser.add_argument('--folder-id', required=True, help='ID da pasta do Obsidian')
    
    args = parser.parse_args()
    
    has_changes = check_changes(args.folder_id)
    
    # Exit code para GitHub Actions
    import sys
    sys.exit(0 if has_changes else 1)

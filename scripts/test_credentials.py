"""
Test Script for Google Credentials
Verifica se as credenciais estão configuradas corretamente
"""

import os
import json
from google.oauth2 import service_account
from google.oauth2 import credentials
from googleapiclient.discovery import build

def test_service_account():
    """Testa autenticação Service Account"""
    print("="*70)
    print("🔐 TESTANDO SERVICE ACCOUNT")
    print("="*70)
    
    # Tenta usar arquivo JSON primeiro (mais confiável)
    if os.path.exists('service_account_test.json'):
        print("📁 Usando arquivo JSON: service_account_test.json")
        try:
            creds = service_account.Credentials.from_service_account_file(
                'service_account_test.json',
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            
            # Testa conexão com Drive API
            drive_service = build('drive', 'v3', credentials=creds)
            about = drive_service.about().get(fields='user').execute()
            
            print(f"\n✅ Service Account autenticado com sucesso (via arquivo JSON)")
            print(f"   Usuário: {about.get('user', {}).get('displayName', 'N/A')}")
            return True
        except Exception as e:
            print(f"\n❌ Erro com arquivo JSON: {e}")
    
    # Fallback para variáveis de ambiente
    print("📋 Tentando via variáveis de ambiente...")
    project_id = os.getenv('GOOGLE_PROJECT_ID')
    private_key_id = os.getenv('GOOGLE_PRIVATE_KEY_ID')
    private_key = os.getenv('GOOGLE_PRIVATE_KEY')
    client_email = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL')
    
    print(f"GOOGLE_PROJECT_ID: {'✅' if project_id else '❌'}")
    print(f"GOOGLE_PRIVATE_KEY_ID: {'✅' if private_key_id else '❌'}")
    print(f"GOOGLE_PRIVATE_KEY: {'✅' if private_key else '❌'}")
    print(f"GOOGLE_SERVICE_ACCOUNT_EMAIL: {'✅' if client_email else '❌'}")
    
    if not all([project_id, private_key_id, private_key, client_email]):
        print("\n❌ Variáveis de ambiente do Service Account não configuradas")
        return False
    
    try:
        # Corrige aspas duplas se presentes (comum em cópias do Google Cloud Console)
        private_key = private_key.replace('""', '"')
        
        # Cria credenciais
        service_account_info = {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": private_key_id,
            "private_key": private_key,
            "client_email": client_email,
            "token_uri": "https://oauth2.googleapis.com/token"
        }
        
        creds = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        
        # Testa conexão com Drive API
        drive_service = build('drive', 'v3', credentials=creds)
        about = drive_service.about().get(fields='user').execute()
        
        print(f"\n✅ Service Account autenticado com sucesso (via variáveis de ambiente)")
        print(f"   Usuário: {about.get('user', {}).get('displayName', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao autenticar Service Account: {e}")
        return False


def test_oauth_credentials():
    """Testa credenciais OAuth"""
    print("\n" + "="*70)
    print("🔐 TESTANDO OAUTH CREDENTIALS")
    print("="*70)
    
    # Verifica variáveis de ambiente
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
    
    print(f"GOOGLE_CLIENT_ID: {'✅' if client_id else '❌'}")
    print(f"GOOGLE_CLIENT_SECRET: {'✅' if client_secret else '❌'}")
    print(f"GOOGLE_REFRESH_TOKEN: {'✅' if refresh_token else '❌'}")
    
    if not all([client_id, client_secret, refresh_token]):
        print("\n❌ Variáveis de ambiente OAuth não configuradas")
        return False
    
    try:
        # Cria credenciais a partir do refresh token
        creds = credentials.Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        # Renova o token
        from google.auth.transport.requests import Request
        creds.refresh(Request())
        
        print(f"\n✅ OAuth autenticado com sucesso")
        print(f"   Access Token gerado: {creds.token[:50]}...")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao autenticar OAuth: {e}")
        return False


def test_blogger_api():
    """Testa API Key do Blogger"""
    print("\n" + "="*70)
    print("🔐 TESTANDO BLOGGER API")
    print("="*70)
    
    api_key = os.getenv('GOOGLE_API_KEY')
    print(f"GOOGLE_API_KEY: {'✅' if api_key else '❌'}")
    
    if not api_key:
        print("\n❌ API Key não configurada")
        return False
    
    try:
        # Testa conexão com Blogger API
        blogger_service = build('blogger', 'v3', developerKey=api_key)
        blogs = blogger_service.blogs().listByUser(userId='self').execute()
        
        print(f"\n✅ Blogger API conectada com sucesso")
        print(f"   Blogs encontrados: {len(blogs.get('items', []))}")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao conectar Blogger API: {e}")
        print("💡 NOTA: Este teste usa API Key que pode não ter permissão para acessar blogs.")
        print("💡 Para editar posts, use OAuth (como em blogger_update.py) que tem permissões completas.")
        return False


def main():
    """Executa todos os testes"""
    print("\n" + "="*70)
    print("🧪 TESTE DE CREDENCIAIS GOOGLE")
    print("="*70)
    print()
    
    results = {
        'Service Account': test_service_account(),
        'OAuth': test_oauth_credentials(),
        'Blogger API': test_blogger_api()
    }
    
    print("\n" + "="*70)
    print("📊 RESUMO DOS TESTES")
    print("="*70)
    for test, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test}: {status}")
    print("="*70)
    
    if all(results.values()):
        print("\n🎉 Todos os testes passaram!")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique as configurações.")


if __name__ == "__main__":
    main()

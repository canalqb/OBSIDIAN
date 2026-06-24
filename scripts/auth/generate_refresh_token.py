"""
Gerador Simplificado de Refresh Token Google OAuth 2.0
Execute este script para obter o refresh token e informar ao usuário
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Configurações OAuth (use variáveis de ambiente ou edite aqui)
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'your_client_id.apps.googleusercontent.com')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', 'your_client_secret')
PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID', 'your_project_id')
REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost')

# Scopes necessários
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/blogger',
    'https://www.googleapis.com/auth/youtube'
]

def generate_refresh_token():
    """Gera refresh token OAuth 2.0"""
    
    print("="*70)
    print("🔐 GERADOR DE REFRESH TOKEN GOOGLE OAUTH 2.0")
    print("="*70)
    print()
    
    # Cria configuração do cliente
    client_config = {
        "installed": {
            "client_id": CLIENT_ID,
            "project_id": PROJECT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": CLIENT_SECRET,
            "redirect_uris": [REDIRECT_URI]
        }
    }
    
    print("📋 Configurações:")
    print(f"   Client ID: {CLIENT_ID}")
    print(f"   Project ID: {PROJECT_ID}")
    print(f"   Redirect URI: {REDIRECT_URI}")
    print()
    
    print("🌐 Abrindo navegador para autenticação...")
    print("   - Faça login na sua conta Google")
    print("   - Autorize o acesso ao Drive, Blogger e YouTube")
    print()
    
    try:
        # Inicia fluxo de autenticação
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        credentials = flow.run_local_server(port=0)
        
        print()
        print("="*70)
        print("✅ AUTENTICAÇÃO REALIZADA COM SUCESSO")
        print("="*70)
        print()
        
        # Extrai informações importantes
        refresh_token = credentials.refresh_token
        access_token = credentials.token
        
        print("🔑 REFRESH TOKEN (COPIE ESTE VALOR):")
        print("-"*70)
        print(refresh_token)
        print("-"*70)
        print()
        
        print("📊 INFORMAÇÕES ADICIONAIS:")
        print(f"   Access Token: {access_token[:50]}...")
        print(f"   Client ID: {credentials.client_id}")
        print(f"   Token URI: {credentials.token_uri}")
        print(f"   Scopes: {', '.join(credentials.scopes)}")
        print()
        
        # Salva em arquivo para backup
        with open('refresh_token.txt', 'w') as f:
            f.write(f"REFRESH_TOKEN: {refresh_token}\n")
            f.write(f"ACCESS_TOKEN: {access_token}\n")
            f.write(f"CLIENT_ID: {credentials.client_id}\n")
            f.write(f"GENERATED_AT: {credentials.expiry if hasattr(credentials, 'expiry') else 'N/A'}\n")
        
        print("💾 Refresh token salvo em: refresh_token.txt")
        print()
        
        print("="*70)
        print("📝 PRÓXIMOS PASSOS:")
        print("="*70)
        print("1. Copie o REFRESH TOKEN acima")
        print("2. Adicione como secret no GitHub: GOOGLE_REFRESH_TOKEN")
        print("3. URL: https://github.com/canalqb/OBSIDIAN/settings/secrets/actions")
        print("4. Nome do secret: GOOGLE_REFRESH_TOKEN")
        print("5. Valor: [cole o refresh token aqui]")
        print("="*70)
        
        return refresh_token
        
    except Exception as e:
        print(f"❌ Erro durante autenticação: {e}")
        return None


if __name__ == "__main__":
    refresh_token = generate_refresh_token()
    
    if refresh_token:
        print()
        print("✅ Processo concluído! Informe o refresh token ao usuário.")
    else:
        print()
        print("❌ Falha ao gerar refresh token. Tente novamente.")

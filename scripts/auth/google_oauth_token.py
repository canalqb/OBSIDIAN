"""
Google OAuth 2.0 Token Generator
Gera refresh token para autenticação OAuth 2.0
"""

import json
import os
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import webbrowser

# Configurações
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/blogger',
    'https://www.googleapis.com/auth/youtube'
]

class GoogleOAuthTokenGenerator:
    """Gerador de tokens OAuth 2.0 do Google"""
    
    def __init__(self, client_config_path=None):
        """
        Inicializa gerador de tokens
        
        Args:
            client_config_path: Caminho para o arquivo de configuração do cliente
                              Se None, usa variável de ambiente ou arquivo padrão
        """
        if client_config_path is None:
            client_config_path = os.getenv('GOOGLE_CLIENT_CONFIG')
            if client_config_path is None:
                client_config_path = 'client_config.json'
        
        self.client_config_path = client_config_path
        self.credentials = None
        self.token_path = 'token.json'
    
    def create_client_config(self, client_id, client_secret, project_id, redirect_uri='http://localhost'):
        """
        Cria arquivo de configuração do cliente OAuth
        
        Args:
            client_id: Client ID do Google Cloud Console
            client_secret: Client Secret do Google Cloud Console
            project_id: ID do projeto
            redirect_uri: URI de redirecionamento
        """
        client_config = {
            "installed": {
                "client_id": client_id,
                "project_id": project_id,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": client_secret,
                "redirect_uris": [redirect_uri]
            }
        }
        
        with open(self.client_config_path, 'w') as f:
            json.dump(client_config, f, indent=2)
        
        print(f"✅ Arquivo {self.client_config_path} criado")
        return client_config
    
    def generate_token(self, force_refresh=False):
        """
        Gera ou renova token OAuth
        
        Args:
            force_refresh: Força renovação do token mesmo se válido
        
        Returns:
            Credenciais OAuth
        """
        # Verifica se já existe token salvo
        if os.path.exists(self.token_path) and not force_refresh:
            self.credentials = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            
            # Verifica se o token está expirado
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                print("🔄 Token expirado, renovando...")
                self.credentials.refresh(Request())
                self._save_token()
                return self.credentials
            elif self.credentials and not self.credentials.expired:
                print("✅ Token válido encontrado")
                return self.credentials
        
        # Inicia fluxo de autenticação
        print("🔐 Iniciando fluxo de autenticação OAuth...")
        flow = InstalledAppFlow.from_client_secrets_file(self.client_config_path, SCOPES)
        
        # Abre navegador para autenticação
        self.credentials = flow.run_local_server(port=0)
        
        # Salva token
        self._save_token()
        
        print("✅ Token gerado com sucesso")
        return self.credentials
    
    def _save_token(self):
        """Salva token em arquivo"""
        with open(self.token_path, 'w') as token:
            token.write(self.credentials.to_json())
        print(f"💾 Token salvo em {self.token_path}")
    
    def get_token_info(self):
        """
        Retorna informações do token atual
        
        Returns:
            Dicionário com informações do token
        """
        if not self.credentials:
            self.generate_token()
        
        token_info = {
            'token': self.credentials.token,
            'refresh_token': self.credentials.refresh_token,
            'token_uri': self.credentials.token_uri,
            'client_id': self.credentials.client_id,
            'client_secret': self.credentials.client_secret,
            'scopes': self.credentials.scopes,
            'expired': self.credentials.expired if hasattr(self.credentials, 'expired') else False
        }
        
        if hasattr(self.credentials, 'expiry'):
            token_info['expiry'] = self.credentials.expiry.isoformat() if self.credentials.expiry else None
        
        return token_info
    
    def print_token_info(self):
        """Imprime informações do token de forma legível"""
        info = self.get_token_info()
        
        print("\n" + "="*60)
        print("📋 INFORMAÇÕES DO TOKEN")
        print("="*60)
        print(f"🔑 Access Token: {info['token'][:50]}...")
        print(f"🔄 Refresh Token: {info['refresh_token'][:50]}...")
        print(f"🆔 Client ID: {info['client_id']}")
        print(f"🌐 Token URI: {info['token_uri']}")
        print(f"📡 Scopes: {', '.join(info['scopes'])}")
        print(f"⏰ Expirado: {'Sim' if info['expired'] else 'Não'}")
        if info.get('expiry'):
            print(f"📅 Expira em: {info['expiry']}")
        print("="*60 + "\n")
    
    def refresh_token(self):
        """Renova o token usando refresh token"""
        if not self.credentials or not self.credentials.refresh_token:
            print("❌ Nenhum refresh token disponível")
            return None
        
        print("🔄 Renovando token...")
        self.credentials.refresh(Request())
        self._save_token()
        print("✅ Token renovado com sucesso")
        return self.credentials


def create_client_config_from_config_file(config_path):
    """
    Cria configuração do cliente a partir do arquivo de configuração do projeto
    
    Args:
        config_path: Caminho para o arquivo de configuração
    """
    # Usa variáveis de ambiente
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    project_id = os.getenv('GOOGLE_PROJECT_ID')
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost')
    
    if not all([client_id, client_secret, project_id]):
        print("❌ Variáveis de ambiente não configuradas")
        print("Configure: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_PROJECT_ID")
        return None
    
    # Cria gerador e configuração
    generator = GoogleOAuthTokenGenerator()
    generator.create_client_config(client_id, client_secret, project_id, redirect_uri)
    
    return generator


if __name__ == "__main__":
    print("🔐 Google OAuth 2.0 Token Generator")
    
    # Cria configuração do cliente
    generator = create_client_config_from_config_file('../configuracoes_pipeline.txt')
    
    # Gera token
    credentials = generator.generate_token()
    
    # Imprime informações
    generator.print_token_info()
    
    print("\n💡 Dica: Salve o refresh token em local seguro para uso futuro")
    print("💡 O refresh token permite renovar o access token sem necessidade de nova autenticação")

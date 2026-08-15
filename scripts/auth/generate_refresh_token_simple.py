"""
Gerador simplificado de Refresh Token Google OAuth 2.0
(versao sem emojis para compatibilidade Windows)
"""

import os
import sys

# Garante UTF-8 no Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your_client_id.apps.googleusercontent.com")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your_client_secret")
PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "your_project_id")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost")

# Escopos necessarios: Drive, Blogger, YOUTUBE
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/blogger",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
]


def generate_refresh_token():
    print("=" * 70)
    print("GERADOR DE REFRESH TOKEN GOOGLE OAUTH 2.0")
    print("=" * 70)
    print()
    print("[INFO] Este script vai abrir o navegador para autenticacao.")
    print("[INFO] Faca login na conta Google VINCULADA ao YouTube certo.")
    print("[INFO] Autorize os escopos: Drive, Blogger, YouTube")
    print()

    client_config = {
        "installed": {
            "client_id": CLIENT_ID,
            "project_id": PROJECT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": CLIENT_SECRET,
            "redirect_uris": [REDIRECT_URI],
        }
    }

    print("Client ID:", CLIENT_ID)
    print("Project ID:", PROJECT_ID)
    print("Redirect URI:", REDIRECT_URI)
    print("Scopes:", ", ".join(SCOPES))
    print()

    try:
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        credentials = flow.run_local_server(port=0)

        print()
        print("=" * 70)
        print("AUTENTICACAO REALIZADA COM SUCESSO")
        print("=" * 70)
        print()

        refresh_token = credentials.refresh_token
        access_token = credentials.token

        print("-" * 70)
        print("REFRESH TOKEN (COPIE ESTE VALOR):")
        print("-" * 70)
        print(refresh_token)
        print("-" * 70)
        print()

        print("Informacoes adicionais:")
        print(f"  Scopes: {', '.join(credentials.scopes)}")
        print()

        # Salva em arquivo
        with open("refresh_token.txt", "w", encoding="utf-8") as f:
            f.write(f"REFRESH_TOKEN: {refresh_token}\n")
            f.write(f"ACCESS_TOKEN: {access_token}\n")
            f.write(f"CLIENT_ID: {credentials.client_id}\n")
            f.write(f"SCOPES: {', '.join(credentials.scopes)}\n")

        print("Refresh token salvo em: refresh_token.txt")
        print()
        print("=" * 70)
        print("PROXIMOS PASSOS:")
        print("=" * 70)
        print("1. Copie o REFRESH TOKEN acima")
        print("2. Adicione como secret no GitHub: GOOGLE_REFRESH_TOKEN")
        print("3. URL: https://github.com/canalqb/OBSIDIAN/settings/secrets/actions")
        print("4. Atualize o arquivo .env com o novo token")
        print("=" * 70)

        return refresh_token

    except Exception as e:
        print(f"Erro durante autenticacao: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    refresh_token = generate_refresh_token()
    if refresh_token:
        print()
        print("Processo concluido com sucesso!")
    else:
        print()
        print("Falha ao gerar refresh token. Tente novamente.")
        sys.exit(1)

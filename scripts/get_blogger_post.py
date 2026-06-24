"""
Script para ler post do Blogger usando OAuth
"""

import os
from google.oauth2 import credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

def get_blogger_post(blog_id, post_id):
    """
    Lê post do Blogger usando OAuth
    
    Args:
        blog_id: ID do blog (5982274115355506187)
        post_id: ID do post (6744117048720374259)
    """
    # Configurações OAuth
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        print("❌ Variáveis OAuth não configuradas")
        return None
    
    try:
        # Cria credenciais
        creds = credentials.Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=['https://www.googleapis.com/auth/blogger']
        )
        
        # Renova token
        creds.refresh(Request())
        
        # Conecta ao Blogger
        blogger_service = build('blogger', 'v3', credentials=creds)
        
        # Lê o post
        post = blogger_service.posts().get(
            blogId=blog_id,
            postId=post_id
        ).execute()
        
        return post
        
    except Exception as e:
        print(f"❌ Erro ao ler post: {e}")
        return None

if __name__ == "__main__":
    blog_id = "5982274115355506187"
    post_id = "6744117048720374259"
    
    post = get_blogger_post(blog_id, post_id)
    
    if post:
        print("✅ Post obtido com sucesso")
        print(f"Título: {post.get('title', 'N/A')}")
        
        # Salva conteúdo completo em arquivo
        with open('blogger_post_content.html', 'w', encoding='utf-8') as f:
            f.write(post.get('content', ''))
        
        print(f"Conteúdo salvo em: blogger_post_content.html")
        print(f"Tamanho: {len(post.get('content', ''))} caracteres")

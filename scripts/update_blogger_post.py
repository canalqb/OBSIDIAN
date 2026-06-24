"""
Script para atualizar post no Blogger usando OAuth
"""

import os
from google.oauth2 import credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

def update_blogger_post(blog_id, post_id, content):
    """
    Atualiza post do Blogger usando OAuth
    
    Args:
        blog_id: ID do blog (5982274115355506187)
        post_id: ID do post (6744117048720374259)
        content: Conteúdo HTML do post
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
        
        # Lê o post atual para obter dados
        post_atual = blogger_service.posts().get(
            blogId=blog_id,
            postId=post_id
        ).execute()
        
        # Atualiza o post
        post_atualizado = blogger_service.posts().update(
            blogId=blog_id,
            postId=post_id,
            body={
                'content': content,
                'title': post_atual.get('title')
            }
        ).execute()
        
        return post_atualizado
        
    except Exception as e:
        print(f"❌ Erro ao atualizar post: {e}")
        return None

if __name__ == "__main__":
    blog_id = "5982274115355506187"
    post_id = "6744117048720374259"
    
    # Lê o conteúdo atualizado
    with open('blogger_post_atualizado.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    post = update_blogger_post(blog_id, post_id, content)
    
    if post:
        print("✅ Post atualizado com sucesso")
        print(f"Título: {post.get('title', 'N/A')}")
        print(f"URL: {post.get('url', 'N/A')}")

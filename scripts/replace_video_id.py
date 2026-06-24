import os
import sys
import re
import json
from blogger_client import BloggerClient
from sheets_client import SheetsClient


PLACEHOLDER_ID = 'DUDla8Bya8M'


def get_blogger_post(blog_id: str, post_id: str) -> dict:
    bc = BloggerClient()
    return bc.get_post(blog_id, post_id)


def replace_video_id_in_content(content: str, new_video_id: str) -> str:
    if PLACEHOLDER_ID not in content:
        print(f"Placeholder {PLACEHOLDER_ID} nao encontrado no conteudo")
        return None
    updated = content.replace(PLACEHOLDER_ID, new_video_id)
    count = content.count(PLACEHOLDER_ID)
    print(f"Substituido {count} ocorrencia(s) de {PLACEHOLDER_ID} -> {new_video_id}")
    return updated


def update_blogger_post(blog_id: str, post_id: str, content: str) -> dict:
    bc = BloggerClient()
    return bc.update_post(blog_id, post_id, content)


def update_sheets(post_url: str, youtube_url: str):
    sheet_id = os.getenv('GOOGLE_SHEET')
    if not sheet_id:
        print("GOOGLE_SHEET nao configurado, pulando")
        return
    sc = SheetsClient()
    sc.update_youtube_link(sheet_id, post_url, youtube_url)


def delete_from_drive(file_id: str):
    try:
        from drive_client import DriveClient
        dc = DriveClient()
        dc.service.files().delete(fileId=file_id).execute()
        print(f"Video deletado do Drive: {file_id}")
    except Exception as e:
        print(f"Erro ao deletar do Drive: {e}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Substituir ID de video placeholder no Blogger')
    parser.add_argument('--blog-id', default=os.getenv('BLOGGER_BLOG_ID', '5982274115355506187'))
    parser.add_argument('--post-id', required=True)
    parser.add_argument('--video-id', required=True, help='Novo ID do YouTube')
    parser.add_argument('--post-url', default='', help='URL do post para atualizar planilha')
    parser.add_argument('--drive-file-id', default='', help='ID do arquivo no Drive para deletar')
    args = parser.parse_args()

    print(f"Lendo post {args.post_id} do Blogger...")
    post = get_blogger_post(args.blog_id, args.post_id)
    content = post.get('content', '')

    print(f"Substituindo {PLACEHOLDER_ID} -> {args.video_id}...")
    new_content = replace_video_id_in_content(content, args.video_id)
    if new_content is None:
        print("Nada a substituir. Verifique se o placeholder esta no post.")
        sys.exit(1)

    print(f"Atualizando post no Blogger...")
    updated = update_blogger_post(args.blog_id, args.post_id, new_content)
    if updated:
        print(f"Post atualizado: {updated.get('url', 'N/A')}")

    youtube_url = f"https://www.youtube.com/watch?v={args.video_id}"

    if args.post_url:
        print(f"Atualizando planilha...")
        update_sheets(args.post_url, youtube_url)

    if args.drive_file_id:
        print(f"Limpando video do Drive...")
        delete_from_drive(args.drive_file_id)

    print(f"\nConcluido! YouTube: {youtube_url}")

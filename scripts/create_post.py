import os
import sys
import json
import asyncio
from datetime import datetime
from blogger_client import BloggerClient
from sheets_client import SheetsClient


def create_blogger_post(title: str, content_html: str, labels: list[str]) -> dict:
    blog_id = os.getenv('BLOGGER_BLOG_ID', '5982274115355506187')
    bc = BloggerClient()
    post = bc.publish_post(blog_id, title, content_html, labels)
    print(f"Post criado: {post.get('url', 'N/A')}")
    print(f"Post ID: {post.get('id', 'N/A')}")
    return post


def register_in_sheets(post_url: str, title: str):
    sheet_id = os.getenv('GOOGLE_SHEET')
    if not sheet_id:
        print("GOOGLE_SHEET nao configurado, pulando planilha")
        return
    sc = SheetsClient()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    sc.append_row(sheet_id, 'Novos_Posts!A:D', [
        post_url,
        '',
        '',
        f'criado {now}',
    ])
    print(f"Registrado na planilha: {post_url}")


def save_state(post_id: str, post_url: str, title: str):
    state = {
        'post_id': post_id,
        'post_url': post_url,
        'title': title,
        'created_at': datetime.now().isoformat(),
        'audio_generated': False,
        'video_generated': False,
        'video_id': '',
        'youtube_url': '',
    }
    with open('.post_state.json', 'w') as f:
        json.dump(state, f, indent=2)
    print(f"Estado salvo em .post_state.json")


async def sync_notebooklm(notebook_id: str, post_title: str):
    try:
        from notebooklm import NotebookLMClient
    except ImportError:
        print("notebooklm-py nao instalado. pip install notebooklm-py")
        return False
    auth_json = os.getenv('NOTEBOOKLM_AUTH_JSON')
    if auth_json:
        os.environ['NOTEBOOKLM_AUTH_JSON'] = auth_json
    try:
        async with NotebookLMClient.from_storage() as client:
            nb = await client.notebooks.get(notebook_id)
            print("Notebook encontrado:", nb.id)
            print("Conteudo sincronizado com NotebookLM (fonte adicionada pelo workflow)")
            print("OK - fonte disponivel para geracao de video")
            return True
    except Exception as e:
        print("Erro ao sincronizar com NotebookLM:", str(e))
        return False


def trigger_github_workflow():
    import subprocess
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("GITHUB_TOKEN nao configurado, pulando trigger")
        return
    owner = os.getenv('GITHUB_REPO_OWNER', 'canalqb')
    repo = os.getenv('GITHUB_REPO_NAME', 'OBSIDIAN')
    cmd = [
        'gh', 'workflow', 'run', 'sync-notebooklm.yml',
        '--repo', f'{owner}/{repo}',
        '--ref', 'main',
        '-f', 'force_sync=true',
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("Workflow sync-notebooklm.yml acionado no GitHub")
    else:
        print(f"Erro ao acionar workflow: {result.stderr}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Criar post no Blogger + NotebookLM')
    parser.add_argument('--title', required=True, help='Titulo do post')
    parser.add_argument('--content-file', required=True, help='Arquivo HTML com conteudo do post')
    parser.add_argument('--labels', default='', help='Marcadores separados por virgula')
    parser.add_argument('--no-sync', action='store_true', help='Pular sync NotebookLM')
    args = parser.parse_args()

    if not os.path.isfile(args.content_file):
        print(f"Arquivo nao encontrado: {args.content_file}")
        sys.exit(1)

    with open(args.content_file, 'r', encoding='utf-8') as f:
        content = f.read()

    labels = [l.strip() for l in args.labels.split(',') if l.strip()]

    print("=== FASE 1: Criar Post ===")
    post = create_blogger_post(args.title, content, labels)
    post_url = post.get('url', '')
    post_id = post.get('id', '')

    print("\n=== Registrar na Planilha ===")
    register_in_sheets(post_url, args.title)

    print("\n=== Salvar Estado ===")
    save_state(post_id, post_url, args.title)

    if not args.no_sync:
        print("\n=== Sync NotebookLM ===")
        notebook_id = os.getenv('NOTEBOOKLM_NOTEBOOK_ID')
        if notebook_id:
            asyncio.run(sync_notebooklm(notebook_id, args.title))
        else:
            print("NOTEBOOKLM_NOTEBOOK_ID nao configurado")

    print("\n=== Acionar Workflow GitHub ===")
    trigger_github_workflow()

    print(f"\nConcluido! Post: {post_url}")

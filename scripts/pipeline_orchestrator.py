"""
pipeline_orchestrator.py
Orquestrador local: publica no Blogger, envia ao GitHub, dispara workflow.
O restante (NotebookLM -> YouTube -> update post) roda no GitHub Actions.
"""

from __future__ import annotations

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

from blogger_client import BloggerClient


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLOGGER_BLOG_ID = os.getenv("BLOGGER_BLOG_ID", "5982274115355506187")
GITHUB_REPO = os.getenv("GITHUB_REPO_NAME", "OBSIDIAN")
GITHUB_OWNER = os.getenv("GITHUB_REPO_OWNER", "canalqb")


def run_pipeline(
    html: str,
    title: str,
    labels: list | None = None,
    source: str = "opencode",
    dry_run: bool = False,
) -> dict:
    """Fluxo local: Blogger -> GitHub.
    O push no Obsidian_Master.txt dispara automaticamente o
    sync-notebooklm.yml no GitHub Actions, que roda:
      NotebookLM -> YouTube -> update post.
    """

    result = {
        "success": False,
        "steps": {},
        "post_id": None,
        "post_url": None,
        "actions_url": None,
    }

    # === Step 1: Publicar no Blogger ===
    print(f"\n{'='*60}")
    print(f"STEP 1/2: Publicando post no Blogger...")
    print(f"{'='*60}")

    if dry_run:
        print(f"[DRY-RUN] Publicaria no Blogger: {title}")
        result["steps"]["blogger"] = "dry_run"
    else:
        try:
            blogger = BloggerClient()
            post = blogger.publish_post(
                blog_id=BLOGGER_BLOG_ID,
                title=title,
                content=html,
                labels=labels or [],
            )
            result["post_id"] = post.get("id")
            result["post_url"] = post.get("url")
            result["steps"]["blogger"] = "published"
            print(f"Post publicado: {post.get('url')}")
        except Exception as e:
            result["steps"]["blogger"] = f"error: {e}"
            print(f"Erro ao publicar no Blogger: {e}")
            return result

    # === Step 2: Enviar para Obsidian_Master.txt (GitHub) ===
    print(f"\n{'='*60}")
    print(f"STEP 2/2: Enviando para Obsidian_Master.txt...")
    print(f"{'='*60}")
    print(f"(O push dispara sync-notebooklm.yml no GitHub Actions)")
    print(f"{'='*60}")

    nlm_content = (
        f"# Post: {title}\n"
        f"Source: {source}\n"
        f"Date: {datetime.now(timezone.utc).isoformat()}\n"
        f"Post ID: {result['post_id']}\n\n"
        f"{html[:50000]}"
    )

    if dry_run:
        print(f"[DRY-RUN] Enviaria para Obsidian_Master.txt")
        result["steps"]["github"] = "dry_run"
    else:
        try:
            from send_to_obsidian import send_to_obsidian as send_fn
            send_result = send_fn(
                content=nlm_content,
                source=source,
                file_path="Obsidian_Master.txt",
            )
            if send_result.get("success"):
                result["steps"]["github"] = "sent"
                print(f"Conteudo enviado ao GitHub. Commit: {send_result.get('commit_sha', 'N/A')}")
            else:
                result["steps"]["github"] = f"error: {send_result.get('message')}"
                print(f"Erro ao enviar: {send_result.get('message')}")
        except Exception as e:
            result["steps"]["github"] = f"error: {e}"
            print(f"Erro ao enviar para GitHub: {e}")

    result["success"] = True

    print(f"\n{'='*60}")
    print(f"ORQUESTRACAO LOCAL COMPLETA!")
    print(f"{'='*60}")
    print(f"  Post:  {result.get('post_url', 'N/A')}")
    print(f"  GitHub: https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}")
    print(f"")
    print(f"O push no Obsidian_Master.txt ja disparou o workflow")
    print(f"sync-notebooklm.yml no GitHub Actions, que vai:")
    print(f"  1. Sincronizar com NotebookLM")
    print(f"  2. Gerar audio/video")
    print(f"  3. Fazer upload para YouTube (privado)")
    print(f"  4. Atualizar o post com embed do video")
    print(f"")
    print(f"Acompanhe em: https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/actions")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Orquestrador local: posta no Blogger e dispara pipeline no GitHub Actions"
    )
    parser.add_argument("--html", help="Caminho do arquivo HTML do post")
    parser.add_argument("--html-content", help="Conteudo HTML direto (string)")
    parser.add_argument("--title", required=True, help="Titulo do post/video")
    parser.add_argument("--labels", default="", help="Labels separadas por virgula")
    parser.add_argument("--source", default="opencode", help="Nome do agente fonte")
    parser.add_argument("--dry-run", action="store_true", help="Simula sem executar acoes reais")

    args = parser.parse_args()

    if args.html:
        with open(args.html, "r", encoding="utf-8") as f:
            html_content = f.read()
    elif args.html_content:
        html_content = args.html_content
    else:
        print("Erro: informe --html ou --html-content")
        sys.exit(1)

    labels_list = [l.strip() for l in args.labels.split(",") if l.strip()]

    result = run_pipeline(
        html=html_content,
        title=args.title,
        labels=labels_list,
        source=args.source,
        dry_run=args.dry_run,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result.get("success"):
        sys.exit(1)

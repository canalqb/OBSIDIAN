"""
pipeline_orchestrator.py
Orquestrador completo: cria post no Blogger, envia ao pipeline NotebookLM,
faz polling do video, publica no YouTube (privado) e atualiza o post.
"""

from __future__ import annotations

import os
import sys
import json
import time
import argparse
import subprocess
import tempfile
from datetime import datetime, timezone
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from blogger_client import BloggerClient
from youtube_uploader import YouTubeUploader
from send_to_obsidian import send_to_obsidian, format_block


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
FOLDER_ID = os.getenv("OBSIDIAN_VAULT_FOLDER_ID", "1Eikf5MOwCNopr-FS976lheYlUprvWEx-")
NOTEBOOKLM_NOTEBOOK_ID = os.getenv("NOTEBOOKLM_NOTEBOOK_ID", "999a0463-0274-49fe-8fb7-f242338f4a2d")
BLOGGER_BLOG_ID = os.getenv("BLOGGER_BLOG_ID", "5982274115355506187")
GITHUB_REPO = os.getenv("GITHUB_REPO_NAME", "OBSIDIAN")
GITHUB_OWNER = os.getenv("GITHUB_REPO_OWNER", "canalqb")

POLL_INTERVAL_SECONDS = 30
MAX_POLL_MINUTES = 45


def trigger_github_workflow(post_id: str, video_title: str) -> dict:
    """Dispara o workflow publish-post.yml via GitHub API."""
    import requests

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return {"success": False, "message": "GITHUB_TOKEN nao configurado"}

    url = (f"https://api.github.com/repos/{GITHUB_OWNER}/"
           f"{GITHUB_REPO}/actions/workflows/publish-post.yml/dispatches")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    payload = {
        "ref": "main",
        "inputs": {
            "post_id": post_id,
            "video_title": video_title,
        },
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code in (204, 200, 201):
        print(f"Workflow publish-post.yml disparado para post_id={post_id}")
        actions_url = (f"https://github.com/{GITHUB_OWNER}/"
                       f"{GITHUB_REPO}/actions")
        return {"success": True, "actions_url": actions_url}
    else:
        return {
            "success": False,
            "message": f"Erro HTTP {resp.status_code}: {resp.text[:200]}",
        }


def wait_for_video_in_drive(
    folder_id: str,
    timeout_minutes: int = MAX_POLL_MINUTES,
    poll_interval: int = POLL_INTERVAL_SECONDS,
) -> Optional[str]:
    """Faz polling no Drive ate detectar novo video do NotebookLM."""
    from drive_client import DriveClient

    drive = DriveClient()
    known_files = set()

    existing = drive.list_files(folder_id)
    for f in existing:
        known_files.add(f["name"])

    timeout_seconds = timeout_minutes * 60
    start = time.time()

    print(f"Aguardando novo video no Drive (timeout: {timeout_minutes}min)...")

    while time.time() - start < timeout_seconds:
        files = drive.list_files(folder_id)
        for f in files:
            if f["name"] not in known_files and f["name"].endswith((".mp4", ".webm", ".mov")):
                print(f"Novo video detectado: {f['name']} (ID: {f['id']})")
                temp_path = os.path.join(tempfile.gettempdir(), f["name"])
                raw = drive.service.files().get_media(fileId=f["id"]).execute()
                with open(temp_path, "wb") as fp:
                    fp.write(raw)
                print(f"Video baixado para: {temp_path}")
                return temp_path
            known_files.add(f["name"])

        remaining = int(timeout_seconds - (time.time() - start))
        print(f"  Aguardando... {remaining}s restantes")
        time.sleep(poll_interval)

    print("Timeout: video nao detectado no Drive dentro do prazo.")
    return None


def run_pipeline(
    html: str,
    title: str,
    labels: Optional[list] = None,
    source: str = "opencode",
    dry_run: bool = False,
) -> dict:
    """Fluxo completo: Blogger -> GitHub -> NotebookLM -> YouTube -> Blogger."""

    result = {
        "success": False,
        "steps": {},
        "post_id": None,
        "post_url": None,
        "video_id": None,
        "video_url": None,
        "actions_url": None,
    }

    # === Step 1: Publicar no Blogger ===
    print(f"\n{'='*60}")
    print(f"STEP 1/6: Publicando post no Blogger...")
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
    print(f"STEP 2/6: Enviando para Obsidian_Master.txt...")
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
            # Usa o send_to_obsidian direto
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

    # === Step 3: Disparar workflow GitHub Actions ===
    print(f"\n{'='*60}")
    print(f"STEP 3/6: Disparando workflow GitHub Actions...")
    print(f"{'='*60}")

    if dry_run:
        print(f"[DRY-RUN] Dispararia workflow com post_id={result['post_id']}")
        result["steps"]["workflow"] = "dry_run"
    else:
        wf_result = trigger_github_workflow(
            post_id=result["post_id"] or "",
            video_title=title,
        )
        result["steps"]["workflow"] = "triggered" if wf_result.get("success") else wf_result.get("message")
        result["actions_url"] = wf_result.get("actions_url")
        if wf_result.get("success"):
            print(f"Workflow disparado!")
            print(f"Acompanhe: {wf_result.get('actions_url')}")
        else:
            print(f"Erro ao disparar workflow: {wf_result.get('message')}")

    # === Step 4: Polling NotebookLM -> Drive (aguardar video) ===
    print(f"\n{'='*60}")
    print(f"STEP 4/6: Aguardando video do NotebookLM no Drive...")
    print(f"{'='*60}")

    notebooklm_outputs_folder = os.getenv(
        "NOTEBOOKLM_OUTPUTS_FOLDER_ID",
        "1Eikf5MOwCNopr-FS976lheYlUprvWEx-",
    )

    if dry_run:
        print(f"[DRY-RUN] Aguardaria video em: {notebooklm_outputs_folder}")
        video_path = None
        result["steps"]["notebooklm"] = "dry_run"
    else:
        video_path = wait_for_video_in_drive(notebooklm_outputs_folder)

        if video_path:
            result["steps"]["notebooklm"] = "video_ready"
            print(f"Video pronto para upload: {video_path}")
        else:
            result["steps"]["notebooklm"] = "timeout"
            print("Video nao detectado dentro do timeout.")
            return result

    # === Step 5: Upload para YouTube (privado) ===
    print(f"\n{'='*60}")
    print(f"STEP 5/6: Enviando video para YouTube (privado)...")
    print(f"{'='*60}")

    if dry_run or not video_path:
        print(f"[DRY-RUN] Enviaria para YouTube: {title}")
        result["steps"]["youtube"] = "dry_run"
    else:
        try:
            yt = YouTubeUploader()
            yt_result = yt.upload_video(
                file_path=video_path,
                title=title,
                description=f"Video gerado pelo NotebookLM para o post: {result.get('post_url', '')}",
                tags=[f"@CanalQb", title[:50]],
                privacy_status="private",
            )
            result["video_id"] = yt_result["video_id"]
            result["video_url"] = yt_result["video_url"]
            result["steps"]["youtube"] = "uploaded"
            print(f"Video no YouTube: {yt_result['video_url']}")

            # Limpa arquivo temporario
            os.remove(video_path)
        except Exception as e:
            result["steps"]["youtube"] = f"error: {e}"
            print(f"Erro ao enviar para YouTube: {e}")
            return result

    # === Step 6: Atualizar post do Blogger com embed do YouTube ===
    print(f"\n{'='*60}")
    print(f"STEP 6/6: Atualizando post do Blogger com embed YouTube...")
    print(f"{'='*60}")

    if dry_run or not result.get("video_id"):
        print(f"[DRY-RUN] Atualizaria post com video_id={result.get('video_id')}")
        result["steps"]["blogger_update"] = "dry_run"
    else:
        try:
            blogger = BloggerClient()
            blogger.add_youtube_embed(
                blog_id=BLOGGER_BLOG_ID,
                post_id=result["post_id"],
                video_id=result["video_id"],
                video_title=title,
            )
            result["steps"]["blogger_update"] = "updated"
            print(f"Post atualizado com embed do YouTube!")
        except Exception as e:
            result["steps"]["blogger_update"] = f"error: {e}"
            print(f"Erro ao atualizar post: {e}")

    result["success"] = True

    print(f"\n{'='*60}")
    print(f"PIPELINE COMPLETO!")
    print(f"{'='*60}")
    print(f"  Post:  {result.get('post_url', 'N/A')}")
    print(f"  Video: {result.get('video_url', 'N/A')}")
    print(f"  Status: {'Sucesso' if result['success'] else 'Falha'}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Orquestrador completo: cria post e publica no ecossistema CanalQb"
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

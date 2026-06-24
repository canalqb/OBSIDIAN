"""
send_to_obsidian.py — Envio de conteúdo para Obsidian_Master.txt via GitHub API
=================================================================================
Esta é a forma RECOMENDADA para agentes externos (Claude.ai, ChatGPT, Manus,
n8n, Make, Zapier) enviarem conteúdo sem precisar de um servidor Flask local.

Como funciona:
  1. O agente chama este script (ou usa a GitHub API diretamente)
  2. O script faz commit no arquivo Obsidian_Master.txt no GitHub
  3. O GitHub Actions detecta o push e dispara o pipeline automaticamente
  4. Chega ao NotebookLM sem depender de servidor local rodando 24/7

Uso:
  python send_to_obsidian.py --content "Texto aqui" --source "Claude"
  python send_to_obsidian.py --file nota.md --source "Manus"
  python send_to_obsidian.py --stdin --source "n8n"  # lê do stdin

Variáveis de ambiente necessárias:
  GITHUB_TOKEN       Personal Access Token com permissão contents:write
  GITHUB_REPO_OWNER  ex: canalqb
  GITHUB_REPO_NAME   ex: OBSIDIAN
  GITHUB_BRANCH      ex: main (padrão)
  GITHUB_FILE_PATH   ex: Obsidian_Master.txt (padrão)
"""

from __future__ import annotations

import os
import sys
import base64
import hashlib
import argparse
import json
from datetime import datetime, timezone
from typing import Optional, Tuple
import requests

# Garante UTF-8 no Windows (emojis nos prints)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


# ── Configurações ──────────────────────────────────────────────────────────

GITHUB_API_BASE = "https://api.github.com"

MAX_CONTENT_CHARS = 100_000   # 100k chars por envio
MAX_FILE_SIZE_MB = 5          # Tamanho máximo do Obsidian_Master.txt


# ── GitHub API Client ──────────────────────────────────────────────────────

class GitHubClient:
    def __init__(self, token: str, owner: str, repo: str, branch: str = "main"):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _url(self, path: str) -> str:
        return f"{GITHUB_API_BASE}/repos/{self.owner}/{self.repo}{path}"

    def get_file(self, file_path: str) -> Optional[dict]:
        """Retorna metadados + conteúdo base64 do arquivo. None se não existir."""
        resp = requests.get(
            self._url(f"/contents/{file_path}"),
            headers=self.headers,
            params={"ref": self.branch},
            timeout=30,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def update_file(self, file_path: str, new_content: str,
                    commit_message: str, sha: str = None) -> dict:
        """
        Cria ou atualiza um arquivo no repositório.
        sha é obrigatório para atualização (retornado por get_file).
        """
        encoded = base64.b64encode(new_content.encode("utf-8")).decode("ascii")
        payload = {
            "message": commit_message,
            "content": encoded,
            "branch": self.branch,
        }
        if sha:
            payload["sha"] = sha

        resp = requests.put(
            self._url(f"/contents/{file_path}"),
            headers=self.headers,
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()


# ── Validação ──────────────────────────────────────────────────────────────

def validate_content(content: str, source: str) -> Tuple[bool, str]:
    """
    Valida o conteúdo antes de enviar.
    Retorna (ok: bool, motivo: str).
    """
    if not content or not content.strip():
        return False, "Conteúdo vazio"

    if len(content) > MAX_CONTENT_CHARS:
        return False, (
            f"Conteúdo muito grande: {len(content):,} chars "
            f"(máximo {MAX_CONTENT_CHARS:,}). "
            "Divida em partes menores."
        )

    if not source or not source.strip():
        return False, "Campo 'source' (nome do agente) é obrigatório"

    if len(source) > 100:
        return False, "Nome do agente muito longo (máximo 100 chars)"

    return True, ""


def content_hash(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:16]


def is_duplicate(existing_content: str, new_content: str, window: int = 3) -> bool:
    """
    Verifica se o conteúdo novo é idêntico a um dos últimos N blocos adicionados.
    Evita que agentes com bug enviem o mesmo conteúdo repetido.
    """
    new_hash = content_hash(new_content)
    # Extrai hashes dos últimos blocos (formato: HASH:xxxx no cabeçalho)
    import re
    found_hashes = re.findall(r'HASH:([a-f0-9]{16})', existing_content)
    recent_hashes = found_hashes[-window:] if found_hashes else []
    return new_hash in recent_hashes


# ── Formatação do bloco ─────────────────────────────────────────────────────

def format_block(content: str, source: str) -> str:
    """Formata o conteúdo como um bloco rastreável."""
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    chash = content_hash(content)
    return (
        f"\n\n{'='*60}\n"
        f"AGENTE: {source} | DATA: {ts} | HASH:{chash}\n"
        f"{'='*60}\n"
        f"{content.strip()}\n"
    )


# ── Função principal ────────────────────────────────────────────────────────

def send_to_obsidian(
    content: str,
    source: str,
    file_path: str = "Obsidian_Master.txt",
    dry_run: bool = False,
) -> dict:
    """
    Envia conteúdo para o Obsidian_Master.txt via GitHub API.

    Retorna dict com:
      success: bool
      message: str
      commit_sha: str (se sucesso)
      chars_added: int
    """
    # 1. Validação
    ok, reason = validate_content(content, source)
    if not ok:
        return {"success": False, "message": f"Validação falhou: {reason}"}

    # 2. Credenciais
    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_REPO_OWNER")
    repo = os.getenv("GITHUB_REPO_NAME")
    branch = os.getenv("GITHUB_BRANCH", "main")

    if not all([token, owner, repo]):
        return {
            "success": False,
            "message": "Variáveis GITHUB_TOKEN, GITHUB_REPO_OWNER e GITHUB_REPO_NAME são obrigatórias.",
        }

    client = GitHubClient(token, owner, repo, branch)

    try:
        # 3. Busca arquivo atual
        existing = client.get_file(file_path)

        if existing:
            current_content = base64.b64decode(existing["content"]).decode("utf-8")
            file_sha = existing["sha"]
        else:
            current_content = f"# Obsidian Master — {owner}/{repo}\nCriado automaticamente.\n"
            file_sha = None

        # 4. Checa tamanho do arquivo
        size_mb = len(current_content.encode("utf-8")) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            return {
                "success": False,
                "message": (
                    f"Obsidian_Master.txt está muito grande ({size_mb:.1f} MB). "
                    "Execute merge_notes.py para consolidar e limpar o arquivo."
                ),
            }

        # 5. Anti-duplicata
        if is_duplicate(current_content, content):
            return {
                "success": False,
                "message": "Conteúdo duplicado detectado. Este bloco já foi enviado recentemente.",
                "status": "duplicate",
            }

        # 6. Formata e anexa
        new_block = format_block(content, source)
        new_content = current_content + new_block

        if dry_run:
            print(f"[DRY-RUN] Bloco que seria adicionado:\n{new_block}")
            return {"success": True, "message": "Dry-run: nenhuma alteração feita", "dry_run": True}

        # 7. Commit
        ts_short = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M')
        commit_msg = f"feat(obsidian): [{source}] adiciona conteúdo {ts_short}"

        result = client.update_file(file_path, new_content, commit_msg, file_sha)
        commit_sha = result.get("commit", {}).get("sha", "")[:8]

        print(f"✅ Conteúdo de [{source}] enviado com sucesso!")
        print(f"   Commit: {commit_sha}")
        print(f"   Arquivo: {owner}/{repo}/{file_path}")
        print(f"   Chars adicionados: {len(new_block):,}")
        print(f"   GitHub Actions irá sincronizar com NotebookLM em até 6h.")

        return {
            "success": True,
            "message": f"Conteúdo adicionado por {source}",
            "commit_sha": commit_sha,
            "chars_added": len(new_block),
            "file": f"{owner}/{repo}/{file_path}",
        }

    except requests.HTTPError as e:
        msg = f"Erro HTTP {e.response.status_code}: {e.response.text[:200]}"
        return {"success": False, "message": msg}
    except Exception as e:
        return {"success": False, "message": str(e)}


# ── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Envia conteúdo para Obsidian_Master.txt via GitHub API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python send_to_obsidian.py --content "Nova pesquisa sobre Bitcoin" --source "Claude"
  python send_to_obsidian.py --file nota.md --source "Manus"
  echo "Conteúdo" | python send_to_obsidian.py --stdin --source "n8n"
  python send_to_obsidian.py --content "teste" --source "Claude" --dry-run

Variáveis de ambiente:
  GITHUB_TOKEN        Personal Access Token (contents:write)
  GITHUB_REPO_OWNER   Dono do repositório (ex: canalqb)
  GITHUB_REPO_NAME    Nome do repositório (ex: OBSIDIAN)
  GITHUB_BRANCH       Branch alvo (padrão: main)
  GITHUB_FILE_PATH    Caminho do arquivo (padrão: Obsidian_Master.txt)
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--content", help="Conteúdo a ser adicionado (string direta)")
    group.add_argument("--file", help="Caminho de arquivo local para enviar")
    group.add_argument("--stdin", action="store_true", help="Lê conteúdo do stdin")

    parser.add_argument("--source", required=True, help="Nome do agente/fonte (ex: Claude, Manus)")
    parser.add_argument("--file-path", default="Obsidian_Master.txt",
                        help="Caminho do arquivo no repositório (padrão: Obsidian_Master.txt)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simula sem fazer commit")
    parser.add_argument("--json", action="store_true",
                        help="Saída em formato JSON")

    args = parser.parse_args()

    # Resolve conteúdo
    if args.content:
        content = args.content
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    else:  # stdin
        content = sys.stdin.read()

    # Sobrescreve file_path via env se definido
    file_path = os.getenv("GITHUB_FILE_PATH", args.file_path)

    result = send_to_obsidian(
        content=content,
        source=args.source,
        file_path=file_path,
        dry_run=args.dry_run,
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif not result["success"]:
        print(f"❌ Erro: {result['message']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

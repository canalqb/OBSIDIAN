"""
add_to_obsidian.py — Adiciona conteúdo ao Obsidian_Master.txt no Google Drive
Versão refatorada: usa DriveClient centralizado, logging estruturado e anti-duplicata.

NOTA: Para agentes EXTERNOS (Claude.ai, ChatGPT, Manus, n8n), prefira usar
      send_to_obsidian.py que opera via GitHub API sem precisar de servidor local.
      Este script é útil para agentes rodando na mesma máquina.
"""

import os
import sys
import hashlib
import re
from datetime import datetime, timezone
from drive_client import DriveClient
from logger import log_agent_action


# ── Configurações ──────────────────────────────────────────────────────────

MAX_CONTENT_CHARS = 100_000
MAX_FILE_SIZE_MB = 5


# ── Helpers ────────────────────────────────────────────────────────────────

def content_hash(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:16]


def is_duplicate(existing_content: str, new_content: str, window: int = 3) -> bool:
    """Verifica se o bloco foi enviado recentemente (anti-spam)."""
    new_hash = content_hash(new_content)
    found_hashes = re.findall(r'HASH:([a-f0-9]{16})', existing_content)
    recent = found_hashes[-window:] if found_hashes else []
    return new_hash in recent


def format_block(content: str, source: str) -> str:
    """Formata o conteúdo como bloco rastreável com hash."""
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    chash = content_hash(content)
    return (
        f"\n\n{'='*60}\n"
        f"AGENTE: {source} | DATA: {ts} | HASH:{chash}\n"
        f"{'='*60}\n"
        f"{content.strip()}\n"
    )


# ── Função principal ────────────────────────────────────────────────────────

def add_content_to_obsidian(
    content: str,
    source: str = "Unknown Agent",
    folder_id: str = None,
) -> bool:
    """
    Adiciona conteúdo ao Obsidian_Master.txt no Google Drive.

    Args:
        content:   Texto a ser adicionado.
        source:    Nome do agente/fonte.
        folder_id: ID da pasta do Drive. Usa env OBSIDIAN_VAULT_FOLDER_ID se None.

    Returns:
        True em caso de sucesso, False em caso de erro.
    """
    folder_id = folder_id or os.getenv('OBSIDIAN_VAULT_FOLDER_ID')

    # 1. Validação básica
    if not content or not content.strip():
        log_agent_action(source, content, "rejected", error="Conteúdo vazio")
        return False

    if len(content) > MAX_CONTENT_CHARS:
        msg = f"Conteúdo muito grande: {len(content):,} chars (máximo {MAX_CONTENT_CHARS:,})"
        log_agent_action(source, content, "rejected", error=msg)
        print(f"❌ {msg}")
        return False

    if not folder_id:
        msg = "OBSIDIAN_VAULT_FOLDER_ID não definido"
        log_agent_action(source, content, "error", error=msg)
        print(f"❌ {msg}")
        return False

    try:
        drive = DriveClient()

        # 2. Busca o arquivo
        file_meta = drive.find_file("Obsidian_Master.txt", folder_id)

        if not file_meta:
            print("⚠️ Obsidian_Master.txt não encontrado. Criando...")
            current_content = "# Obsidian Master\nCriado automaticamente.\n"
        else:
            # 3. Verifica tamanho
            size_mb = int(file_meta.get('size', 0)) / (1024 * 1024)
            if size_mb > MAX_FILE_SIZE_MB:
                msg = f"Arquivo muito grande ({size_mb:.1f} MB). Execute merge_notes.py para limpar."
                log_agent_action(source, content, "rejected", error=msg)
                print(f"❌ {msg}")
                return False

            current_content = drive.read_file(file_meta['id'])

        # 4. Anti-duplicata
        if is_duplicate(current_content, content):
            msg = "Conteúdo duplicado detectado — este bloco já foi enviado recentemente."
            log_agent_action(source, content, "duplicate", error=msg)
            print(f"⚠️ {msg}")
            return False

        # 5. Formata e anexa
        new_block = format_block(content, source)
        updated_content = current_content + new_block

        # 6. Salva no Drive
        if file_meta:
            drive.write_file(file_meta['id'], updated_content)
        else:
            drive.create_file("Obsidian_Master.txt", updated_content, folder_id)

        chars_added = len(new_block)
        log_agent_action(source, content, "success", chars_added=chars_added,
                         content_hash=content_hash(content))
        print(f"✅ Conteúdo de [{source}] adicionado com sucesso ({chars_added:,} chars)")
        return True

    except EnvironmentError as e:
        log_agent_action(source, content, "error", error=str(e))
        print(f"❌ Configuração: {e}")
        return False
    except Exception as e:
        log_agent_action(source, content, "error", error=str(e))
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False


# ── CLI ─────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Adiciona conteúdo ao Obsidian_Master.txt no Google Drive'
    )
    parser.add_argument('--content', required=True, help='Conteúdo a ser adicionado')
    parser.add_argument('--source', default='CLI', help='Nome do agente/fonte')
    parser.add_argument('--folder-id', help='ID da pasta no Drive (opcional, usa env se omitido)')

    args = parser.parse_args()

    success = add_content_to_obsidian(args.content, args.source, args.folder_id)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

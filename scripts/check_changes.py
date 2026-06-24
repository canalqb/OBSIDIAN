"""
check_changes.py — Detecção de mudanças no Obsidian_Master.txt
Versão refatorada: usa modifiedTime do Drive (mais robusto que MD5 local)
e persiste o estado no próprio repositório via arquivo .last_sync.json.

Estratégia dual:
  1. Primary:  compara modifiedTime ISO 8601 do Drive (sem precisar baixar o arquivo)
  2. Fallback: se modifiedTime não disponível, usa SHA256 do conteúdo

Saídas para GitHub Actions:
  has_changes=true|false
  last_modified=<ISO timestamp>
  file_id=<drive file id>
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from drive_client import DriveClient
from logger import log_pipeline_run


STATE_FILE = Path(__file__).parent.parent / ".last_sync.json"


# ── Persistência de estado ─────────────────────────────────────────────────

def load_state() -> dict:
    """Carrega o estado da última sincronização."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_state(state: dict):
    """Persiste o estado da sincronização."""
    STATE_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


# ── Detecção de mudanças ───────────────────────────────────────────────────

def check_changes(folder_id: str) -> bool:
    """
    Verifica se Obsidian_Master.txt foi modificado desde a última sincronização.

    Retorna True se houve mudanças, False caso contrário.
    Escreve outputs para GitHub Actions se GITHUB_OUTPUT estiver definido.
    """
    log_pipeline_run("check_changes", "started", {"folder_id": folder_id})

    try:
        drive = DriveClient()

        # 1. Busca metadados do arquivo (sem baixar o conteúdo)
        file_meta = drive.find_file("Obsidian_Master.txt", folder_id)

        if not file_meta:
            print("⚠️ Obsidian_Master.txt não encontrado no Drive.")
            log_pipeline_run("check_changes", "error", error="Arquivo não encontrado")
            _set_github_output("has_changes", "false")
            return False

        file_id = file_meta['id']
        modified_time = file_meta.get('modifiedTime', '')
        file_size = file_meta.get('size', '0')

        print(f"📄 Arquivo encontrado: {file_id}")
        print(f"   Modificado em: {modified_time}")
        print(f"   Tamanho: {int(file_size):,} bytes")

        # 2. Carrega estado anterior
        state = load_state()
        last_modified = state.get("last_modified", "")
        last_file_id = state.get("file_id", "")

        # 3. Comparação primária: modifiedTime
        has_changes = (modified_time != last_modified) or (file_id != last_file_id)

        if has_changes:
            print(f"✅ Mudanças detectadas no Obsidian_Master.txt")
            print(f"   Anterior: {last_modified or 'nunca sincronizado'}")
            print(f"   Atual:    {modified_time}")

            # 4. Fallback: confirma com SHA256 do conteúdo (evita falso positivo por metadata)
            content = drive.read_file(file_id)
            current_sha = hashlib.sha256(content.encode("utf-8")).hexdigest()[:32]
            last_sha = state.get("content_sha", "")

            if current_sha == last_sha:
                print("ℹ️ modifiedTime diferente mas conteúdo idêntico — sem mudanças reais.")
                has_changes = False
            else:
                print(f"   SHA256: {last_sha or 'N/A'} → {current_sha}")
                # Salva novo estado
                save_state({
                    "last_modified": modified_time,
                    "file_id": file_id,
                    "content_sha": current_sha,
                    "synced_at": datetime.now(timezone.utc).isoformat(),
                    "file_size_bytes": int(file_size),
                })
        else:
            print("✅ Nenhuma mudança detectada.")

        # 5. Outputs para GitHub Actions
        _set_github_output("has_changes", "true" if has_changes else "false")
        _set_github_output("last_modified", modified_time)
        _set_github_output("file_id", file_id)

        log_pipeline_run(
            "check_changes",
            "success",
            {"has_changes": has_changes, "modified_time": modified_time},
        )

        return has_changes

    except EnvironmentError as e:
        print(f"❌ Configuração: {e}")
        log_pipeline_run("check_changes", "error", error=str(e))
        _set_github_output("has_changes", "false")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar mudanças: {e}")
        import traceback
        traceback.print_exc()
        log_pipeline_run("check_changes", "error", error=str(e))
        # Em caso de erro, considera que houve mudanças para não bloquear o pipeline
        _set_github_output("has_changes", "true")
        return True


def _set_github_output(key: str, value: str):
    """Escreve output para GitHub Actions."""
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"{key}={value}\n")


# ── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Verifica mudanças no Obsidian_Master.txt')
    parser.add_argument('--folder-id', help='ID da pasta do Obsidian (opcional, usa env)')

    args = parser.parse_args()

    folder_id = args.folder_id or os.getenv('OBSIDIAN_VAULT_FOLDER_ID')

    if not folder_id:
        print("❌ folder-id obrigatório via --folder-id ou OBSIDIAN_VAULT_FOLDER_ID")
        sys.exit(1)

    has_changes = check_changes(folder_id)
    sys.exit(0 if has_changes else 1)

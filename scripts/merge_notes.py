"""
merge_notes.py — Mescla todas as notas .md do Obsidian em Obsidian_Master.txt
Versão refatorada: usa DriveClient centralizado, paginação completa e logging.

Este script substitui o Google Apps Script (Code.js).
Execute via GitHub Actions ou localmente.
"""

import os
import sys
from datetime import datetime, timezone
from drive_client import DriveClient
from logger import log_pipeline_run


def merge_obsidian_notes(
    folder_id: str,
    output_filename: str = 'Obsidian_Master.txt',
) -> bool:
    """
    Mescla todas as notas .md do Obsidian em um único arquivo TXT no Drive.

    Args:
        folder_id:       ID da pasta raiz do Obsidian no Drive.
        output_filename: Nome do arquivo de saída.

    Returns:
        True em caso de sucesso, False em caso de erro.
    """
    log_pipeline_run("merge_notes", "started", {"folder_id": folder_id})

    try:
        drive = DriveClient()
        all_notes = []

        def collect_notes(fid: str, path: str = ""):
            """Coleta notas .md recursivamente."""
            # Arquivos .md na pasta atual
            files = drive.list_files(fid, extension=".md")
            for f in files:
                try:
                    content = drive.read_file(f['id'])
                    all_notes.append({
                        'name': f['name'],
                        'path': path,
                        'modified': f.get('modifiedTime', ''),
                        'content': content,
                    })
                    print(f"   ✅ {path}{f['name']}")
                except Exception as e:
                    print(f"   ⚠️ Falha ao ler {f['name']}: {e}")

            # Subpastas
            folders = drive.list_folders(fid)
            for folder in folders:
                collect_notes(folder['id'], f"{path}{folder['name']}/")

        print(f"📖 Coletando notas da pasta: {folder_id}")
        collect_notes(folder_id)

        if not all_notes:
            print("⚠️ Nenhuma nota .md encontrada.")
            log_pipeline_run("merge_notes", "skipped", {"reason": "Nenhuma nota encontrada"})
            return False

        print(f"\n🔄 Mesclando {len(all_notes)} notas...")

        # Ordena por pasta/nome para saída determinística
        all_notes.sort(key=lambda n: (n['path'], n['name']))

        ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        lines = [
            f"# OBSIDIAN VAULT EXPORT",
            f"# Gerado em: {ts}",
            f"# Total de notas: {len(all_notes)}",
            f"# Pasta Drive: {folder_id}",
            "",
        ]

        for note in all_notes:
            title = note['name'].replace('.md', '')
            path = note['path'] or '/'
            modified = note['modified'][:10] if note['modified'] else 'N/A'

            lines.append(f"\n{'─'*60}")
            lines.append(f"NOTA: {title}")
            lines.append(f"PATH: {path} | MODIFICADO: {modified}")
            lines.append(f"{'─'*60}")
            lines.append(note['content'].strip())
            lines.append("")

        merged_content = "\n".join(lines)
        total_chars = len(merged_content)
        print(f"✅ Conteúdo mesclado: {total_chars:,} chars ({total_chars/1024:.1f} KB)")

        # Cria ou atualiza o arquivo de saída
        file_id = drive.upsert_file(output_filename, merged_content, folder_id)

        print(f"✅ {output_filename} salvo no Drive (ID: {file_id})")
        log_pipeline_run("merge_notes", "success", {
            "notes_count": len(all_notes),
            "total_chars": total_chars,
            "file_id": file_id,
        })
        return True

    except EnvironmentError as e:
        print(f"❌ Configuração: {e}")
        log_pipeline_run("merge_notes", "error", error=str(e))
        return False
    except Exception as e:
        print(f"❌ Erro ao mesclar notas: {e}")
        import traceback
        traceback.print_exc()
        log_pipeline_run("merge_notes", "error", error=str(e))
        return False


# ── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Mescla notas do Obsidian em um arquivo TXT')
    parser.add_argument('--folder-id', help='ID da pasta do Obsidian (opcional, usa env)')
    parser.add_argument('--output', default='Obsidian_Master.txt', help='Nome do arquivo de saída')

    args = parser.parse_args()

    folder_id = args.folder_id or os.getenv('OBSIDIAN_VAULT_FOLDER_ID')

    if not folder_id:
        print("❌ folder-id obrigatório via --folder-id ou OBSIDIAN_VAULT_FOLDER_ID")
        sys.exit(1)

    success = merge_obsidian_notes(folder_id, args.output)

    if success:
        print("\n🎉 Processo concluído com sucesso!")
    else:
        print("\n❌ Processo falhou")
        sys.exit(1)

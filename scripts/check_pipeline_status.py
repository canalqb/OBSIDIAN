"""
check_pipeline_status.py — Verifica status do pipeline e
lista os ultimos videos gerados pelo NotebookLM salvos no Drive.
"""

from __future__ import annotations

import os
import json
import sys
from datetime import datetime, timezone
from drive_client import DriveClient


def get_pipeline_status(
    drive_folder_id: str = None,
    max_files: int = 10,
) -> dict:
    drive = DriveClient()
    folder_id = drive_folder_id or os.getenv("NOTEBOOKLM_OUTPUTS_FOLDER_ID")

    if not folder_id:
        return {"error": "NOTEBOOKLM_OUTPUTS_FOLDER_ID nao configurado"}

    files = drive.list_files(folder_id)

    videos = [f for f in files if f["name"].endswith((".mp4", ".webm", ".mov"))]
    audios = [f for f in files if f["name"].endswith((".mp3", ".wav", ".ogg"))]
    outros = [f for f in files if f not in videos and f not in audios]

    videos.sort(key=lambda x: x.get("modifiedTime", ""), reverse=True)
    audios.sort(key=lambda x: x.get("modifiedTime", ""), reverse=True)

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_files": len(files),
        "videos": videos[:max_files],
        "audios": audios[:max_files],
        "outros": len(outros),
        "folder_id": folder_id,
    }


if __name__ == "__main__":
    folder_id = sys.argv[1] if len(sys.argv) > 1 else None
    status = get_pipeline_status(folder_id)
    print(json.dumps(status, ensure_ascii=False, indent=2, default=str))

    if status.get("videos"):
        print(f"\nUltimos videos gerados:")
        for v in status["videos"]:
            print(f"  - {v['name']} ({v.get('modifiedTime', '')[:19]})")
    else:
        print("\nNenhum video encontrado na pasta.")

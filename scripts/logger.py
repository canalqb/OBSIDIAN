"""
logger.py — Módulo centralizado de logging estruturado
Registra todas as ações dos agentes com timestamp, fonte e status.
"""

from __future__ import annotations

import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List


# Pasta padrão para logs (dentro do repo, ignorada pelo git via *.log)
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

AGENT_LOG_FILE = LOG_DIR / "agent_activity.jsonl"   # 1 JSON por linha
PIPELINE_LOG_FILE = LOG_DIR / "pipeline_runs.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_agent_action(
    source: str,
    content: str,
    status: str,       # "success" | "error" | "duplicate" | "rejected"
    error: str = None,
    chars_added: int = 0,
    content_hash: str = None,
):
    """
    Registra uma ação de agente no log JSONL.
    Cada linha é um JSON independente para facilitar análise.
    """
    entry = {
        "ts": _now_iso(),
        "source": source,
        "status": status,
        "chars_added": chars_added,
        "content_preview": content[:120].replace("\n", " ") if content else "",
        "content_hash": content_hash or _hash(content),
        "error": error,
    }

    try:
        with AGENT_LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[LOGGER] Falha ao escrever log: {e}")

    # Print formatado no terminal
    icon = {"success": "✅", "error": "❌", "duplicate": "⚠️", "rejected": "🚫"}.get(status, "ℹ️")
    print(f"{icon} [{source}] {status.upper()} — {entry['content_preview'][:80]}...")
    if error:
        print(f"   Erro: {error}")


def log_pipeline_run(
    step: str,
    status: str,       # "started" | "success" | "error" | "skipped"
    details: dict = None,
    error: str = None,
):
    """
    Registra uma execução do pipeline no log JSONL.
    """
    entry = {
        "ts": _now_iso(),
        "step": step,
        "status": status,
        "details": details or {},
        "error": error,
    }

    try:
        with PIPELINE_LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[LOGGER] Falha ao escrever log de pipeline: {e}")

    icon = {"started": "🚀", "success": "✅", "error": "❌", "skipped": "⏭️"}.get(status, "ℹ️")
    print(f"{icon} [PIPELINE:{step}] {status.upper()}")
    if error:
        print(f"   Erro: {error}")


def get_recent_agent_logs(limit: int = 50) -> List[dict]:
    """Retorna os últimos N registros de atividade dos agentes."""
    if not AGENT_LOG_FILE.exists():
        return []
    lines = AGENT_LOG_FILE.read_text(encoding="utf-8").strip().splitlines()
    return [json.loads(l) for l in lines[-limit:]]


def get_agent_stats() -> dict:
    """Retorna estatísticas agregadas dos agentes."""
    logs = get_recent_agent_logs(limit=10000)
    if not logs:
        return {}

    stats = {}
    for entry in logs:
        src = entry.get("source", "unknown")
        if src not in stats:
            stats[src] = {"success": 0, "error": 0, "duplicate": 0, "rejected": 0, "total_chars": 0}
        stats[src][entry.get("status", "error")] = stats[src].get(entry.get("status", "error"), 0) + 1
        stats[src]["total_chars"] += entry.get("chars_added", 0)

    return stats


def _hash(text: str) -> str:
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

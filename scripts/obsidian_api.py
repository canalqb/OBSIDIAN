"""
obsidian_api.py — API REST para alimentar Obsidian_Master.txt
Versão refatorada: autenticação por API key, validação, logging e anti-duplicata.

Endpoints:
  GET  /health          — Status da API + estatísticas dos agentes
  GET  /stats           — Estatísticas detalhadas de atividade
  POST /add             — Adiciona conteúdo (JSON)
  POST /add/text        — Adiciona conteúdo (texto puro)
  GET  /logs            — Últimas N ações dos agentes

Autenticação:
  Todos os endpoints POST exigem o header:
    X-API-Key: <valor de API_SECRET_KEY no .env>

  Para uso local sem autenticação (desenvolvimento), defina:
    API_AUTH_ENABLED=false

Uso:
  python obsidian_api.py
  PORT=8080 python obsidian_api.py

Variáveis de ambiente:
  OBSIDIAN_VAULT_FOLDER_ID  ID da pasta do Drive
  API_SECRET_KEY            Chave para autenticar agentes externos
  API_AUTH_ENABLED          true (padrão) | false (desativa auth para dev local)
  PORT                      Porta do servidor (padrão: 5000)
"""

import os
import sys
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from add_to_obsidian import add_content_to_obsidian
from logger import log_agent_action, get_recent_agent_logs, get_agent_stats


app = Flask(__name__)

# ── Configurações ──────────────────────────────────────────────────────────

FOLDER_ID = os.getenv('OBSIDIAN_VAULT_FOLDER_ID')
API_SECRET_KEY = os.getenv('API_SECRET_KEY', '')
AUTH_ENABLED = os.getenv('API_AUTH_ENABLED', 'true').lower() != 'false'

_start_time = datetime.now(timezone.utc)


# ── Middleware de autenticação ──────────────────────────────────────────────

def require_api_key():
    """
    Verifica o header X-API-Key.
    Retorna None se OK, ou uma resposta de erro se falhar.
    """
    if not AUTH_ENABLED:
        return None

    if not API_SECRET_KEY:
        return jsonify({
            "error": "API_SECRET_KEY não configurada no servidor. "
                     "Defina no .env ou desative auth com API_AUTH_ENABLED=false."
        }), 500

    key = request.headers.get("X-API-Key", "")
    if not key or key != API_SECRET_KEY:
        return jsonify({"error": "Unauthorized: X-API-Key inválida ou ausente"}), 401

    return None


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health():
    """Health check com status do sistema."""
    uptime = (datetime.now(timezone.utc) - _start_time).total_seconds()
    stats = get_agent_stats()
    return jsonify({
        "status": "healthy",
        "service": "Obsidian API",
        "version": "2.0",
        "uptime_seconds": round(uptime),
        "auth_enabled": AUTH_ENABLED,
        "folder_id": FOLDER_ID or "não configurado",
        "agent_stats": stats,
    })


@app.route('/stats', methods=['GET'])
def stats():
    """Estatísticas detalhadas de atividade dos agentes."""
    limit = request.args.get('limit', 50, type=int)
    logs = get_recent_agent_logs(limit=min(limit, 500))
    agent_stats = get_agent_stats()
    return jsonify({
        "agent_stats": agent_stats,
        "recent_logs": logs,
        "total_shown": len(logs),
    })


@app.route('/logs', methods=['GET'])
def logs():
    """Retorna as últimas N ações dos agentes."""
    limit = request.args.get('limit', 20, type=int)
    source_filter = request.args.get('source')
    all_logs = get_recent_agent_logs(limit=min(limit, 200))

    if source_filter:
        all_logs = [l for l in all_logs if l.get('source') == source_filter]

    return jsonify({"logs": all_logs, "count": len(all_logs)})


@app.route('/add', methods=['POST'])
def add_content():
    """
    Adiciona conteúdo via JSON.

    Body:
      {
        "content": "Texto a adicionar",
        "source": "NomeDoAgente"   (opcional, padrão: API)
      }

    Headers:
      X-API-Key: <API_SECRET_KEY>
    """
    auth_error = require_api_key()
    if auth_error:
        return auth_error

    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Body JSON inválido ou vazio"}), 400

        content = data.get('content', '').strip()
        source = data.get('source', 'API').strip() or 'API'

        if not content:
            return jsonify({"error": "Campo 'content' é obrigatório e não pode ser vazio"}), 400

        success = add_content_to_obsidian(content, source, FOLDER_ID)

        if success:
            return jsonify({
                "status": "success",
                "message": f"Conteúdo adicionado por {source}",
                "source": source,
                "chars": len(content),
                "ts": datetime.now(timezone.utc).isoformat(),
            }), 200
        else:
            return jsonify({
                "error": "Falha ao adicionar conteúdo. Verifique os logs do servidor."
            }), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/add/text', methods=['POST'])
def add_text_plain():
    """
    Adiciona conteúdo como texto puro (plain text).

    Headers:
      X-Source:  Nome do agente (opcional)
      X-API-Key: <API_SECRET_KEY>

    Body: texto puro
    """
    auth_error = require_api_key()
    if auth_error:
        return auth_error

    try:
        content = request.get_data(as_text=True).strip()
        source = request.headers.get('X-Source', 'API').strip() or 'API'

        if not content:
            return jsonify({"error": "Conteúdo vazio"}), 400

        success = add_content_to_obsidian(content, source, FOLDER_ID)

        if success:
            return jsonify({
                "status": "success",
                "message": f"Conteúdo adicionado por {source}",
                "source": source,
                "chars": len(content),
                "ts": datetime.now(timezone.utc).isoformat(),
            }), 200
        else:
            return jsonify({
                "error": "Falha ao adicionar conteúdo. Verifique os logs do servidor."
            }), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Tratamento de erros globais ─────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint não encontrado", "endpoints": [
        "GET /health", "GET /stats", "GET /logs",
        "POST /add (JSON)", "POST /add/text (plain)"
    ]}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Método HTTP não permitido neste endpoint"}), 405


# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("=" * 55)
    print("  Obsidian API v2.0")
    print("=" * 55)
    print(f"  Porta:        {port}")
    print(f"  Pasta Drive:  {FOLDER_ID or 'NAO CONFIGURADA'}")
    print(f"  Auth:         {'ATIVA' if AUTH_ENABLED else 'DESATIVADA (dev)'}")
    print(f"  API Key:      {'configurada' if API_SECRET_KEY else 'NAO CONFIGURADA'}")
    print("=" * 55)
    print()

    if not FOLDER_ID:
        print("AVISO: OBSIDIAN_VAULT_FOLDER_ID nao definida — endpoints /add vao falhar.")

    if AUTH_ENABLED and not API_SECRET_KEY:
        print("AVISO: API_SECRET_KEY nao definida — todos os POSTs vao retornar erro 500.")

    # Em produção, use gunicorn em vez de app.run()
    # gunicorn -w 2 -b 0.0.0.0:5000 obsidian_api:app
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true')

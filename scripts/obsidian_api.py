"""
API REST para alimentar Obsidian_Master.txt
Permite que agentes (Claude, Ollama, ChatGPT, Manus) enviem conteúdo via HTTP
"""

from flask import Flask, request, jsonify
from add_to_obsidian import add_content_to_obsidian
import os

app = Flask(__name__)

# Configurações
FOLDER_ID = os.getenv('OBSIDIAN_VAULT_FOLDER_ID', '1Eikf5MOwCNopr-FS976lheYlUprvWEx-')

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de health check"""
    return jsonify({"status": "healthy", "service": "Obsidian API"})

@app.route('/add', methods=['POST'])
def add_content():
    """
    Endpoint para adicionar conteúdo ao Obsidian_Master.txt
    
    Body JSON:
    {
        "content": "Conteúdo a ser adicionado",
        "source": "Nome do agente (opcional, padrão: API)"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({"error": "Campo 'content' é obrigatório"}), 400
        
        content = data['content']
        source = data.get('source', 'API')
        
        success = add_content_to_obsidian(content, source, FOLDER_ID)
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Conteúdo adicionado por {source}",
                "source": source
            }), 200
        else:
            return jsonify({"error": "Falha ao adicionar conteúdo"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add/text', methods=['POST'])
def add_text_plain():
    """
    Endpoint para adicionar conteúdo como texto plain
    Útil para agentes que enviam texto diretamente
    
    Headers:
        X-Source: Nome do agente (opcional)
    
    Body: Conteúdo como texto plain
    """
    try:
        content = request.get_data(as_text=True)
        source = request.headers.get('X-Source', 'API')
        
        if not content:
            return jsonify({"error": "Conteúdo vazio"}), 400
        
        success = add_content_to_obsidian(content, source, FOLDER_ID)
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Conteúdo adicionado por {source}",
                "source": source
            }), 200
        else:
            return jsonify({"error": "Falha ao adicionar conteúdo"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"🚀 Obsidian API rodando na porta {port}")
    print(f"📁 Pasta ID: {FOLDER_ID}")
    app.run(host='0.0.0.0', port=port, debug=True)

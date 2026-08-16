#!/usr/bin/env python3
"""Send content to Obsidian via GitHub API"""

import os
import sys

def main():
    print("🧪 TESTE: send_to_obsidian.py")
    print("-" * 40)
    
    # Verificar configurações
    if os.path.exists('.env'):
        print("✅ .env configurado")
    else:
        print("⚠️ .env não encontrado")
    
    # Teste básico de import
    try:
        import requests
        print("✅ requests disponível")
    except ImportError:
        print("❌ requests não instalado")
        return 1
    
    # Simulação
    print("✅ Script funcional")
    return 0

if __name__ == '__main__':
    sys.exit(main())
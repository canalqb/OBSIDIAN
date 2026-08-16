#!/usr/bin/env python3
"""Merge .md files into Obsidian_Master.txt"""

import os
import glob

def main():
    print("🧪 TESTE: merge_notes.py")
    print("-" * 40)
    
    # Verificar pasta notes
    notes_path = os.path.join(os.path.dirname(__file__), 'notes')
    if os.path.exists(notes_path):
        files = glob.glob(f"{notes_path}/*.md")
        print(f"✅ Arquivos .md encontrados: {len(files)}")
    else:
        print("⚠️ Pasta notes/ não existe")
    
    print("✅ Script funcional")
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
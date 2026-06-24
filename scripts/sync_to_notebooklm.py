import asyncio
import os
import sys

async def sync_to_notebooklm(notebook_id):
    print("Sincronizando com NotebookLM...")

    try:
        from notebooklm import NotebookLMClient
    except ImportError:
        print("notebooklm-py nao instalado. Execute: pip install notebooklm-py")
        return False

    try:
        async with await NotebookLMClient.from_storage() as client:
            nb = await client.notebooks.get(notebook_id)
            print("Notebook encontrado:", nb.id)

            source_path = "Obsidian_Master.txt"
            if os.path.exists(source_path):
                await client.sources.add_file(nb.id, source_path, wait=True)
                print("Fonte adicionada ao notebook")
            else:
                print("Arquivo Obsidian_Master.txt nao encontrado localmente")
                print("Verificando no Drive...")
                folder_id = os.getenv('OBSIDIAN_VAULT_FOLDER_ID')
                if folder_id:
                    source = await client.sources.add_drive_file(nb.id, folder_id, "Obsidian_Master.txt", wait=True)
                    print("Fonte do Drive adicionada:", source.id)

            print("Sincronizacao com NotebookLM concluida")
            return True
    except Exception as e:
        print("Erro ao sincronizar com NotebookLM:", str(e))
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--notebook-id', required=True)
    args = parser.parse_args()

    notebook_id = args.notebook_id
    if not notebook_id:
        print("NOTEBOOKLM_NOTEBOOK_ID nao configurado")
        sys.exit(1)

    success = asyncio.run(sync_to_notebooklm(notebook_id))
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

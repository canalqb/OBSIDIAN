import os
import json
import sys

try:
    from sheets_client import SheetsClient
except ImportError:
    print("sheets_client nao encontrado")
    sys.exit(1)

sheet_id = os.getenv('GOOGLE_SHEET')
if not sheet_id:
    print("GOOGLE_SHEET nao configurado")
    sys.exit(1)

try:
    sc = SheetsClient()
    data = sc.read_range(sheet_id, 'Novos_Posts!A:D')
except Exception as e:
    print(f"Erro ao ler planilha: {e}")
    sys.exit(1)

if not data or len(data) < 2:
    print("Nenhum dado na planilha")
    sys.exit(0)

header = data[0]
rows = data[1:]

for i, row in enumerate(rows):
    post_url = row[0].strip() if len(row) > 0 else ''
    drive_link = row[1].strip() if len(row) > 1 else ''
    youtube_link = row[2].strip() if len(row) > 2 else ''
    status = row[3].strip() if len(row) > 3 else ''

    if status == 'concluido':
        continue
    if not post_url:
        continue

    print(f"Post pendente encontrado (linha {i+2}): {post_url}")

    post_id = ''
    if '/blogger' in post_url or 'blogspot' in post_url:
        parts = post_url.rstrip('/').split('/')
        post_id = parts[-1] if parts else ''

    pending = {
        'row': i + 2,
        'post_url': post_url,
        'post_id': post_id,
        'drive_link': drive_link,
        'youtube_link': youtube_link,
        'status': status,
    }

    with open('/tmp/pending_post.json', 'w') as f:
        json.dump(pending, f)

    print(f"Post ID: {post_id}")
    print(f"Status atual: {status}")
    sys.exit(0)

print("Nenhum post pendente encontrado na planilha")
sys.exit(0)

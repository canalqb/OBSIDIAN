from __future__ import annotations

import os, sys
from datetime import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account

sys.path.insert(0, os.path.dirname(__file__))
from blogger_client import BloggerClient
from sheets_client import SheetsClient, SCOPES

load_dotenv()

BLOG_ID = os.getenv('BLOGGER_BLOG_ID', '5982274115355506187')
SHEET_ID = os.getenv('GOOGLE_SHEET')
SHEET_NAME = 'Posts'

def sheet_exists(sheets_service, spreadsheet_id: str, sheet_name: str) -> bool:
    meta = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    return any(s['properties']['title'] == sheet_name for s in meta.get('sheets', []))

def create_sheet_if_missing(sheets_service, spreadsheet_id: str, sheet_name: str):
    if sheet_exists(sheets_service, spreadsheet_id, sheet_name):
        return
    body = {'requests': [{'addSheet': {'properties': {'title': sheet_name}}}]}
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body=body
    ).execute()
    print(f"Aba '{sheet_name}' criada.")

def rebuild_sheet(sheets_service, spreadsheet_id: str, sheet_name: str, rows: list[list[str]]):
    sheets_service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id, range=f'{sheet_name}!A:Z'
    ).execute()
    if rows:
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f'{sheet_name}!A1',
            valueInputOption='USER_ENTERED',
            body={'values': rows},
        ).execute()
    print(f"Aba '{sheet_name}' atualizada com {len(rows)} linhas.")

def main():
    print("=== Download de todas as postagens do Blogger ===")

    bc = BloggerClient()
    print(f"Buscando posts do blog {BLOG_ID}...")
    posts = bc.list_posts(BLOG_ID, max_results=500)
    print(f"Total de posts encontrados: {len(posts)}")

    sc = SheetsClient()
    sheets_service = build('sheets', 'v4', credentials=sc._get_credentials())
    create_sheet_if_missing(sheets_service, SHEET_ID, SHEET_NAME)

    header = [
        'Link do Post',
        'ID do Post',
        'Data de Criação',
        'Data de Modificação',
        'Link Drive',
        'Link YouTube',
        'Status',
    ]

    bc_service = bc.service
    existing = {}
    try:
        old = sc.read_range(SHEET_ID, f'{SHEET_NAME}!A:G')
        if old and len(old) > 1:
            for row in old[1:]:
                if len(row) >= 2:
                    existing[row[1]] = row
    except Exception:
        pass

    rows = [header]
    for post in posts:
        post_id = post['id']
        post_url = post.get('url', '')
        created = post.get('published', '')
        modified = post.get('updated', '')

        old_data = existing.get(post_id, [])
        drive_link = old_data[4] if len(old_data) > 4 else ''
        youtube_link = old_data[5] if len(old_data) > 5 else ''
        status = old_data[6] if len(old_data) > 6 else 'pendente'

        rows.append([post_url, post_id, created, modified, drive_link, youtube_link, status])

    rebuild_sheet(sheets_service, SHEET_ID, SHEET_NAME, rows)
    print("Concluido!")

if __name__ == '__main__':
    main()

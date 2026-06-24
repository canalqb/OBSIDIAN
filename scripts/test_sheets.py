import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

private_key_lines = []
with open('configuracoes_pipeline.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    capture = False
    for line in lines:
        if 'SERVICE_ACCOUNT_PRIVATE_KEY:' in line:
            capture = True
            continue
        if capture:
            stripped = line.strip()
            if stripped.startswith('---') and 'END' in stripped:
                private_key_lines.append(stripped)
                break
            if stripped:
                private_key_lines.append(stripped)

private_key = '\n'.join(private_key_lines)

info = {
    'type': 'service_account',
    'project_id': 'bloggerwindsurf',
    'private_key_id': '3016c1509228b8d415c5370ab3f703e77555ecbe',
    'private_key': private_key,
    'client_email': 'bloggerwindsurf@bloggerwindsurf.iam.gserviceaccount.com',
    'client_id': '',
    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
    'token_uri': 'https://oauth2.googleapis.com/token',
    'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
    'client_x509_cert_url': 'https://www.googleapis.com/robot/v1/metadata/x509/bloggerwindsurf@bloggerwindsurf.iam.gserviceaccount.com',
}

creds = service_account.Credentials.from_service_account_info(info, scopes=['https://www.googleapis.com/auth/spreadsheets'])
service = build('sheets', 'v4', credentials=creds)
sheet_id = '1QGwQVWJ_KiiSHm-LWuK4f32PtJMOsaPYsP-E_Hk3wdI'

result = service.spreadsheets().values().get(
    spreadsheetId=sheet_id,
    range='Novos_Posts!A:A'
).execute()
existing = result.get('values', [])
print(f'Linhas existentes: {len(existing)}')

body = {'values': [[
    'https://www.canalqb.com.br/2026/06/pipeline-automatizado-blogger.html',
    '',
    '',
    'criado'
]]}
result = service.spreadsheets().values().append(
    spreadsheetId=sheet_id,
    range='Novos_Posts!A:D',
    valueInputOption='USER_ENTERED',
    insertDataOption='INSERT_ROWS',
    body=body
).execute()
updated = result.get('updates', {}).get('updatedRange', '')
print(f'Linha adicionada: {updated}')
print('SUCESSO')

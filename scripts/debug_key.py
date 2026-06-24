import json

with open('configuracoes_pipeline.txt', 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('SERVICE_ACCOUNT_PRIVATE_KEY:')
if start > -1:
    rest = content[start:]
    begin = rest.find('-----BEGIN PRIVATE KEY-----')
    end = rest.find('-----END PRIVATE KEY-----')
    if begin > -1 and end > -1:
        raw_key = rest[begin:end + len('-----END PRIVATE KEY-----')]
        raw_key = raw_key.replace('\r\n', '\n').replace('\r', '\n')
        # Remove whitespace-only lines except actual key data
        lines = [l.strip() for l in raw_key.split('\n') if l.strip()]
        pk = '\n'.join(lines)
        print(f'Key length: {len(pk)}')
        print(f'Starts with: {repr(pk[:50])}')
        print(f'Ends with: {repr(pk[-40:])}')

        from google.oauth2 import service_account

        info = {
            'type': 'service_account',
            'project_id': 'bloggerwindsurf',
            'private_key_id': '3016c1509228b8d415c5370ab3f703e77555ecbe',
            'private_key': pk,
            'client_email': 'bloggerwindsurf@bloggerwindsurf.iam.gserviceaccount.com',
            'client_id': '',
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
            'client_x509_cert_url': 'https://www.googleapis.com/robot/v1/metadata/x509/bloggerwindsurf@bloggerwindsurf.iam.gserviceaccount.com',
        }

        creds = service_account.Credentials.from_service_account_info(
            info, scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        print('SUCCESS: Credentials loaded!')

        from googleapiclient.discovery import build
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
        print('SUCESSO!')
    else:
        print('BEGIN/END not found')

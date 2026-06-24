import json, os, requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Read private key
with open('configuracoes_pipeline.txt', 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('SERVICE_ACCOUNT_PRIVATE_KEY:')
rest = content[start:]
begin = rest.find('-----BEGIN PRIVATE KEY-----')
end = rest.find('-----END PRIVATE KEY-----')
raw_key = rest[begin:end + len('-----END PRIVATE KEY-----')]
raw_key = raw_key.replace('\r\n', '\n').replace('\r', '\n')
lines = [l.strip() for l in raw_key.split('\n') if l.strip()]
private_key = '\n'.join(lines)

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

creds = service_account.Credentials.from_service_account_info(
    info,
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)
creds.refresh(Request())
access_token = creds.token
print('Token obtido!')

resp = requests.post(
    'https://serviceusage.googleapis.com/v1/projects/bloggerwindsurf/services/sheets.googleapis.com:enable',
    headers={'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
)
print(f'Status: {resp.status_code}')
data = resp.json()
if resp.status_code == 200:
    print('Sheets API ativada com sucesso!')
elif 'error' in data and data['error'].get('status') == 'NOT_FOUND':
    print(f'Projeto nao encontrado: {data}')
else:
    print(f'Resposta: {json.dumps(data, indent=2)}')

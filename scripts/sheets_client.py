from __future__ import annotations

import json
import os
from typing import Optional, List
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def _build_service_account_info():
    client_email = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL')
    private_key = os.getenv('GOOGLE_PRIVATE_KEY')
    project_id = os.getenv('GOOGLE_PROJECT_ID')
    private_key_id = os.getenv('GOOGLE_PRIVATE_KEY_ID')

    if all([client_email, private_key, project_id, private_key_id]):
        if private_key and '\\n' in private_key:
            private_key = private_key.replace('\\n', '\n')
        return {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": private_key_id,
            "private_key": private_key,
            "client_email": client_email,
            "client_id": "",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email}",
        }

    config_file = 'service_account.json'
    if os.path.exists(config_file):
        with open(config_file) as f:
            return json.load(f)

    config_file = 'configuracoes_pipeline.txt'
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        start = content.find('SERVICE_ACCOUNT_PRIVATE_KEY:')
        if start >= 0:
            rest = content[start:]
            begin = rest.find('-----BEGIN PRIVATE KEY-----')
            end = rest.find('-----END PRIVATE KEY-----')
            raw_key = rest[begin:end + len('-----END PRIVATE KEY-----')]
            raw_key = raw_key.replace('\r\n', '\n').replace('\r', '\n')
            lines = [l.strip() for l in raw_key.split('\n') if l.strip()]
            pk = '\n'.join(lines)
            return {
                "type": "service_account",
                "project_id": "bloggerwindsurf",
                "private_key_id": "3016c1509228b8d415c5370ab3f703e77555ecbe",
                "private_key": pk,
                "client_email": "bloggerwindsurf@bloggerwindsurf.iam.gserviceaccount.com",
                "client_id": "",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/bloggerwindsurf@bloggerwindsurf.iam.gserviceaccount.com",
            }

    raise EnvironmentError("Service account credentials nao encontradas")


class SheetsClient:
    def __init__(self):
        self._service = None

    def _get_credentials(self):
        info = _build_service_account_info()
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)

    @property
    def service(self):
        if self._service is None:
            self._service = build('sheets', 'v4', credentials=self._get_credentials())
        return self._service

    def append_row(self, spreadsheet_id: str, range_name: str, values: List[str]) -> dict:
        body = {'values': [values]}
        result = self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body,
        ).execute()
        return result

    def update_cell(self, spreadsheet_id: str, range_name: str, value: str) -> dict:
        body = {'values': [[value]]}
        result = self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body,
        ).execute()
        return result

    def read_range(self, spreadsheet_id: str, range_name: str) -> List[List[str]]:
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name,
        ).execute()
        return result.get('values', [])

    def find_row_by_post_url(self, spreadsheet_id: str, post_url: str) -> Optional[int]:
        data = self.read_range(spreadsheet_id, 'Novos_Posts!A:A')
        for i, row in enumerate(data):
            if row and post_url in row[0]:
                return i + 1
        return None

    def update_youtube_link(self, spreadsheet_id: str, post_url: str, youtube_url: str):
        row = self.find_row_by_post_url(spreadsheet_id, post_url)
        if row:
            self.update_cell(spreadsheet_id, f'Novos_Posts!C{row}', youtube_url)
            print(f"Planilha atualizada: linha {row}, coluna C (YouTube)")

    def update_drive_link(self, spreadsheet_id: str, post_url: str, drive_url: str):
        row = self.find_row_by_post_url(spreadsheet_id, post_url)
        if row:
            self.update_cell(spreadsheet_id, f'Novos_Posts!B{row}', drive_url)
            print(f"Planilha atualizada: linha {row}, coluna B (Drive)")

    def update_status(self, spreadsheet_id: str, post_url: str, status: str):
        row = self.find_row_by_post_url(spreadsheet_id, post_url)
        if row:
            self.update_cell(spreadsheet_id, f'Novos_Posts!D{row}', status)
            print(f"Planilha atualizada: linha {row}, coluna D (Status: {status})")

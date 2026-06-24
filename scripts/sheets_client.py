from __future__ import annotations

import os
from typing import Optional, List
from google.oauth2 import credentials as google_credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class SheetsClient:
    def __init__(self):
        self._service = None

    def _get_credentials(self):
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
        if not all([client_id, client_secret, refresh_token]):
            raise EnvironmentError("GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET e GOOGLE_REFRESH_TOKEN obrigatorios")
        creds = google_credentials.Credentials(
            token=None, refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id, client_secret=client_secret,
            scopes=SCOPES,
        )
        creds.refresh(Request())
        return creds

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

    def find_row_by_post_id(self, spreadsheet_id: str, post_url: str) -> Optional[int]:
        data = self.read_range(spreadsheet_id, 'Novos_Posts!A:A')
        for i, row in enumerate(data):
            if row and post_url in row[0]:
                return i + 1
        return None

    def update_youtube_link(self, spreadsheet_id: str, post_url: str, youtube_url: str):
        row = self.find_row_by_post_id(spreadsheet_id, post_url)
        if row:
            self.update_cell(spreadsheet_id, f'Novos_Posts!C{row}', youtube_url)
            print(f"Planilha atualizada: linha {row}, coluna C (YouTube)")

    def update_drive_link(self, spreadsheet_id: str, post_url: str, drive_url: str):
        row = self.find_row_by_post_id(spreadsheet_id, post_url)
        if row:
            self.update_cell(spreadsheet_id, f'Novos_Posts!B{row}', drive_url)
            print(f"Planilha atualizada: linha {row}, coluna B (Drive)")

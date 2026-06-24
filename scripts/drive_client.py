"""
drive_client.py — Cliente Google Drive centralizado
Elimina duplicação de código OAuth em todos os scripts.
"""

from __future__ import annotations

import os
import io
import time
import functools
from datetime import datetime
from typing import Optional, List
from google.oauth2 import credentials as google_credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError


# ── Retry decorator ─────────────────────────────────────────────────────────

def retry(max_attempts=3, delay=2, backoff=2, exceptions=(Exception,)):
    """Decorator para retry com backoff exponencial."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        raise
                    print(f"[RETRY] Tentativa {attempt}/{max_attempts} falhou: {e}")
                    print(f"[RETRY] Aguardando {current_delay}s antes de tentar novamente...")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator


# ── DriveClient ──────────────────────────────────────────────────────────────

class DriveClient:
    """
    Cliente Google Drive com autenticação OAuth centralizada.
    Usa variáveis de ambiente — nunca credenciais hard-coded.
    """

    def __init__(self):
        self._service = None

    def _get_credentials(self):
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')

        if not all([client_id, client_secret, refresh_token]):
            raise EnvironmentError(
                "Variáveis de ambiente ausentes: GOOGLE_CLIENT_ID, "
                "GOOGLE_CLIENT_SECRET e GOOGLE_REFRESH_TOKEN são obrigatórias."
            )

        creds = google_credentials.Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=['https://www.googleapis.com/auth/drive'],
        )
        creds.refresh(Request())
        return creds

    @property
    def service(self):
        if self._service is None:
            self._service = build('drive', 'v3', credentials=self._get_credentials())
        return self._service

    # ── Busca de arquivos ────────────────────────────────────────────────────

    @retry(max_attempts=3, delay=2, exceptions=(HttpError, Exception))
    def find_file(self, name: str, folder_id: str = None) -> Optional[dict]:
        """
        Retorna metadados do primeiro arquivo com o nome dado.
        Retorna None se não encontrar.
        """
        query = f"name='{name}' and trashed=false"
        if folder_id:
            query += f" and '{folder_id}' in parents"

        results = self.service.files().list(
            q=query,
            fields="files(id, name, modifiedTime, size)",
            pageSize=5,
        ).execute()

        files = results.get('files', [])
        return files[0] if files else None

    # ── Leitura ──────────────────────────────────────────────────────────────

    @retry(max_attempts=3, delay=2, exceptions=(HttpError, Exception))
    def read_file(self, file_id: str) -> str:
        """Lê e retorna o conteúdo de um arquivo como string UTF-8."""
        raw = self.service.files().get_media(fileId=file_id).execute()
        return raw.decode('utf-8') if isinstance(raw, bytes) else str(raw)

    # ── Escrita / atualização ────────────────────────────────────────────────

    @retry(max_attempts=3, delay=2, exceptions=(HttpError, Exception))
    def write_file(self, file_id: str, content: str) -> str:
        """Atualiza o conteúdo de um arquivo existente. Retorna o file_id."""
        fh = io.BytesIO(content.encode('utf-8'))
        media = MediaIoBaseUpload(fh, mimetype='text/plain', resumable=True)
        result = self.service.files().update(
            fileId=file_id,
            media_body=media,
            fields='id',
        ).execute()
        return result['id']

    @retry(max_attempts=3, delay=2, exceptions=(HttpError, Exception))
    def create_file(self, name: str, content: str, folder_id: str,
                    mimetype: str = 'text/plain') -> str:
        """Cria um novo arquivo no Drive. Retorna o file_id."""
        metadata = {'name': name, 'parents': [folder_id], 'mimeType': mimetype}
        fh = io.BytesIO(content.encode('utf-8'))
        media = MediaIoBaseUpload(fh, mimetype=mimetype, resumable=True)
        result = self.service.files().create(
            body=metadata, media_body=media, fields='id'
        ).execute()
        return result['id']

    def upsert_file(self, name: str, content: str, folder_id: str) -> str:
        """Cria ou atualiza o arquivo. Retorna o file_id."""
        existing = self.find_file(name, folder_id)
        if existing:
            return self.write_file(existing['id'], content)
        return self.create_file(name, content, folder_id)

    # ── Listagem ─────────────────────────────────────────────────────────────

    @retry(max_attempts=3, delay=2, exceptions=(HttpError, Exception))
    def list_files(self, folder_id: str, mime_filter: str = None,
                   extension: str = None) -> List[dict]:
        """Lista arquivos em uma pasta com paginação completa."""
        query = f"'{folder_id}' in parents and trashed=false"
        if mime_filter:
            query += f" and mimeType='{mime_filter}'"

        all_files = []
        page_token = None

        while True:
            kwargs = dict(
                q=query,
                fields="nextPageToken, files(id, name, modifiedTime)",
                pageSize=200,
            )
            if page_token:
                kwargs['pageToken'] = page_token

            results = self.service.files().list(**kwargs).execute()
            files = results.get('files', [])

            if extension:
                files = [f for f in files if f['name'].endswith(extension)]

            all_files.extend(files)
            page_token = results.get('nextPageToken')
            if not page_token:
                break

        return all_files

    @retry(max_attempts=3, delay=2, exceptions=(HttpError, Exception))
    def list_folders(self, folder_id: str) -> List[dict]:
        """Lista subpastas de uma pasta."""
        return self.list_files(
            folder_id,
            mime_filter='application/vnd.google-apps.folder'
        )

    # ── Metadados ─────────────────────────────────────────────────────────────

    @retry(max_attempts=3, delay=2, exceptions=(HttpError, Exception))
    def get_modified_time(self, file_id: str) -> str:
        """Retorna a data de modificação ISO 8601 do arquivo."""
        result = self.service.files().get(
            fileId=file_id, fields='modifiedTime'
        ).execute()
        return result.get('modifiedTime', '')

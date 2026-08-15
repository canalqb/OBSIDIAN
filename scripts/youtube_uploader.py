from __future__ import annotations

import os
import json
from typing import Optional, List
from google.oauth2 import credentials as google_credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubeUploader:
    def __init__(self):
        self._service = None

    def _get_credentials(self):
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
        if not all([client_id, client_secret, refresh_token]):
            raise EnvironmentError(
                "Variaveis de ambiente ausentes: GOOGLE_CLIENT_ID, "
                "GOOGLE_CLIENT_SECRET e GOOGLE_REFRESH_TOKEN sao obrigatorias."
            )
        creds = google_credentials.Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=SCOPES,
        )
        creds.refresh(Request())
        return creds

    @property
    def service(self):
        if self._service is None:
            self._service = build("youtube", "v3", credentials=self._get_credentials())
        return self._service

    def upload_video(
        self,
        file_path: str,
        title: str,
        description: str = "",
        tags: Optional[List[str]] = None,
        privacy_status: str = "private",
        category_id: str = "28",
    ) -> dict:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Arquivo nao encontrado: {file_path}")

        body = {
            "snippet": {
                "title": title[:100],
                "description": description[:5000],
                "tags": tags[:500] if tags else [],
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)

        print(f"Enviando video para YouTube (privado): {title}")
        request = self.service.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"Progresso: {progress}%")

        video_id = response.get("id")
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        print(f"Video enviado com sucesso!")
        print(f"  ID: {video_id}")
        print(f"  URL: {video_url}")
        print(f"  Status: {privacy_status}")

        return {
            "video_id": video_id,
            "video_url": video_url,
            "title": title,
            "privacy_status": privacy_status,
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Upload video para YouTube (privado)")
    parser.add_argument("--file", required=True, help="Caminho do arquivo de video")
    parser.add_argument("--title", required=True, help="Titulo do video")
    parser.add_argument("--description", default="", help="Descricao do video")
    parser.add_argument("--tags", default="", help="Tags separadas por virgula")
    parser.add_argument("--privacy", default="private",
                        choices=["private", "unlisted", "public"],
                        help="Status de privacidade (padrao: private)")
    args = parser.parse_args()

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    uploader = YouTubeUploader()
    result = uploader.upload_video(
        file_path=args.file,
        title=args.title,
        description=args.description,
        tags=tags,
        privacy_status=args.privacy,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

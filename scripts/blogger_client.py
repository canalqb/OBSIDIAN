from __future__ import annotations

import os
from typing import Optional, List
from dotenv import load_dotenv
from google.oauth2 import credentials as google_credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

load_dotenv()


class BloggerClient:
    def __init__(self):
        self._service = None

    def _get_credentials(self):
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')

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
            scopes=['https://www.googleapis.com/auth/blogger'],
        )
        creds.refresh(Request())
        return creds

    @property
    def service(self):
        if self._service is None:
            self._service = build('blogger', 'v3', credentials=self._get_credentials())
        return self._service

    def publish_post(self, blog_id: str, title: str, content: str,
                     labels: Optional[List[str]] = None) -> dict:
        body = {
            'kind': 'blogger#post',
            'title': title,
            'content': content,
        }
        if labels:
            body['labels'] = labels

        post = self.service.posts().insert(
            blogId=blog_id,
            body=body,
            isDraft=False,
        ).execute()
        return post

    def update_post(self, blog_id: str, post_id: str, content: str,
                    title: Optional[str] = None) -> dict:
        existing = self.service.posts().get(
            blogId=blog_id,
            postId=post_id,
            view='ADMIN',
        ).execute()
        existing['content'] = content
        if title:
            existing['title'] = title
        updated = self.service.posts().update(
            blogId=blog_id,
            postId=post_id,
            body=existing,
        ).execute()
        return updated

    def add_youtube_embed(self, blog_id: str, post_id: str,
                          video_id: str, video_title: str = "") -> dict:
        existing = self.service.posts().get(
            blogId=blog_id,
            postId=post_id,
            view='ADMIN',
        ).execute()

        embed_html = (
            '<div style="margin-bottom:30px;text-align:center">'
            '<iframe allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
            'gyroscope; picture-in-picture" allowfullscreen loading="lazy" '
            'height="450" width="100%" '
            'src="https://www.youtube.com/embed/' + video_id
            + '?origin=https://www.canalqb.com.br/&controls=1&rel=0" '
            'title="Video do @CanalQb \u2014 ' + video_title + '" '
            'aria-label="Video tutorial @CanalQb" '
            'style="border:none;border-radius:10px;max-width:100%">'
            '</iframe></div>'
        )

        existing['content'] = embed_html + '\n' + existing['content']
        updated = self.service.posts().update(
            blogId=blog_id,
            postId=post_id,
            body=existing,
        ).execute()
        return updated

    def get_post(self, blog_id: str, post_id: str) -> dict:
        return self.service.posts().get(
            blogId=blog_id,
            postId=post_id,
            view='ADMIN',
        ).execute()

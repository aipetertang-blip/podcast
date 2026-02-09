#!/usr/bin/env python3
import json
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

BASE_DIR = Path('/home/ttang/.openclaw/workspace/daily_podcast')
TOKEN_FILE = BASE_DIR / 'youtube_token.json'
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly',
]
OUT = BASE_DIR / 'weekly_report_latest.json'


def get_service():
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    return build('youtube', 'v3', credentials=creds)


def iso(dt):
    return dt.replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def main():
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    try:
        youtube = get_service()
        search = youtube.search().list(
            part='id,snippet',
            forMine=True,
            type='video',
            order='date',
            maxResults=20,
            publishedAfter=iso(week_ago),
        ).execute()

        ids = [i['id']['videoId'] for i in search.get('items', []) if i.get('id', {}).get('videoId')]
        if not ids:
            OUT.write_text(json.dumps({'videos': [], 'summary': {'count': 0}}, indent=2), encoding='utf-8')
            print(str(OUT))
            return

        detail = youtube.videos().list(part='snippet,statistics,contentDetails', id=','.join(ids)).execute()

        videos = []
        view_list = []
        for it in detail.get('items', []):
            s = it.get('statistics', {})
            views = int(s.get('viewCount', 0))
            likes = int(s.get('likeCount', 0)) if s.get('likeCount') is not None else 0
            comments = int(s.get('commentCount', 0)) if s.get('commentCount') is not None else 0
            view_list.append(views)
            videos.append({
                'videoId': it.get('id'),
                'title': it.get('snippet', {}).get('title'),
                'publishedAt': it.get('snippet', {}).get('publishedAt'),
                'url': f"https://www.youtube.com/watch?v={it.get('id')}",
                'views': views,
                'likes': likes,
                'comments': comments,
            })

        videos.sort(key=lambda x: x['views'], reverse=True)
        summary = {
            'count': len(videos),
            'totalViews': sum(view_list),
            'avgViews': round(statistics.mean(view_list), 2) if view_list else 0,
            'medianViews': statistics.median(view_list) if view_list else 0,
            'topVideo': videos[0] if videos else None,
            'generatedAt': iso(now),
        }

        OUT.write_text(json.dumps({'videos': videos, 'summary': summary}, indent=2), encoding='utf-8')
        print(str(OUT))
    except HttpError as e:
        data = {
            'videos': [],
            'summary': {'count': 0, 'generatedAt': iso(now)},
            'error': 'insufficientPermissions',
            'remediation': 'Update OAuth scope to include https://www.googleapis.com/auth/youtube.readonly and re-authorize.',
            'detail': str(e),
        }
        OUT.write_text(json.dumps(data, indent=2), encoding='utf-8')
        print(str(OUT))


if __name__ == '__main__':
    main()

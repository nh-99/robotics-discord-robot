from tiktokapipy.api import TikTokAPI
from itertools import islice


def get_latest_video_url(username: str):
    with TikTokAPI() as api:
        user = api.user(username)
        for video in islice(user.videos, 1):
            return f'https://tiktok.com/@{username}/video/{video.id}'

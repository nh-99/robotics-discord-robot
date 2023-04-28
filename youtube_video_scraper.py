import requests
import settings

def get_latest_video_url(channel_id: str):
    response = requests.get(f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults=1&order=date&type=video&key={settings.GOOGLE_API_KEY}")
    video_id = response.json()["items"][0]["id"]["videoId"]
    return f"https://www.youtube.com/watch?v={video_id}"
    

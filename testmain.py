import os
import datetime
import requests
from googleapiclient.discovery import build

# 這裡填入你的API金鑰和Discord Webhook URL
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_TEST')
DISCORD_WEBHOOK_URL_ALT = os.getenv('DISCORD_WEBHOOK_ALT')  # 新的Webhook URL

# YouTube API客戶端
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def check_videos(channel_id, keywords, special_keywords):
    # 獲取頻道的最新影片
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        order="date",
        type="video",
        publishedAfter=(datetime.datetime.utcnow() - datetime.timedelta(hours=12)).isoformat() + 'Z'
    )
    response = request.execute()

    for item in response.get('items', []):
        video_title = item['snippet']['title']
        video_id = item['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # 檢查視頻標題是否包含任何一般關鍵字
        if any(keyword.lower() in video_title.lower() for keyword in keywords):
            # 檢查視頻標題是否包含特殊關鍵字
            if any(special_keyword in video_title for special_keyword in special_keywords):
                post_to_discord(item['snippet']['channelTitle'], video_title, video_url, DISCORD_WEBHOOK_URL)
            else:
                post_to_discord(item['snippet']['channelTitle'], video_title, video_url, DISCORD_WEBHOOK_URL_ALT)

def post_to_discord(channel_name, video_title, video_url, webhook_url):
    # 將信息發送到Discord
    data = {
        "content": f"新影片發布：{video_title}\n頻道：{channel_name}\n網址：{video_url}"
    }
    requests.post(webhook_url, json=data)

# 這裡填入要監控的YouTube頻道ID和關鍵字
CHANNEL_IDS = ['UCxH2mFGJOqJ15UyCiZ7rN9w', 'UCpI7QnTiStXbCB3_Qnx96Tg','UCvN59KwVSCv0KaAUuAYyUew','UClu2SdimbmQCzSrlBSzLXSg','UCLDeAj5mc1yhiWyUXQ3gxLg','UClu2SdimbmQCzSrlBSzLXSg','UC6bVPRmwuNS7NC0AjkGpJAA','UCMUMvpp2o4jvP5kYovDOu9w']
KEYWORDS = ['戰隊戰']
SPECIAL_KEYWORDS = ['四階段', '4階段', '補償', '短時間']  # 特殊關鍵字

for channel_id in CHANNEL_IDS:
    check_videos(channel_id, KEYWORDS, SPECIAL_KEYWORDS)
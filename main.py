import os
import datetime
import requests
from googleapiclient.discovery import build

# 初始化 YouTube API 客戶端
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# 為每個頻道配置一個 Discord Webhook URL
DISCORD_WEBHOOK_URLS = {
    'UCxH2mFGJOqJ15UyCiZ7rN9w': os.getenv('DISCORD_WEBHOOK_URL_CHANNEL1'),
    'UCpI7QnTiStXbCB3_Qnx96Tg': os.getenv('DISCORD_WEBHOOK_URL_CHANNEL2'),
    # 添加更多頻道和對應的 Webhook URLs
}

def check_videos(channel_id, keywords):
    # 獲取頻道的最新視頻
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        order="date",
        type="video",
        publishedAfter=(datetime.datetime.utcnow() - datetime.timedelta(days=1)).isoformat() + 'Z'
    )
    response = request.execute()

    for item in response.get('items', []):
        video_title = item['snippet']['title']
        video_id = item['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # 檢查視頻標題是否包含任何關鍵字
        if any(keyword.lower() in video_title.lower() for keyword in keywords):
            post_to_discord(channel_id, item['snippet']['channelTitle'], video_title, video_url)

def post_to_discord(channel_id, channel_name, video_title, video_url):
    webhook_url = DISCORD_WEBHOOK_URLS.get(channel_id)
    if webhook_url:
        data = {
            "content": f"新影片發布：{video_title}\n頻道：{channel_name}\n網址：{video_url}"
        }
        requests.post(webhook_url, data=data)

# 監控的 YouTube 頻道 ID 和關鍵字
CHANNEL_IDS = ['UCxH2mFGJOqJ15UyCiZ7rN9w', 'UCpI7QnTiStXbCB3_Qnx96Tg']
KEYWORDS = ['戰隊戰']

for channel_id in CHANNEL_IDS:
    check_videos(channel_id, KEYWORDS)

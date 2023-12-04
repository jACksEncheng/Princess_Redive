import os
import datetime
import requests
from googleapiclient.discovery import build

# 填入不同的API金鑰和Discord Webhook URLs，每个关键字对应一个Webhook URL
YOUTUBE_API_KEYS = {
    'keyword1': os.getenv('YOUTUBE_API_KEY'),
    # 添加更多关键字和相应的API金鑰
}

DISCORD_WEBHOOK_URLS = {
    'keyword1': os.getenv('DISCORD_WEBHOOK_URL'),
    'keyword2': os.getenv('DISCORD_WEBHOOK_URL_2'),
    # 添加更多关键字和相应的Webhook URL
}

# YouTube API客户端
youtube_clients = {keyword: build('youtube', 'v3', developerKey=api_key) for keyword, api_key in YOUTUBE_API_KEYS.items()}

def check_videos(channel_id, keywords):
    for keyword in keywords:
        youtube = youtube_clients.get(keyword)
        if not youtube:
            continue

        # 获取频道的最新影片
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            order="date",
            type="video",
            publishedAfter=(datetime.datetime.utcnow() - datetime.timedelta(days=8)).isoformat() + 'Z'
        )
        response = request.execute()

        for item in response.get('items', []):
            video_title = item['snippet']['title']
            video_id = item['id']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            # 检查视频标题是否包含当前关键字
            if keyword.lower() in video_title.lower():
                post_to_discord(item['snippet']['channelTitle'], video_title, video_url, keyword)

def post_to_discord(channel_name, video_title, video_url, keyword):
    # 将信息发送到对应的 Discord Webhook
    webhook_url = DISCORD_WEBHOOK_URLS.get(keyword)
    if not webhook_url:
        return

    data = {
        "content": f"新影片发表：{video_title}\n频道：{channel_name}\n网址：{video_url}"
    }
    requests.post(webhook_url, data=data)

# 填入要监控的 YouTube 频道 ID 和相应的关键字
CHANNEL_KEYWORDS = {
    'UCxH2mFGJOqJ15UyCiZ7rN9w': ['keyword1'],
    'UCpI7QnTiStXbCB3_Qnx96Tg': ['keyword2'],
    'UCvN59KwVSCv0KaAUuAYyUew': ['keyword1', 'keyword2'],
    # 添加更多频道和关键字
}

for channel_id, keywords in CHANNEL_KEYWORDS.items():
    check_videos(channel_id, keywords)

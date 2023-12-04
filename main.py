import os
import datetime
import discord
from googleapiclient.discovery import build

# 這裡填入你的API金鑰和Discord Token
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# YouTube API客戶端
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

client = discord.Client()

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')
    # 這裡填入要監控的YouTube頻道ID和關鍵字
    CHANNEL_IDS = ['UCxH2mFGJOqJ15UyCiZ7rN9w', 'UCpI7QnTiStXbCB3_Qnx96Tg']
    KEYWORDS = ['戰隊戰','超異域公主連結']

    for channel_id in CHANNEL_IDS:
        await check_videos(channel_id, KEYWORDS)

async def check_videos(channel_id, keywords):
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
            await post_to_discord(item['snippet']['channelTitle'], video_title, video_url)

async def post_to_discord(channel_name, video_title, video_url):
    # 創建 Discord 文本消息
    message = f"新影片發布：{video_title}\n頻道：{channel_name}\n網址：{video_url}"

    # 獲取您的 Discord 伺服器中的特定文本頻道
    # 假設您有一個名為 "general" 的文本頻道
    channel = client.get_channel(997108672784236627)  # 將 YOUR_TEXT_CHANNEL_ID 替換為實際的文本頻道ID

    # 發送消息到指定的文本頻道
    if channel:
        await channel.send(message)

# 啟動 Discord 客戶端
client.run(DISCORD_TOKEN)

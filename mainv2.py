import os
import datetime
import requests
from googleapiclient.discovery import build

# 這裡填入你的API金鑰和Discord Webhook URL
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# YouTube API客戶端
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def get_full_video_description(video_id):
    # 使用videos().list方法獲取完整的資訊欄文字
    video_request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    video_response = video_request.execute()
    description = video_response.get('items', [])[0]['snippet']['description']
    return description

def check_videos(channel_id, keywords):
    # 獲取頻道的最新影片
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        order="date",
        type="video",
        publishedAfter=(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3)).isoformat()
    )
    response = request.execute()

    for item in response.get('items', []):
        video_title = item['snippet']['title']
        video_id = item['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # 獲取完整的資訊欄文字
        video_description = get_full_video_description(video_id)

        # 檢查視頻標題是否包含任何關鍵字
        if any(keyword.lower() in video_title.lower() for keyword in keywords):
            post_to_discord(item['snippet']['channelTitle'], video_title, video_url, video_description)

def post_to_discord(channel_name, video_title, video_url, video_description):
    # 定義一個包含不需要的字串的列表
    unwanted_strings = ["隊伍來源：日版影片", "公主連結台版戰隊戰作業群：", "會有人幫忙貼戰隊戰作業","也可在戰隊戰期間問作業問題","裡面有補償刀文字軸秒數轉換機器人可以使用","平時也歡迎各位過來閒聊","==================="
                       ,"https://youtu.be/Odrce0CBqYE","https://youtu.be/bU-EzqD4eR8","https://discord.gg/VFbFf9QeXY"]

    # 遍歷列表並從描述中移除這些字串
    filtered_description = video_description
    for unwanted in unwanted_strings:
        filtered_description = filtered_description.replace(unwanted, "")

    # 將信息發送到Discord
    data = {
        "content": f"新影片發布：{video_title}\n頻道：{channel_name}\n網址：{video_url}\n描述：{filtered_description}"
    }
    requests.post(DISCORD_WEBHOOK_URL, data=data)

# 這裡填入要監控的YouTube頻道ID和關鍵字
CHANNEL_IDS = ['UCxH2mFGJOqJ15UyCiZ7rN9w', 'UCpI7QnTiStXbCB3_Qnx96Tg','UCvN59KwVSCv0KaAUuAYyUew']
KEYWORDS = ['戰隊戰','公主']

for channel_id in CHANNEL_IDS:
    check_videos(channel_id, KEYWORDS)

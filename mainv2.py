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
        publishedAfter=(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).isoformat()
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
    unwanted_strings = ["公主連結台版戰隊戰作業群：", "會有人幫忙貼戰隊戰作業", "也可在戰隊戰期間問作業問題", "裡面有補償刀文字軸秒數轉換機器人可以使用"
                        , "平時也歡迎各位過來閒聊", "===================", "https://discord.gg/VFbFf9QeXY", "=================="
                        , "目前台版角色推薦星數/RANK :https://docs.google.com/spreadsheets/d/1KCUY8o77sR0llFn1aTBaM-q6YuiBM5E73HwqPbeKVAw/edit#gid=1483537175"
                        , "介紹單機遊戲的副頻道:http://www.youtube.com/c/煌靈的副頻道", "FB粉絲團:https://www.facebook.com/%E7%85%8C%E9%9D%88longtimenoc-109066521597298"
                        , "我目前使用的NORD VPN:https://nordvpn.com/longtimenoc", "專屬折扣券: longtimenoc", "推薦玩公主連結的模擬器:BS5", "下載連結:https://bstk.me/owTWv5GFy"
                        , "本頻道影片請勿轉載至其他影片網站，謝謝", "DISCORD歡樂觀眾聊天群:https://discord.gg/kAwDuM5", "合作信箱:D878749122@gmail.com"]

    # 遍歷列表並從描述中移除這些字串
    filtered_description = video_description
    for unwanted in unwanted_strings:
        filtered_description = filtered_description.replace(unwanted, "")

    # 為 URL 添加尖括號以取消網址預覽
    video_url_with_no_preview = f" <{video_url}> "

    # 將信息發送到Discord
    data = {
        "content": f"新影片發布：{video_title}\n頻道：{channel_name}\n網址：{video_url_with_no_preview}\n描述：{filtered_description}"
    }
    requests.post(DISCORD_WEBHOOK_URL, data=data)

# 這裡填入要監控的YouTube頻道ID和關鍵字
CHANNEL_IDS = ['UCxH2mFGJOqJ15UyCiZ7rN9w', 'UCpI7QnTiStXbCB3_Qnx96Tg','UCvN59KwVSCv0KaAUuAYyUew']
KEYWORDS = ['戰隊戰']

for channel_id in CHANNEL_IDS:
    check_videos(channel_id, KEYWORDS)

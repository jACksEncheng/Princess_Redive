import os
import datetime
import requests
import subprocess
import cv2
import numpy as np
from googleapiclient.discovery import build

# 環境變數：YouTube API金鑰和Discord Webhook URL
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# YouTube API客戶端
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def check_videos(channel_id, keywords):
    # 獲取頻道的最新影片
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
            video_path = download_video(video_url)
            process_video(video_path, item['snippet']['channelTitle'])

def download_video(video_url):
    # 使用youtube-dl下載影片
    video_path = 'downloaded_video.mp4'
    subprocess.run(["youtube-dl", video_url, "-f", "best", "-o", video_path])
    return video_path

def capture_screenshot(frame, frame_number):
    # 截圖並保存
    screenshot_path = f'screenshot_{frame_number}.png'
    cv2.imwrite(screenshot_path, frame)
    return screenshot_path

def post_to_discord(channel_name, video_title, screenshot_path):
    # 將截圖信息發送到Discord
    data = {
        "content": f"新影片發布：{video_title}\n頻道：{channel_name}\n截圖：查看附件",
    }
    files = {'file': open(screenshot_path, 'rb')}
    response = requests.post(DISCORD_WEBHOOK_URL, data=data, files=files)
    files['file'].close()

def process_video(video_path, channel_name):
    cap = cv2.VideoCapture(video_path)
    previous_frame_roi = None
    frame_number = 0
    threshold = 50000  # 需要根據實際影片調整這個閾值

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 定義紅色方框區域的位置 (x, y, width, height)
        x, y, w, h = 600, 300, 100, 100  # 需要根據實際情況設定這些值

        # 獲取當前幀的感興趣區域
        current_frame_roi = frame[y:y+h, x:x+w]
        frame_number += 1

        if previous_frame_roi is not None:
            # 比較前一幀與當前幀的區域內容
            difference = cv2.absdiff(previous_frame_roi, current_frame_roi)
            difference = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
            _, difference = cv2.threshold(difference, 30, 255, cv2.THRESH_BINARY)

            # 如果變化足夠大，認定為角色變化，進行截圖
            if np.sum(difference) > threshold:
                screenshot_path = capture_screenshot(current_frame_roi, frame_number)
                post_to_discord(channel_name, "角色變化截圖", screenshot_path)

        previous_frame_roi = current_frame_roi

    cap.release()

# 要監控的YouTube頻道ID和關鍵字
CHANNEL_IDS = ['UCxH2mFGJOqJ15UyCiZ7rN9w']
KEYWORDS = ['關鍵字']

for channel_id in CHANNEL_IDS:
    check_videos(channel_id, KEYWORDS)

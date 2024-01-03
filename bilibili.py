import asyncio
import requests
from bilibili_api import video, sync
from datetime import datetime, timedelta

# Discord Webhook URL
DISCORD_WEBHOOK_URL = None

async def check_videos(up_ids, keywords):
    # 计算N天前的日期
    days_ago = datetime.now() - timedelta(days=14)

    for keyword in keywords:
        # 使用关键字搜索视频
        v = video.Video(UP_IDS)
        search_result = await v.get_info(keyword, search_type="video", publish_time_from=days_ago)

        for item in search_result['result']:
            video_title = item['title']
            up_id = item['author_mid']
            video_url = f"https://www.bilibili.com/video/{item['bvid']}"

            # 检查视频是否来自指定的 UP 主
            if str(up_id) in up_ids:
                post_to_discord(item['author'], video_title, video_url)

def post_to_discord(channel_name, video_title, video_url):
    global DISCORD_WEBHOOK_URL
    if DISCORD_WEBHOOK_URL is None:
        DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_TEST')
    data = {
        "content": f"新影片發布：{video_title}\n頻道：{channel_name}\n網址：{video_url}"
    }
    requests.post(DISCORD_WEBHOOK_URL, data=data)

# 这里填入要监控的 UP 主 ID 和关键字
UP_IDS = 'BV16C4y1378y' # 示例 UP 主 ID
KEYWORDS = ['戰隊戰']

# 主函数
def main():
    asyncio.run(check_videos(UP_IDS, KEYWORDS))

if __name__ == "__main__":
    main()

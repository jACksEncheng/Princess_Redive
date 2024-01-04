import os
import asyncio
import json
from bilibili_api import user
import aiohttp
from datetime import datetime, timezone, timedelta

# Discord Webhook URL
webhook_url = os.getenv('DISCORD_WEBHOOK_URL')  # 請將此處替換為您的 Discord Webhook URL

# Bilibili 用戶的 UID
uid = 33383193  # 請將此處替換為實際的 UID

u = user.User(uid=uid)

def getVideoItem(input, timestamp):
    item = {}
    if input.get("title"):
        item["title"] = input["title"]
    if aid := input.get("aid"):
        item["aid"] = aid
        item["url"] = f"https://www.bilibili.com/video/av{aid}"
    # 將 timestamp 轉換為台灣時間（UTC+8）
    dt = datetime.fromtimestamp(timestamp, tz=timezone(timedelta(hours=8)))
    item["timestamp"] = dt.strftime('%Y-%m-%d %H:%M:%S')  # 格式化時間
    return item

def cardToObj(card_data):
    card = json.loads(card_data["card"]) if isinstance(card_data["card"], str) else card_data["card"]
    timestamp = card_data["desc"]["timestamp"]
    return getVideoItem(card, timestamp)

async def send_to_discord(cardObj):
    if cardObj:
        async with aiohttp.ClientSession() as session:
            discord_message = {
                "content": f"標題: {cardObj.get('title', 'No Title')}\n"
                           f"影片網址: {cardObj.get('url', 'No URL')}\n"
                           f"上傳時間: {cardObj.get('timestamp', 'No Timestamp')}"
            }
            response = await session.post(webhook_url, json=discord_message)
            if response.status == 200:
                print("Message sent successfully")
            else:
                print(f"Failed to send message: {response.status} {response.reason}")

async def main():
    offset = 0
    max_posts = 3
    count = 0
    keyword = "公主连结"
    while True:
        res = await u.get_dynamics(offset)
        if res["has_more"] != 1 or count >= max_posts:
            break
        offset = res["next_offset"]
        for card in res["cards"]:
            if count >= max_posts:
                break
            cardObj = cardToObj(card)
            if keyword in cardObj.get('title', ''):
                await send_to_discord(cardObj)
                count += 1
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

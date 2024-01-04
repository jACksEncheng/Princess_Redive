import os
import asyncio
import json
from bilibili_api import user
import aiohttp
from datetime import datetime, timezone, timedelta

# Discord Webhook URL
webhook_url = os.getenv('DISCORD_WEBHOOK_URL')  # 請將此處替換為您的 Discord Webhook URL

# Bilibili 用戶的 UID 列表
uids = [33383193, 3254764]  # 請將這些數字替換為實際的 UID

def getVideoItem(input, timestamp):
    item = {}
    if input.get("title"):
        item["title"] = input["title"]
    if aid := input.get("aid"):
        item["aid"] = aid
        item["url"] = f"https://www.bilibili.com/video/av{aid}"
    dt = datetime.fromtimestamp(timestamp, tz=timezone(timedelta(hours=8)))
    item["timestamp"] = dt.strftime('%Y-%m-%d %H:%M:%S')
    return item

def cardToObj(card_data):
    card = json.loads(card_data["card"]) if isinstance(card_data["card"], str) else card_data["card"]
    timestamp = card_data["desc"]["timestamp"]
    return getVideoItem(card, timestamp)

async def send_to_discord(cardObj):
    # 檢查所有必需的參數是否存在
    if cardObj and all(key in cardObj for key in ['title', 'url', 'timestamp']):
        async with aiohttp.ClientSession() as session:
            discord_message = {
                "content": f"Title: {cardObj['title']}\n"
                           f"URL: {cardObj['url']}\n"
                           f"Timestamp: {cardObj['timestamp']}"
            }
            response = await session.post(webhook_url, json=discord_message)
            if response.status == 200:
                print("Message sent successfully")
            else:
                print(f"Failed to send message: {response.status} {response.reason}")

async def fetch_dynamics(uid):
    user_obj = user.User(uid=uid)
    offset = 0
    max_posts = 3
    count = 0
    keyword = "公主连结"
    while True:
        res = await user_obj.get_dynamics(offset)
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

async def main():
    tasks = [fetch_dynamics(uid) for uid in uids]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

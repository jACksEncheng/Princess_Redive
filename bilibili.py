import os
import asyncio
import json
from bilibili_api import user
import aiohttp

# Discord Webhook URL
webhook_url = os.getenv('DISCORD_WEBHOOK_URL')  # 請將此處替換為您的 Discord Webhook URL

# Bilibili 用戶的 UID
uid = 33383193  # 請將此處替換為實際的 UID

u = user.User(uid=uid)

def getVideoItem(input):
    item = {}
    if input.get("title"):
        item["title"] = input["title"]
    if aid := input.get("aid"):
        item["aid"] = aid
        item["url"] = f"https://www.bilibili.com/video/av{aid}"
    return item

def cardToObj(input):
    if isinstance(input["card"], str):
        card = json.loads(input["card"])
    else:
        card = input["card"]
    return getVideoItem(card)

async def send_to_discord(cardObj):
    if cardObj:  # 只有當 cardObj 不是空字典時才發送
        async with aiohttp.ClientSession() as session:
            # 包裹消息內容
            discord_message = {
                "content": f"Title: {cardObj.get('title', 'No Title')}\n"
                           f"URL: {cardObj.get('url', 'No URL')}"
            }
            response = await session.post(webhook_url, json=discord_message)
            if response.status == 200:
                print("Message sent successfully")
            else:
                print(f"Failed to send message: {response.status} {response.reason}")

async def main():
    offset = 0
    while True:
        res = await u.get_dynamics(offset)
        if res["has_more"] != 1:
            break
        offset = res["next_offset"]
        for card in res["cards"]:
            cardObj = cardToObj(card)
            await send_to_discord(cardObj)
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

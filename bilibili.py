import os
import asyncio
import json
from bilibili_api import user
import aiohttp

# Discord Webhook URL
webhook_url = os.getenv('DISCORD_WEBHOOK_TEST')  # TEST是呱呱專案，URL是測試

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
    # 發送含有特定關鍵詞的前三筆資料
    # ----- 修改開始 -----
    max_posts = 3  # 最大發送數量
    count = 0  # 初始化計數器
    keyword = "公主连结"  # 指定的關鍵詞
    # ----- 修改結束 -----
    while True:
        res = await u.get_dynamics(offset)
        if res["has_more"] != 1 or count >= max_posts:
            break
        offset = res["next_offset"]
        for card in res["cards"]:
            cardObj = cardToObj(card)
            if count >= max_posts:
                break  # 如果已達到最大發送數量，則中斷迴圈
            if keyword in cardObj.get('title', ''):
                await send_to_discord(cardObj)
                count += 1  # 發送成功後計數器加1
        await asyncio.sleep(1)  # 等待1秒以避免被限速

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

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
    return {
        "title": input.get("title", ""),
        "desc": input.get("desc", ""),
        "aid": input.get("aid", "")
    }

def cardToObj(input):
    card = json.loads(input["card"])
    return getVideoItem(card)

async def send_to_discord(cardObj):
    async with aiohttp.ClientSession() as session:
        webhook_message = {
            "content": json.dumps(cardObj, ensure_ascii=False)
        }
        await session.post(webhook_url, json=webhook_message)

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

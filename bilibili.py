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

def copyKeys(src, keys):
    res = {}
    for k in keys:
        if k in src:
            res[k] = src[k]
    return res

def getItem(input):
    if "item" in input:
        return getItem(input["item"])
    if "videos" in input:
        return getVideoItem(input)
    else:
        return getNormal(input)

def getNormal(input):
    res = copyKeys(input, ['description', 'pictures', 'content'])
    if "pictures" in res:
        res["pictures"] = [pic["img_src"] for pic in res["pictures"]]
    return res

def getVideoItem(input):
    res = copyKeys(input, ['title', 'desc', 'dynamic', 'short_link', 'stat', 'tname'])
    res["av"] = input["aid"]
    res["pictures"] = [input["pic"]]
    return res

def cardToObj(input):
    res = {
        "dynamic_id": input["desc"]["dynamic_id"],
        "timestamp": input["desc"]["timestamp"],
        "type": input["desc"]["type"],
        "item": getItem(input["card"])
    }
    if "origin" in input["card"]:
        originObj = json.loads(input["card"]["origin"])
        res["origin"] = getItem(originObj)
        if "user" in originObj and "name" in originObj["user"]:
            res["origin_user"] = originObj["user"]["name"]
    return res

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

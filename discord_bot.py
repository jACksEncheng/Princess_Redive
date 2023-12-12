import os
import discord

# 這裡放你的機器人Token
TOKEN = os.getenv('DISCORD_TOKEN_BC4')

# 設定意圖
intents = discord.Intents.default()
intents.messages = True
intents.guild_messages = True
intents.message_content = True #確保機器人能接收消息內容

# 啟動客戶端，加入意圖
client = discord.Client(intents=intents)

# 關鍵字到討論串ID的映射
KEYWORD_THREAD_MAP = {
    'apple': 1016325726816960582,  # 討論串A的ID
    '煌靈': 1168932902877278210,  # 討論串B的ID
    # 可以繼續添加更多關鍵字和討論串ID
}

# 設定要監聽的頻道ID
source_channel_id = 823212390480085065  # 頻道A的ID

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    # 機器人啟動後，在監聽頻道發送一條訊息
    channel = client.get_channel(source_channel_id)
    # if channel:
    #     await channel.send("機器人已啟動並準備好監聽訊息！")
    # else:
    #     print(f"無法找到頻道 {source_channel_id}。")

    # 同時在所有目標討論串發送一條訊息
    # for thread_id in KEYWORD_THREAD_MAP.values():
    #     try:
    #         thread = await client.fetch_channel(thread_id)
    #         await thread.send("機器人已啟動並準備好監聽訊息！")
    #     except discord.NotFound:
    #         print(f"討論串 {thread_id} 未找到。")
    #     except discord.Forbidden:
    #         print(f"無權限發送訊息到討論串 {thread_id}。")

@client.event
async def on_message(message):
    try:
        # 檢查訊息是否為空
        if not message.content:
            print(f"Received an empty or non-text message in channel {message.channel.id}")
            return

        # 分別打印訊息的內容和頻道ID
        print(f"Received a message: {message.content}")
        print(f"Message channel ID: {message.channel.id}")

        # 確保機器人不會回復自己的訊息
        if message.author == client.user:
            return

        # 檢查是否是指定頻道的訊息
        if message.channel.id == source_channel_id:
            for keyword, thread_id in KEYWORD_THREAD_MAP.items():
                if keyword in message.content:
                    print(f"Keyword '{keyword}' found in message. Sending to thread {thread_id}.")
                    try:
                        # 獲取討論串
                        target_thread = await client.fetch_channel(thread_id)
                        # 發送訊息到目標討論串
                        await target_thread.send(message.content)
                        print("Message sent to thread successfully. Now deleting original message.")
                        # 刪除原始頻道中的訊息
                        await message.delete()
                        print("Original message deleted.")
                    except discord.NotFound:
                        print(f"討論串 {thread_id} 未找到。")
                    except discord.Forbidden:
                        print(f"無權限執行操作於討論串 {thread_id} 或原始頻道。")
                    break  # 找到匹配的關鍵字後就不再繼續檢查
    except Exception as e:
        # 如果在處理訊息時發生錯誤，打印錯誤訊息
        print(f"An error occurred: {e}")

# 運行機器人
client.run(TOKEN)

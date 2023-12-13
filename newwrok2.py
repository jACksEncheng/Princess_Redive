import os
import discord

# 這裡放你的機器人Token
TOKEN = os.getenv('DISCORD_TOKEN_BC4')

# 設定意圖
intents = discord.Intents.default()
intents.messages = True
intents.guild_messages = True
intents.message_content = True

# 啟動客戶端，加入意圖
client = discord.Client(intents=intents)

# 設定要監聽的頻道ID
source_channel_id = 997108672784236627  # 頻道A的ID

# 設定需要建立討論串的關鍵字列表
keywords_to_track = ['TAL', '煌靈', '終將']

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    try:
        if not message.content:
            print(f"Received an empty or non-text message in channel {message.channel.id}")
            return

        print(f"Received a message: {message.content}")
        print(f"Message channel ID: {message.channel.id}")

        if message.author == client.user:
            return

        if message.channel.id == source_channel_id:
            for keyword in keywords_to_track:
                if keyword in message.content:
                    print(f"Keyword '{keyword}' found in message. Creating a thread.")
                    try:
                        # 為該消息建立討論串
                        thread = await message.create_thread(name=f"Discussion on {keyword}")
                        print(f"Thread created successfully: {thread.id}")

                        # 刪除原始消息
                        await message.delete()
                        print("Original message deleted.")
                    except discord.HTTPException as e:
                        print(f"Failed to create a thread or delete message: {e}")
                    break
    except Exception as e:
        print(f"An error occurred: {e}")

# 運行機器人
client.run(TOKEN)

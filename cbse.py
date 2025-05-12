import requests
import hashlib
import os
import discord
import asyncio

URL = "https://results.cbse.nic.in/"
HASH_FILE = "last_hash.txt"

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = int(os.environ['DISCORD_CHANNEL_ID'])

def get_hash():
    content = requests.get(URL).text
    return hashlib.md5(content.encode()).hexdigest()

async def main():
    new_hash = get_hash()
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            old_hash = f.read().strip()
    else:
        old_hash = ""

    if new_hash != old_hash:
        client = discord.Client()

        @client.event
        async def on_ready():
            channel = client.get_channel(CHANNEL_ID)
            await channel.send("🔔 CBSE Results page has changed! https://results.cbse.nic.in/")
            await client.close()

        with open(HASH_FILE, "w") as f:
            f.write(new_hash)

        await client.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())

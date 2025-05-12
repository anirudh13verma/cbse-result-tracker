import requests
import hashlib
import os
import discord
import asyncio

URL = "https://results.cbse.nic.in/"
HASH_FILE = "last_hash.txt"

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = int(os.environ['DISCORD_CHANNEL_ID'])     # Main result alert channel
DEBUG_CHANNEL_ID = int(os.environ['DEBUG_ID'])         # Debug/heartbeat channel

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

    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        try:
            debug_channel = client.get_channel(DEBUG_CHANNEL_ID)
            await debug_channel.send("@everyone\n✅ Workflow ran successfully!")

            if new_hash != old_hash:
                result_channel = client.get_channel(CHANNEL_ID)
                await result_channel.send("@everyone\n🔔 CBSE Results page has changed! https://results.cbse.nic.in/\nNote: Backend changes in website may also be flagged and notified")

                with open(HASH_FILE, "w") as f:
                    f.write(new_hash)

        except Exception as e:
            debug_channel = client.get_channel(DEBUG_CHANNEL_ID)
            await debug_channel.send(f"❌ Error: {e}")

        await client.close()

    await client.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())

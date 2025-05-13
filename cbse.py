import os
import requests
from bs4 import BeautifulSoup
import discord
import asyncio

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
MAIN_CHANNEL_ID = int(os.environ['DISCORD_CHANNEL_ID'])
DEBUG_CHANNEL_ID = int(os.environ['DEBUG_ID'])

URL = "https://results.cbse.nic.in/"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def fetch_matching_lines(max_retries=3, delay=5):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": URL,
        "DNT": "1"
    }

    for attempt in range(1, max_retries + 1):
        try:
            print(f"🟡 Attempt {attempt}...")
            response = requests.get(URL, headers=headers)
            if "An error occurred while processing your request." in response.text:
                print("⚠️ Akamai edge block detected. Retrying...")
                if attempt == max_retries:
                    return ["⚠️ Akamai edge block detected."]
                await asyncio.sleep(delay)
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            lines = soup.prettify().splitlines()

            matching_lines = [
                line.strip()
                for line in lines
                if '2025' in line and 'xii' in line.lower() and ('result' in line.lower() or 'results' in line.lower())
            ]

            print(f"✅ Found {len(matching_lines)} matching line(s).")
            for line in matching_lines:
                print("📌", line)

            return matching_lines if matching_lines else ["NOPE"]

        except Exception as e:
            print(f"❌ Error on attempt {attempt}: {e}")
            await asyncio.sleep(delay)

    return ["❌ Failed to fetch site data after all retries."]

def load_last_snapshot():
    try:
        with open("last_hash.txt", "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "NEW"

def save_snapshot(snapshot_text):
    with open("last_hash.txt", "w", encoding="utf-8") as file:
        file.write(snapshot_text)

@client.event
async def on_ready():
    main_channel = client.get_channel(MAIN_CHANNEL_ID)
    debug_channel = client.get_channel(DEBUG_CHANNEL_ID)

    matching_lines = await fetch_matching_lines()
    current_snapshot = "\n".join(matching_lines)
    old_snapshot = load_last_snapshot()

    # Check if it's the first run (or last_hash.txt contains "NEW")
    if old_snapshot == "NEW":
        save_snapshot(current_snapshot)
        await debug_channel.send("@hmmmm8544\n🆕 First run. Snapshot saved but no alert sent.")
        await debug_channel.send("```\n" + current_snapshot + "\n```")
        await client.close()
        return

    if current_snapshot != old_snapshot:
        if current_snapshot != "NOPE":
            await main_channel.send(f"@everyone\n🔔 **CBSE website updated!** Possibly a new 2025 XII Result.\nCheck it out [CBSE]({URL})")
        await debug_channel.send("@hmmmm8544\n🔄 Snapshot changed.")
        await debug_channel.send("📂 Old:")
        await debug_channel.send("```\n" + old_snapshot + "\n```")
        await debug_channel.send("🆕 New:")
        await debug_channel.send("```\n" + current_snapshot + "\n```")
        save_snapshot(current_snapshot)
    else:
        await debug_channel.send("@hmmmm8544\n✅ No change detected.")
        await debug_channel.send("```\n" + current_snapshot + "\n```")

    await client.close()

asyncio.run(client.start(DISCORD_TOKEN))

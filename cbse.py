import os
import hashlib
import requests
from bs4 import BeautifulSoup
import discord
import asyncio

# Load environment variables
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
MAIN_CHANNEL_ID = int(os.environ['DISCORD_CHANNEL_ID'])
DEBUG_CHANNEL_ID = int(os.environ['DEBUG_ID'])

# Website URL
URL = "https://results.cbse.nic.in/"

# Discord client setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def fetch_site_hash(max_retries=3, delay=5):
    """Scrape the CBSE site and generate a hash of lines mentioning 2025 XII Result(s)."""
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
                    return None, ["⚠️ Akamai edge block detected."]
                await asyncio.sleep(delay)
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            full_text = soup.prettify()
            lines = full_text.splitlines()

            matching_lines = [
                line.strip()
                for line in lines
                if '2025' in line and 'xii' in line.lower() and ('result' in line.lower() or 'results' in line.lower())
            ]

            print(f"✅ Found {len(matching_lines)} matching line(s).")
            for line in matching_lines:
                print("📌", line)

            combined_text = ''.join(matching_lines)
            return hashlib.md5(combined_text.encode()).hexdigest(), matching_lines

        except Exception as e:
            print(f"❌ Error on attempt {attempt}: {e}")
            await asyncio.sleep(delay)

    return None, ["❌ Failed to fetch site data after all retries."]

def load_last_hash():
    """Load last saved hash from file."""
    try:
        with open("last_hash.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return ""

def save_hash(new_hash):
    """Save the current hash to file."""
    with open("last_hash.txt", "w") as file:
        file.write(new_hash)

@client.event
async def on_ready():
    main_channel = client.get_channel(MAIN_CHANNEL_ID)
    debug_channel = client.get_channel(DEBUG_CHANNEL_ID)

    new_hash, matching_lines = await fetch_site_hash()
    old_hash = load_last_hash()

    if new_hash is None:
        await debug_channel.send("@hmmmm8544\n❌ Error fetching site. Possibly Akamai blocked or other issue.")
        await debug_channel.send("```\n" + "\n".join(matching_lines) + "\n```")
        await client.close()
        return

    if not old_hash:  # Check for empty old_hash
        save_hash(new_hash)
        await debug_channel.send("@hmmmm8544\n🆕 First run detected. Hash saved but no alert sent.")
        await debug_channel.send("```\n" + "\n".join(matching_lines) + "\n```")
        await client.close()
        return

    if new_hash != old_hash:
        await main_channel.send(f"@everyone\n🔔 **CBSE website updated!** Possibly a new 2025 XII Result.\nCheck it out [CBSE]({URL})")
        await debug_channel.send(f"@hmmmm8544\n🔔 **CBSE website updated!**\nOld Hash: `{old_hash}`\nNew Hash: `{new_hash}`")
        await debug_channel.send("```\n" + "\n".join(matching_lines) + "\n```")
        save_hash(new_hash)
    else:
        await debug_channel.send("@hmmmm8544\n✅ Workflow ran successfully. No update detected.")
        await debug_channel.send(f"Old Hash: `{old_hash}`\nNew Hash: `{new_hash}`")
        await debug_channel.send("```\n" + "\n".join(matching_lines) + "\n```")

    await client.close()
    print("✅ Bot shut down cleanly.")
    

client.run(DISCORD_TOKEN)

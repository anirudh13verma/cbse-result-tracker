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

def fetch_site_hash():
    """Scrape the CBSE site and generate a hash of the relevant 2025 XII results entries."""
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all("a", href=True)

    filtered = [
        link['aria-label']
        for link in links
        if 'aria-label' in link.attrs and all(keyword in link['aria-label'] for keyword in ['2025', 'XII', 'Result'])
    ]

    combined_text = ''.join(filtered)
    return hashlib.md5(combined_text.encode()).hexdigest()

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

    new_hash = fetch_site_hash()
    old_hash = load_last_hash()

    if new_hash != old_hash:
        await main_channel.send(f"@everyone\n🔔 **CBSE website updated!** Possibly a new 2025 XII Result.\nCheck it out [CBSE]({URL})")
        await debug_channel.send(f"@hmmmm8544\n🔔 **CBSE website updated!**\nOld Hash: `{old_hash}`\nNew Hash: `{new_hash}`")       
        save_hash(new_hash)
    else:
        await debug_channel.send("@hmmmm8544\n✅ Workflow ran successfully. No update detected.")

    await client.close()

asyncio.run(client.start(DISCORD_TOKEN))
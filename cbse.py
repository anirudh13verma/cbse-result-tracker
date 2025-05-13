import os
import hashlib
import requests
import time
import discord
from discord.ext import tasks
from bs4 import BeautifulSoup

# URL to scrape
URL = "https://results.cbse.nic.in/"

# Discord token and channel IDs
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MAIN_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
DEBUG_CHANNEL_ID = int(os.getenv('DEBUG_ID'))

# Headers for scraping
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": URL,
    "DNT": "1",
}

# Discord client setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Function to fetch site content and generate MD5 hash
def fetch_site_hash():
    """Fetch website content and generate MD5 hash of matching lines."""
    for attempt in range(3):  # Retry mechanism
        try:
            response = requests.get(URL, headers=HEADERS)
            if "An error occurred while processing your request." in response.text:
                print("⚠️ Akamai edge block detected. Retrying...")
                time.sleep(5)
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            full_text = soup.prettify().lower()
            lines = full_text.splitlines()

            # Filter lines containing 2025, xii, and result
            matching_lines = [
                line for line in lines
                if '2025' in line and 'xii' in line and ('result' in line or 'results' in line)
            ]

            # Return the MD5 hash of the matching lines (empty list -> empty hash)
            combined_text = ''.join(matching_lines)
            return hashlib.md5(combined_text.encode()).hexdigest()

        except Exception as e:
            print(f"❌ Error on attempt {attempt + 1}: {e}")
            time.sleep(5)

    raise Exception("🚫 Failed to fetch valid site data after all retries.")

# Function to load the last saved hash
def load_last_hash():
    """Load the last saved hash from the file."""
    try:
        with open('last_hash.txt', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return ""  # No previous hash found

# Function to save the current hash to the file
def save_hash(new_hash):
    """Save the new hash to the last_hash.txt file."""
    with open('last_hash.txt', 'w') as file:
        file.write(new_hash)

# Function to handle the bot actions after checking the website
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    main_channel = client.get_channel(MAIN_CHANNEL_ID)
    debug_channel = client.get_channel(DEBUG_CHANNEL_ID)

    # Fetch the new hash of the website
    new_hash = fetch_site_hash()
    old_hash = load_last_hash()

    # Print the hashes in the CLI for debugging
    print(f"Old Hash: {old_hash}")
    print(f"New Hash: {new_hash}")

    # Check if the hash has changed
    if new_hash == old_hash:
        print("No change detected.")
        await debug_channel.send(f"No change detected.\nOld Hash: `{old_hash}`\nNew Hash: `{new_hash}`")
    elif new_hash != old_hash and new_hash != hashlib.md5("".encode()).hexdigest():
        print("Change detected: 2025 update.")
        await main_channel.send(f"@everyone\n🔔 **CBSE website updated!** Possibly a new 2025 XII Result.\nCheck it out [CBSE]({URL})")
        await debug_channel.send(f"Change detected: 2025 update.\nOld Hash: `{old_hash}`\nNew Hash: `{new_hash}`")
    elif new_hash != old_hash and new_hash == hashlib.md5("".encode()).hexdigest():
        print("New file or no relevant content.")
        await debug_channel.send(f"New file or no relevant content.\nOld Hash: `{old_hash}`\nNew Hash: `{new_hash}`")

    # Save the new hash to the file for future comparison
    save_hash(new_hash)

    # Close the bot
    await client.close()

# Run the bot
client.run(DISCORD_TOKEN)

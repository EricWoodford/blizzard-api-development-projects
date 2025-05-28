import discord
import requests
import asyncio

TOKEN = "YOUR_DISCORD_BOT_TOKEN"
WOW_API_URL = "https://worldofwarcraft.blizzard.com/en-us/game/status/us"  # Replace with actual WoW API URL

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def check_wow_status():
    await client.wait_until_ready()
    channel = client.get_channel(YOUR_CHANNEL_ID)  # Replace with your Discord channel ID

    while not client.is_closed():
        response = requests.get(WOW_API_URL)
        data = response.json()
        
        if data["server_status"] == "up":
            await channel.send("🔥 **World of Warcraft servers are back up!** 🔥")
        else:
            print("Servers are still down...")

        await asyncio.sleep(300)  # Check every 5 minutes

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    client.loop.create_task(check_wow_status())

client.run(TOKEN)
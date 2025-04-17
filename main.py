import discord
import asyncio
import os
from flask import Flask
from threading import Thread

# ====== Flask keep-alive server ======
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

# ====== Discord Bot Setup ======
intents = discord.Intents.default()
intents.message_content = True

# Load tokens from environment variables
BOT_TOKENS = [
    os.getenv("TOKEN1"),
    os.getenv("TOKEN2"),
    os.getenv("TOKEN3")
]

spamming = False
target_mention = None
bots = []

class BotClient(discord.Client):
    def __init__(self, token):
        super().__init__(intents=intents)
        self.token = token
        self.spam_task = None
        bots.append(self)

    async def on_ready(self):
        print(f'{self.user} is online!')

    async def on_message(self, message):
        global spamming, target_mention

        if message.author.bot:
            return

        content = message.content.strip()
        if content.startswith("!spam ") and message.mentions:
            target_mention = message.mentions[0].mention
            if not spamming:
                spamming = True
                print(f"Started spamming {target_mention}")
                for bot in bots:
                    bot.spam_task = asyncio.create_task(bot.spam_loop(message.channel))

        elif content == "!stop":
            if spamming:
                spamming = False
                print("Stopped spamming")
                for bot in bots:
                    if bot.spam_task:
                        bot.spam_task.cancel()
                        bot.spam_task = None

    async def spam_loop(self, channel):
        try:
            while spamming:
                await channel.send(f"{target_mention} {target_mention} {target_mention}")
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

# ====== Start All Bots ======
async def start_all():
    for token in BOT_TOKENS:
        if token:  # Ensure it's not None
            client = BotClient(token)
            asyncio.create_task(client.start(token))

async def main():
    await start_all()
    while True:
        await asyncio.sleep(3600)

asyncio.run(main())

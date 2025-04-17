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

# Get bot tokens from environment (secrets)
BOT_TOKENS = os.environ.get("BOT_TOKENS", "").split(",")

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
                self.spam_task = asyncio.create_task(self.spam_loop(message.channel))

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
for token in BOT_TOKENS:
    bot = BotClient(token)
    asyncio.create_task(bot.start(token))

# Needed to keep all bots running
asyncio.get_event_loop().run_forever()

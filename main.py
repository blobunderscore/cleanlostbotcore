import os
import discord
import asyncio
from discord.ext import commands
from flask import Flask
import threading

# === Flask Keep-Alive ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_flask).start()

# === Shared Global Spam State ===
spam_target = None
spamming = False

# === Bot Logic ===
intents = discord.Intents.default()
intents.message_content = True

class BotClient(commands.Bot):
    def __init__(self, token):
        super().__init__(command_prefix='!', intents=intents)
        self.token = token
        self.spam_task = None

        @self.event
        async def on_ready():
            print(f'{self.user} is online!')

        @self.event
        async def on_message(message):
            global spam_target, spamming

            if message.author.bot:
                return

            if message.content.startswith('!spam ') and message.mentions:
                spam_target = message.mentions[0]
                spamming = True

                # start spamming if not already
                if not self.spam_task or self.spam_task.done():
                    self.spam_task = asyncio.create_task(self.spam_loop(message.channel))

            elif message.content.strip() == '!stop':
                spamming = False

        async def spam_loop(self, channel):
            global spam_target, spamming
            while spamming:
                try:
                    await channel.send(f"{spam_target.mention} {spam_target.mention} {spam_target.mention}")
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"{self.user} failed to spam: {e}")
                    break

# === Load Tokens and Start All Bots ===
BOT_TOKENS = [os.getenv("TOKEN1"), os.getenv("TOKEN2"), os.getenv("TOKEN3")]

async def start_all():
    for token in BOT_TOKENS:
        if token:
            client = BotClient(token)
            asyncio.create_task(client.start(token))

async def main():
    await start_all()
    while True:
        await asyncio.sleep(3600)

asyncio.run(main())

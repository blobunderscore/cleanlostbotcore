import discord
import asyncio
import os
from flask import Flask
from threading import Thread

# Flask app for keeping the bot alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    thread = Thread(target=run_flask)
    thread.start()

# Load tokens (make sure these are set as environment variables in your hosting platform)
BOT_TOKENS = [
    os.getenv("TOKEN1"),
    os.getenv("TOKEN2"),
    os.getenv("TOKEN3"),
]

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

class BotClient(discord.Client):
    def __init__(self, token):
        super().__init__(intents=intents)
        self.token = token
        self.spamming = False
        self.spam_task = None
        self.mention_target = None

    async def on_ready(self):
        print(f"{self.user} is online!")

    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.strip()
        print(f"[{self.user}] Message received: {content}")

        if content.startswith("!спам") and not self.spamming:
            if message.mentions:
                self.mention_target = message.mentions[0].mention
                self.spamming = True
                self.spam_task = asyncio.create_task(self.spam_loop(message.channel))
                await message.channel.send(f"{self.user} started spamming {self.mention_target}!")
            else:
                await message.channel.send("Please mention someone like !spam @user")

        elif content == "!стоп" and self.spamming:
            self.spamming = False
            if self.spam_task:
                self.spam_task.cancel()
                self.spam_task = None
            await message.channel.send(f"{self.user} stopped spamming.")

    async def spam_loop(self, channel):
        try:
            while self.spamming:
                await channel.send(f"{self.mention_target} {self.mention_target} {self.mention_target}")
                await asyncio.sleep(1)  # 1 second to avoid rate limits
        except asyncio.CancelledError:
            pass

# Start Flask to keep the service alive
keep_alive()

# Instantiate all bots
bots = [BotClient(token) for token in BOT_TOKENS if token]

# Run all bots concurrently
async def run_all_bots():
    await asyncio.gather(*(bot.start(bot.token) for bot in bots))

# Run the bots
asyncio.run(run_all_bots())

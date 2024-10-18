import discord
import dotenv
import os

dotenv.load_dotenv()

class BibleBot(discord.Bot):
    async def on_ready(self):
        print(f'Logged in as {self.user.name} ({self.user.id})')

bot = BibleBot() # might need to add intents

cogs_list = [
    'utility',
]

for cogs in cogs_list:
    bot.load_extension(f'cogs.{cogs}')

bot.run(os.getenv('TOKEN'))
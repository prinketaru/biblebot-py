import discord
import dotenv
import os

dotenv.load_dotenv()

class BibleBot(discord.Bot):
    async def on_ready(self):
        print(f'Logged in as {self.user.name} ({self.user.id})')

bot = BibleBot(intents=discord.Intents.default())


cogs_list = [
    'utility',
    'bible',
]

for cogs in cogs_list:
    bot.load_extension(f'cogs.{cogs}')

bot.run(os.getenv('TOKEN'))
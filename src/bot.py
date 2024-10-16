import discord

class BibleBot(discord.Bot):
    async def on_ready(self):
        print(f'Logged in as {self.user.name} ({self.user.id})')
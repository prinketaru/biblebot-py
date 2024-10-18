import discord
from discord.ext import commands
import requests

bible_id = "de4e12af7f28f599-01"
verse_id = "PSA.23"

class Bible(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO: Fix python thinking JSON links are a string

    verse = discord.SlashCommandGroup("verse", "Commands related to Bible verses")

    @verse.command(description='Search for a Bible verse')
    @discord.option(name='verse', type=discord.SlashCommandOptionType.string, description="The verse to search for")
    async def search(self, ctx, verse: str):

        reference_response = requests.get(f'https://jsonbible.com//search/ref.php?keyword={verse}')
        reference_data = reference_response.json()

        # change refernce to reference_data and remove the [0] from the reference
        verse_response = requests.get(f'https://jsonbible.com/search/verses.php?json={ "book": "{reference_data['book']}", "bid": "{reference_data['bid']}", "chapter": "{reference_data['chapter']}", "chapter_roman": "{reference_data['chapter_roman']}", "verse": "{reference_data['verse']}", "found": {reference_data['found']}, "next_chapter": "{reference_data['next_chapter']}", "version": "esv" }')
        verse_data = verse_response.json()

        await ctx.send_response(f'{verse_data["verse"]}', ephemeral=True)

def setup(bot):
    bot.add_cog(Bible(bot))
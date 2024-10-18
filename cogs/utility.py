import discord
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description='Check the bot\'s latency')
    async def ping(self, ctx):
        await ctx.send_response(f'Pong! {round(self.bot.latency * 1000)}ms', ephemeral=True)
        
    @discord.slash_command(description='Make the bot say something')
    @discord.option("message", type=discord.SlashCommandOptionType.string)
    async def echo(self, ctx, message: str):
        await ctx.send_response(f'{message}')

def setup(bot):
    bot.add_cog(Utility(bot))
import discord
from discord.ext import commands

# Supported Bible versions
BIBLE_VERSIONS = [
    "KJV", "ESV", "NIV", "NLT", "NKJV", "NASB", "ASV", "AMP", "Darby"
]

class UsersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.collection = bot.db['users']

    @discord.slash_command(name="set-default-version", description="Set your default Bible version")
    @discord.option(
        name="version",
        description="The Bible version to set as your default",
        type=discord.SlashCommandOptionType.string,
        choices=BIBLE_VERSIONS
    )
    async def set_default_version(self, ctx, version: str):
        discord_id = ctx.author.id

        user_data = {
            "discord_id": discord_id,
            "default_version": version
        }

        self.collection.update_one(
            {"discord_id": discord_id},
            {"$set": user_data},
            upsert=True
        )

        await ctx.send_response(f"Your default Bible version has been set to ``{version}``.", ephemeral=True)

# Bot setup function
def setup(bot):
    bot.add_cog(UsersCog(bot))
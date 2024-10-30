import discord
from discord.ext import commands
import requests
import json
import globals

# Supported Bible versions
BIBLE_VERSIONS = ["KJV", "ESV", "NIV", "NLT", "NKJV", "NASB", "ASV"]


# Verse Commands Cog
class VerseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    verse_group = discord.SlashCommandGroup("verse", "Commands related to Bible verses")

    # /verse search command
    @verse_group.command(description="Find a Bible verse.")
    @discord.option(
        name="verse",
        type=discord.SlashCommandOptionType.string,
        description="The verse to search for",
    )
    @discord.option(
        name="version",
        type=discord.SlashCommandOptionType.string,
        description="The Bible version (Default: ESV)",
        default="ESV",
        choices=BIBLE_VERSIONS,
    )
    async def search(self, ctx, verse: str, version: str):
        await ctx.defer()

        # Step 1: Fetch verse reference
        reference_url = f"https://jsonbible.com/search/ref.php?keyword={verse}"
        reference_response = requests.get(reference_url)

        try:
            reference_data = reference_response.json()
        except json.decoder.JSONDecodeError:
            await ctx.send_followup(
                "The verse you requested does not exist. Please try again.",
                ephemeral=True,
            )
            return

        # Step 2: Build and send the verse request
        json_payload = {
            "book": reference_data["book"],
            "bid": reference_data["bid"],
            "chapter": reference_data["chapter"],
            "chapter_roman": reference_data["chapter_roman"],
            "verse": reference_data["verse"],
            "found": reference_data["found"],
            "next_chapter": reference_data["next_chapter"],
            "version": version.lower(),
        }

        verse_response_url = (
            f"https://jsonbible.com/search/verses.php?json={json.dumps(json_payload)}"
        )
        verse_response = requests.get(verse_response_url)

        try:
            verse_data = verse_response.json()
        except json.decoder.JSONDecodeError:
            await ctx.send_followup(
                "The verse you requested does not exist. Please try again.",
                ephemeral=True,
            )
            return

        # Step 3: Format and send the response
        await self.send_verse_embed(ctx, verse_data, version)

    async def send_verse_embed(self, ctx, verse_data: dict, version: str):
        """
        Helper function to send an embedded message with the verse data.
        """
        if "-" not in verse_data["verses"]:
            text = verse_data["text"]
            embed = self.create_embed(
                book=verse_data["book"],
                chapter=verse_data["chapter"],
                verse=verse_data["verses"],
                version=version,
                text=text,
            )
            await ctx.send_followup(embed=embed)
        else:
            start, stop = map(int, verse_data["verses"].split("-"))
            await self.send_verse_range(ctx, verse_data, version, start, stop)

    async def send_verse_range(
        self, ctx, verse_data: dict, version: str, start: int, stop: int
    ):
        """
        Helper function to handle and send a range of verses.
        """
        final_message = "> "
        if start == 1:
            final_message += self.format_bold_chapter(verse_data["chapter"])

        for verse_number in range(start, stop + 1):
            json_payload = {
                "book": verse_data["book"],
                "chapter": verse_data["chapter"],
                "verse": verse_number,
                "version": version.lower(),
            }
            verse_url = f"https://jsonbible.com/search/verses.php?json={json.dumps(json_payload)}"
            single_verse_response = requests.get(verse_url)
            single_verse_data = single_verse_response.json()

            formatted_verse = self.format_superscript(str(verse_number))
            book = verse_data["book"].replace(" ", "+")
            final_message += f"[{formatted_verse}](https://www.biblegateway.com/passage/?search={book}+{verse_data['chapter']}%3A{verse_number}&version={version}) {single_verse_data['text']} "

        if len(final_message) > 4096:
            await ctx.send_followup(
                "The passage is too long to send. Try a shorter verse."
            )
            return

        embed = discord.Embed(description=final_message)
        book = (verse_data["book"].replace(" ", "+"),)
        print(book)
        embed.set_author(
            name=f"{verse_data['book']} {verse_data['chapter']}:{start}-{stop} | {version}",
            url=f"https://www.biblegateway.com/passage/?search={book}+{verse_data['chapter']}%3A{start}-{stop}&version={version}",
        )
        await ctx.send_followup(embed=embed)

    @staticmethod
    def format_superscript(verse: str) -> str:
        """
        Converts digits in the verse number to superscript.
        """
        return verse.translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))

    @staticmethod
    def format_bold_chapter(chapter: str) -> str:
        """
        Formats chapter numbers in bold.
        """
        return chapter.translate(
            str.maketrans("0123456789", "０１２３４５６７８９")
        ).replace("0", "**０**")

    def create_embed(
        self, book: str, chapter: str, verse: str, version: str, text: str
    ) -> discord.Embed:
        """
        Helper function to create a Discord embed for a Bible verse.
        """
        formatted_verse = self.format_superscript(verse)
        book = book.replace(" ", "+")
        verse_url = f"https://www.biblegateway.com/passage/?search={book}+{chapter}%3A{verse}&version={version}"
        embed = discord.Embed(description=f"> [{formatted_verse}]({verse_url}) {text}")
        embed.set_author(name=f"{book} {chapter}:{verse} | {version}", url=verse_url)
        return embed

    # /verse daily command
    @verse_group.command(description="Get the verse of the day.")
    @discord.option(
        name="version",
        type=discord.SlashCommandOptionType.string,
        description="Bible version for daily verse (Default: ESV)",
        default="ESV",
        choices=BIBLE_VERSIONS,
    )
    async def daily(self, ctx, version: str):
        await ctx.defer()

        daily_verse = f"{globals.daily_verse['book']} {globals.daily_verse['chapter']}:{globals.daily_verse['verse']}"
        reference_url = f"https://jsonbible.com/search/ref.php?keyword={daily_verse}"
        reference_data = requests.get(reference_url).json()

        json_payload = {
            "book": reference_data["book"],
            "bid": reference_data["bid"],
            "chapter": reference_data["chapter"],
            "chapter_roman": reference_data["chapter_roman"],
            "verse": reference_data["verse"],
            "found": reference_data["found"],
            "next_chapter": reference_data["next_chapter"],
            "version": version.lower(),
        }

        verse_url = (
            f"https://jsonbible.com/search/verses.php?json={json.dumps(json_payload)}"
        )
        verse_data = requests.get(verse_url).json()

        await self.send_verse_embed(ctx, verse_data, version)


# Bot setup function
def setup(bot):
    bot.add_cog(VerseCommands(bot))

import discord
from discord.ext import commands
import requests
import json
import globals

versions = [
    "KJV",
    "ESV",
    "NIV",
    "NLT",
    "NKJV",
    "NASB",
    "ASV",
]


# biblegateway button for verses
class BGButton(discord.ui.Button):
    def __init__(self, book: str, chapter: str, verse: str, version: str):
        super().__init__(
            label="BibleGateway",
            style=discord.ButtonStyle.link,
            url=f"https://www.biblegateway.com/passage/?search={book}+{chapter}%3A{verse}&version={version}",
        )


# verse cog
class VerseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    verse = discord.SlashCommandGroup("verse", "Commands related to Bible verses")

    # /verse search command
    @verse.command(description="Find a Bible verse.")
    @discord.option(
        name="verse",
        type=discord.SlashCommandOptionType.string,
        description="The verse to search for",
    )
    @discord.option(
        name="version",
        type=discord.SlashCommandOptionType.string,
        description="The version of the Bible to search in (Default: ESV).",
        default="ESV",
        choices=versions,
    )
    async def search(self, ctx, verse: str, version: str):
        await ctx.defer()

        reference_response = requests.get(
            f"https://jsonbible.com//search/ref.php?keyword={verse}"
        )
        try:
            reference_data = reference_response.json()
        except json.decoder.JSONDecodeError:
            await ctx.send_followup(
                "The verse you requested does not exist. Please try again.",
                ephemeral=True,
            )
            return

        # Build the JSON payload as a dictionary
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

        # Convert the dictionary to a JSON string
        json_string = json.dumps(json_payload)

        # Make the request using the JSON string
        verse_response = requests.get(
            f"https://jsonbible.com/search/verses.php?json={json_string}"
        )
        try:
            verse_data = verse_response.json()
        except json.decoder.JSONDecodeError:
            await ctx.send_followup(
                "The verse you requested does not exist. Please try again.",
                ephemeral=True,
            )
            return

        # handle case where there is only one verse requested
        if "-" not in verse_data["verses"]:
            verse_as_superscript = (
                verse_data["verses"]
                .replace("1", "¹")
                .replace("2", "²")
                .replace("3", "³")
                .replace("4", "⁴")
                .replace("5", "⁵")
                .replace("6", "⁶")
                .replace("7", "⁷")
                .replace("8", "⁸")
                .replace("9", "⁹")
                .replace("0", "⁰")
            )
            if verse_data["verses"] == "1":
                chapter_as_bold = (
                    verse_data["chapter"]
                    .replace("0", "**０**")
                    .replace("1", "**１**")
                    .replace("2", "**２**")
                    .replace("3", "**３**")
                    .replace("4", "**４**")
                    .replace("5", "**５**")
                    .replace("6", "**６**")
                    .replace("7", "**７**")
                    .replace("8", "**８**")
                    .replace("9", "**９**")
                )
                final_message = (
                    f"> {chapter_as_bold} [{verse_as_superscript}](https://www.biblegateway.com/passage/?search={verse_data['book']}+{verse_data['chapter']}%3A{verse_data['verses']}&version={version}){verse_data['text']}"
                )
            else:
                final_message = f"> [{verse_as_superscript}](https://www.biblegateway.com/passage/?search={verse_data['book']}+{verse_data['chapter']}%3A{verse_data['verses']}&version={version}){verse_data['text']}"

            embed = discord.Embed(
                description=final_message,
            )
            embed.set_author(
                name=f'{verse_data["book"]} {verse_data["chapter"]}:{
                         verse_data["verses"]} | {verse_data["version"]}',
                url=f"https://www.biblegateway.com/passage/?search={verse_data['book']}+{verse_data['chapter']}%3A{verse_data['verses']}&version={version}",
            )

            await ctx.send_followup(embed=embed)

            return

        # Get a range of verses
        start, stop = map(int, verse_data["verses"].split("-"))

        # replace the chapter number with stylized text
        if start == 1:
            chapter_as_bold = (
                verse_data["chapter"]
                .replace("0", "**０**")
                .replace("1", "**１**")
                .replace("2", "**２**")
                .replace("3", "**３**")
                .replace("4", "**４**")
                .replace("5", "**５**")
                .replace("6", "**６**")
                .replace("7", "**７**")
                .replace("8", "**８**")
                .replace("9", "**９**")
            )
            final_message = f"> {chapter_as_bold} "
        else:
            final_message = f"> "

        # Loop through the range of verses and add them to the final message
        for i in range(start, stop + 1):
            json_payload = {
                "book": reference_data["book"],
                "bid": reference_data["bid"],
                "chapter": reference_data["chapter"],
                "chapter_roman": reference_data["chapter_roman"],
                "verse": i,
                "found": reference_data["found"],
                "next_chapter": reference_data["next_chapter"],
                "version": version,
            }

            json_string = json.dumps(json_payload)

            single_verse_response = requests.get(
                f"https://jsonbible.com/search/verses.php?json={json_string}"
            )
            try:
                single_verse_data = single_verse_response.json()
            except json.decoder.JSONDecodeError:
                await ctx.send_followup(
                    "The verse you requested does not exist. Please try again.",
                    ephemeral=True,
                )
                return

            # Handle the case where the verse data is invalid
            if verse_data.get("Verse") is None or verse_data["verses"] == "1-0":
                await ctx.send_followup("The verse you requested does not exist.")
                return

            # stylize verse and add to final message
            verse_as_superscript = (
                str(i)
                .replace("1", "¹")
                .replace("2", "²")
                .replace("3", "³")
                .replace("4", "⁴")
                .replace("5", "⁵")
                .replace("6", "⁶")
                .replace("7", "⁷")
                .replace("8", "⁸")
                .replace("9", "⁹")
                .replace("0", "⁰")
            )
            final_message += (
                f'[{verse_as_superscript}](https://www.biblegateway.com/passage/?search={verse_data["book"]}%20{verse_data["chapter"]}%3A{i}&version={version})'
                + single_verse_data["text"]
                + " "
            )

        if len(final_message) > 4096:
            await ctx.send_followup(
                "The passage is too long to send in one message. Please try a shorter verse."
            )
            return

        embed = discord.Embed(
            description=final_message,
        )
        embed.set_author(
            name=f'{verse_data["book"]} {verse_data["chapter"]}:{
                         verse_data["verses"]} | {verse_data["version"]}',
            url=f"https://www.biblegateway.com/passage/?search={verse_data['book']}+{verse_data['chapter']}%3A{verse_data['verses']}&version={version}",
        )

        await ctx.send_followup(embed=embed)

    # end verse search command

    # /verse daily command
    @verse.command(description="Get the verse of the day.")
    @discord.option(
        name="version",
        type=discord.SlashCommandOptionType.string,
        description="The version of the Bible to get the daily verse in (Default: ESV).",
        default="ESV",
        choices=versions,
    )
    async def daily(self, ctx, version: str):
        await ctx.defer()

        verse = (
            globals.daily_verse.get("book")
            + " "
            + globals.daily_verse.get("chapter")
            + ":"
            + globals.daily_verse.get("verse")
        )

        reference_response = requests.get(
            f"https://jsonbible.com//search/ref.php?keyword={verse}"
        )
        reference_data = reference_response.json()

        json_payload = {
            "book": reference_data["book"],
            "bid": reference_data["bid"],
            "chapter": reference_data["chapter"],
            "verse": reference_data["verse"],
            "chapter_roman": reference_data["chapter_roman"],
            "found": reference_data["found"],
            "next_chapter": reference_data["next_chapter"],
            "version": version.lower(),
        }

        json_string = json.dumps(json_payload)
        verse_response = requests.get(
            f"https://jsonbible.com/search/verses.php?json={json_string}"
        )
        verse_data = verse_response.json()

        # handle case where only one verse is requested
        if "-" not in verse_data["verses"]:
            verse_as_superscript = (
                verse_data["verses"]
                .replace("1", "¹")
                .replace("2", "²")
                .replace("3", "³")
                .replace("4", "⁴")
                .replace("5", "⁵")
                .replace("6", "⁶")
                .replace("7", "⁷")
                .replace("8", "⁸")
                .replace("9", "⁹")
                .replace("0", "⁰")
            )
            if verse_data["verses"] == 1:
                chapter_as_bold = (
                    verse_data["chapter"]
                    .replace("0", "**０**")
                    .replace("1", "**１**")
                    .replace("2", "**２**")
                    .replace("3", "**３**")
                    .replace("4", "**４**")
                    .replace("5", "**５**")
                    .replace("6", "**６**")
                    .replace("7", "**７**")
                    .replace("8", "**８**")
                    .replace("9", "**９**")
                )
                final_message = (
                    f"> {chapter_as_bold} [{verse_as_superscript}](https://www.biblegateway.com/passage/?search={verse_data['book']}+{verse_data['chapter']}%3A{verse_data['verses']}&version={version}){verse_data['text']}"
                )
            else:
                final_message = f"> [{verse_as_superscript}](https://www.biblegateway.com/passage/?search={verse_data['book']}+{verse_data['chapter']}%3A{verse_data['verses']}&version={version}){verse_data['text']}"

            embed = discord.Embed(
                description=final_message,
            )
            embed.set_author(
                name=f'{verse_data["book"]} {verse_data["chapter"]}:{
                         verse_data["verses"]} | {verse_data["version"]}',
                url=f"https://www.biblegateway.com/passage/?search={verse_data['book']}+{verse_data['chapter']}%3A{verse_data['verses']}&version={version}",
            )

            await ctx.send_followup(embed=embed)

            return

        # Get a range of verses
        start, stop = map(int, verse_data["verses"].split("-"))

        # replace the chapter number with stylized text
        if start == 1:
            chapter_as_bold = (
                verse_data["chapter"]
                .replace("0", "**０**")
                .replace("1", "**１**")
                .replace("2", "**２**")
                .replace("3", "**３**")
                .replace("4", "**４**")
                .replace("5", "**５**")
                .replace("6", "**６**")
                .replace("7", "**７**")
                .replace("8", "**８**")
                .replace("9", "**９**")
            )
            final_message = f"> {chapter_as_bold} "
        else:
            final_message = f"> "

        # Loop through the range of verses and add them to the final message
        for i in range(start, stop + 1):
            json_payload = {
                "book": reference_data["book"],
                "bid": reference_data["bid"],
                "chapter": reference_data["chapter"],
                "chapter_roman": reference_data["chapter_roman"],
                "verse": i,
                "found": reference_data["found"],
                "next_chapter": reference_data["next_chapter"],
                "version": version,
            }

            json_string = json.dumps(json_payload)

            single_verse_response = requests.get(
                f"https://jsonbible.com/search/verses.php?json={json_string}"
            )
            single_verse_data = single_verse_response.json()

            # get i as a superscript
            verse_as_superscript = (
                str(i)
                .replace("1", "¹")
                .replace("2", "²")
                .replace("3", "³")
                .replace("4", "⁴")
                .replace("5", "⁵")
                .replace("6", "⁶")
                .replace("7", "⁷")
                .replace("8", "⁸")
                .replace("9", "⁹")
                .replace("0", "⁰")
            )

            final_message += (
                f'[{verse_as_superscript}](https://www.biblegateway.com/passage/?search={verse_data["book"]}%20{verse_data["chapter"]}%3A{i}&version={version})'
                + single_verse_data["text"]
                + " "
            )

        embed = discord.Embed(
            description=final_message,
        )
        embed.set_author(
            name=f'{verse_data["book"]} {verse_data["chapter"]}:{
                         verse_data["verses"]} | {verse_data["version"]}',
            url=f"https://www.biblegateway.com/passage/?search={verse_data['book']}+{verse_data['chapter']}%3A{verse_data['verses']}&version={version}",
        )

        await ctx.send_followup(embed=embed)


def setup(bot):
    bot.add_cog(VerseCommands(bot))

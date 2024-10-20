from datetime import time, timezone
import discord
from discord.ext import tasks
import dotenv
import os
import random
import globals
import json

dotenv.load_dotenv()


# create a new class that inherits from discord.Bot
class BibleBot(discord.Bot):
    async def on_ready(self):
        print(f"Logged in as {self.user.name} ({self.user.id})")
        await get_daily_verse()
        daily_verse_loop.start()


# create an instance of the BibleBot class
bot = BibleBot(
    intents=discord.Intents.default(),
    default_command_integration_types={
        discord.IntegrationType.user_install,
        discord.IntegrationType.guild_install,
    },
)

# get daily verse everyday at 0:00 UTC
with open("daily_verses.json") as f:
    verses = json.load(f)

LAST_VERSE_FILE = "last_verse.json"


# get a random verse
def get_random_verse(exclude=None):
    verse = random.choice(verses)

    while verse == exclude:
        verse = random.choice(verses)

    return verse


# save the last verse to a file
def save_last_verse(verse):
    with open(LAST_VERSE_FILE, "w") as f:
        json.dump(verse, f)


def load_last_verse():
    try:
        with open(LAST_VERSE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


async def get_daily_verse():
    last_verse = load_last_verse()
    new_verse = get_random_verse(exclude=last_verse)

    save_last_verse(new_verse)

    globals.daily_verse = new_verse

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=f'{new_verse["book"]} {new_verse["chapter"]}:{new_verse["verse"]}',
        )
    )


@tasks.loop(time=time(0, 0, tzinfo=timezone.utc))
async def daily_verse_loop():
    await get_daily_verse()


# load cogs
cogs_list = [
    "utility",
    "verses",
]

for cogs in cogs_list:
    bot.load_extension(f"cogs.{cogs}")

# run the bot
bot.run(os.getenv("TOKEN"))

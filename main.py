from src import BibleBot

bot = BibleBot()

bot.load_extension('src.cogs.utilty')

bot.run("TOKEN")
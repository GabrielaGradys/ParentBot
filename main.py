import os

import discord
from dotenv import load_dotenv

from math_daily import MathChecker

load_dotenv()

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.typing = False
    intents.presences = False

    math_bot = MathChecker(command_prefix='!', intents=intents)
    math_bot.run(os.getenv('TOKEN'))

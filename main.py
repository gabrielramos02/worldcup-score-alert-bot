import telegrampy
from telegrampy.ext import commands

import logging

from api_request import get_teams_list
from config import BOT_TOKEN

logging.basicConfig(
    level=logging.INFO,
    format="(%(asctime)s) %(levelname)s %(message)s",
    datefmt="%m/%d/%y - %H:%M:%S %Z",
)
logger = logging.getLogger("telegrampy")


def main():
    bot = commands.Bot(str(BOT_TOKEN))

    @bot.command()
    async def hi(ctx: commands.Context):
        await ctx.send("Hello")

    @bot.command()
    async def list(ctx: commands.Context):
        response = await get_teams_list()
        if not response:
            await ctx.send("No teams found.")
            return
        name_list = [team.get("displayName", "Unknown") for team in response]
        # TODO: add option to get info by id, and add more info to the list
        mensaje_final = "\n".join(f"• {name}" for name in name_list)

        await ctx.send(f"Teams:\n{mensaje_final}")

    ## TODO: add comand to get team info by id

    bot.run()


if __name__ == "__main__":
    main()

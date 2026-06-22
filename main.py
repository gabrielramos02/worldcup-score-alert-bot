from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

import logging

from api_request import get_from_url, get_team_info, get_teams_list
from config import BOT_TOKEN
from database.manager import test_database

logging.basicConfig(
    level=logging.INFO,
    format="(%(asctime)s) %(levelname)s %(message)s",
    datefmt="%m/%d/%y - %H:%M:%S %Z",
)


async def list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = await get_teams_list()
    if not response:
        if update.effective_chat:
            _ = await context.bot.sendMessage(
                chat_id=update.effective_chat.id, text="No teams found."
            )
        return
    # TODO: add option to get info by id, and add more info to the list
    mensaje_final = "\n".join(
        f"• {team["displayName"]} /i_{team["id"]}" for team in response
    )

    if update.effective_chat:
        _ = await context.bot.sendMessage(
            chat_id=update.effective_chat.id, text=f"Teams:\n{mensaje_final}"
        )

    ## TODO: add comand to get team info by id
async def team_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        team_id = update.message.text.split("_")[1]
        response = await get_team_info(team_id)
        print(response)
        mensaje_final = f"Team Info:\nName: {response["displayName"]}\n"
        if update.effective_chat:
            _ = await context.bot.sendMessage(chat_id=update.effective_chat.id, text=mensaje_final)




if __name__ == "__main__":
    application = ApplicationBuilder().token(str(BOT_TOKEN)).build()

    #start_handler = CommandHandler("start", start)
    list_handler = CommandHandler("list", list)
    team_info_handler = MessageHandler(filters.Regex(r"^/i_\d+$"), team_info)

    #application.add_handler(start_handler)
    application.add_handler(list_handler)
    application.add_handler(team_info_handler)

    application.run_polling()

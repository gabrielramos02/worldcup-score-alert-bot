from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import logging

from src.api_request import get_from_url, get_team_info, get_teams_list
from src.config import BOT_TOKEN
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
    # TODO:  add more info to the list
    mensaje_final = "\n".join(
        f"• {team["displayName"]} /i_{team["id"]}" for team in response
    )

    if update.message:
        _ = await update.message.reply_text(mensaje_final)

async def team_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        team_id = update.message.text.split("_")[1]
        response = await get_team_info(team_id)
        mensaje_final = f"Team Info:\nName: {response["displayName"]}\n"
        keyboard = [[InlineKeyboardButton("Suscribe", callback_data=f"sub{team_id}")]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            _ = await update.message.reply_text(mensaje_final, reply_markup=reply_markup)

async def sub_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query and query.data:
        team_id = query.data[3:]  
        # TODO: Add logic to subscribe the user to the team using the team_id
        _ = await query.answer()  
        _ = await query.edit_message_text(text=f"You have subscribed to team {team_id}.")


if __name__ == "__main__":
    application = ApplicationBuilder().token(str(BOT_TOKEN)).build()

    # start_handler = CommandHandler("start", start)
    list_handler = CommandHandler("list", list)
    team_info_handler = MessageHandler(filters.Regex(r"^/i_\d+$"), team_info)

    # application.add_handler(start_handler)
    application.add_handler(list_handler)
    application.add_handler(team_info_handler)
    application.add_handler(CallbackQueryHandler(sub_button))

    application.run_polling()

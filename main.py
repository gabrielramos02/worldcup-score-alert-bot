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
from database.manager import (
    get_subscription_for_team,
    remove_subscription,
    add_subscription,
)

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
    mensaje_final = "\n".join(f"• {team.team_name} /i_{team.id}" for team in response)

    if update.message:
        _ = await update.message.reply_text(mensaje_final)


async def team_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        team_id = update.message.text.split("_")[1]
        response = await get_team_info(team_id)
        if response is None:
            if update.message:
                _ = await update.message.reply_text("Team not found.")
            return
        display_name = response.team_name
        mensaje_final = f"Team Info:\nName: {display_name}\n"
        suscribed = await get_subscription_for_team(
            chat_id=str(update.message.chat.id), team_id=int(team_id)
        )
        sub_icon = suscribed and "✅" or "❌"
        callback_data = suscribed and f"unsub{team_id}" or f"sub{team_id}"
        keyboard = [
            [InlineKeyboardButton(f"Suscribed {sub_icon}", callback_data=callback_data)]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.message:
            _ = await update.message.reply_text(
                mensaje_final, reply_markup=reply_markup
            )


async def sub_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query and query.data:
        if query.data.startswith("sub"):
            team_id = query.data[3:]
            if query.message and query.message.chat:
                await add_subscription(
                    chat_id=str(query.message.chat.id),
                    team_id=int(team_id),
                )
            sub_icon = "✅"
            keyboard = [
                [
                    InlineKeyboardButton(
                        f"Suscribed {sub_icon}", callback_data=f"unsub{team_id}"
                    )
                ]
            ]

            if query.message.text:
                old_text = query.message.text
            else:
                old_text = "Team Info"
            _ = await query.answer(text="Subscription added!", show_alert=True)
            _ = await query.edit_message_text(
                text=old_text, reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            team_id = query.data[5:]
            if query.message and query.message.chat:
                await remove_subscription(
                    chat_id=str(query.message.chat.id),
                    team_id=int(team_id),
                )
            sub_icon = "❌"
            keyboard = [
                [
                    InlineKeyboardButton(
                        f"Suscribed {sub_icon}", callback_data=f"sub{team_id}"
                    )
                ]
            ]

            if query.message.text:
                old_text = query.message.text
            else:
                old_text = "Team Info"
            _ = await query.answer(text="Subscription removed!", show_alert=True)
            _ = await query.edit_message_text(
                text=old_text, reply_markup=InlineKeyboardMarkup(keyboard)
            )


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

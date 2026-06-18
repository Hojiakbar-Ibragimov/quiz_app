from time import sleep
from telegram import InlineKeyboardMarkup, ReplyKeyboardMarkup

from quiz_app.Application.api.game import (check_answer_flow, help_buttons, request_help_50_50,
                                           request_help_change_quest, answers_inline_buttons)

from quiz_app.service.game_service import get_current_question
from quiz_app.service.user_service import register_user
from quiz_app.service.profile_service import update_user_lang
from quiz_app.service.question_service import get_answers_id

from quiz_app.Application.api.handlers.commands import main_keyboards

from quiz_app.locales.messages import msg
from quiz_app.logger import logger

def start_language_query_handler(query, data, user):

    if data == "en" or data == "uz":
        lang = data
        query.message.delete()

        register_user(user.id, user.first_name, user.username, lang)

        keyboards = main_keyboards(lang)

        query.message.reply_text(text=f"{msg(lang, 'welcome')}", reply_markup=ReplyKeyboardMarkup(keyboards,
                                         resize_keyboard=True))

def change_language_query_handler(query, data, user):

    if data == "en" or data == "uz":
        try:
            lang = data

            update_user_lang(user, lang)

            query.message.delete()

            keyboards = main_keyboards(lang)

            query.message.reply_text(text=f"{msg(lang, 'lang_changed')} ✅", reply_markup=ReplyKeyboardMarkup(keyboards,
                                                                                                             resize_keyboard=True))
        except ValueError as w:
            warn = str(w)
            mssg = query.message.reply_text(text=warn)
            sleep(2)
            mssg.delete()

    elif data == "cancel":
        query.message.delete()

def game_query_handler(query, data, user, context):

    if str(data).isdigit():
        answer = data
        check_answer_flow(query, answer, user, context)

    elif data == "help":
        buttons = help_buttons(user, context)
        query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "help_50_50":
        try:
            request_help_50_50(query, user, context)

        except ValueError as w:
            warning = str(w)
            mssg = query.message.reply_text(text=warning)
            logger.warning(f"User {user.id} ({user.first_name}) tried to reuse help 50/50")
            sleep(1)
            mssg.delete()

    elif data == "change_quest":
        try:
            request_help_change_quest(query, user, context)

        except ValueError as w:
            warning = str(w)
            mssg = query.message.reply_text(text=warning)
            logger.warning(f"User {user.id} ({user.first_name}) tried to reuse help to change quest")
            sleep(1)
            mssg.delete()

    elif data == "back_to_question":
        session_id = context.user_data["session_id"]
        question_id = get_current_question(session_id)
        answers_id = get_answers_id(question_id)
        answer_buttons = answers_inline_buttons(answers_id, user, context)

        query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(answer_buttons))

    elif data == "close":
        query.message.delete()
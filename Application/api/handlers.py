from time import sleep

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from api_game import (start_game, check_answer_flow, request_help_change_quest,
                      request_help_50_50, help_buttons)
from quiz_app.Application.api.api_game import answers_inline_buttons
from quiz_app.service.game_service import get_current_question
from quiz_app.service.question_service import get_answers_id
from quiz_app.service.user_service import (get_user_by_id, register_user,
                                           get_one_user_active, is_admin,
                                           greet)
from quiz_app.service.profile_service import (get_rating, get_user_lang,
                                              update_user_lang, get_user_profile)
from admin_panel import admin_start_command, admin_keyboard_handler, admin_query_router
from quiz_app.locales.messages import msg
from quiz_app.logger import logger

def users_start_command(update, context):
    user_id = update.effective_user.id
    real_name = update.effective_user.first_name


    user = get_user_by_id(user_id)

    if user:
        lang = get_user_lang(user_id)
        keyboards = main_keyboards(lang)

        update.message.reply_text(text=f"{greet(lang)}, {real_name}", reply_markup=ReplyKeyboardMarkup(keyboards,
                                                                                                   resize_keyboard=True))
        return

    update.message.reply_text(text=f"{greet('en')}, {real_name}")
    update.message.reply_text(text="Which language?",
                                  reply_markup=InlineKeyboardMarkup(language_buttons("start_language", "en")))

def language_buttons(prefix, lang):
    buttons = [
        [InlineKeyboardButton(text=f"{msg(lang, 'english')}", callback_data=f"{prefix}:en"),
         InlineKeyboardButton(text=f"{msg(lang, 'uzbek')}", callback_data=f"{prefix}:uz")]
    ]
    return buttons

def users_keyboard_handler(update, context):
    data = update.message.text
    user = update.effective_user
    lang = get_user_lang(user.id)

    status = get_one_user_active(user.id)[0]
    active_status = bool(status)

    if data == f"🎮 {msg(lang, 'start_game')}":
        if active_status:
            start_game(update, user, context)

            update.message.delete()

        else:
            update.message.delete()
            mssg = update.message.reply_text(text=f"🔴 {msg(lang, 'you_inactive')}!")
            sleep(3)
            mssg.delete()

    elif data == f"🏆 {msg(lang, 'rating')}":
        close_button = [[InlineKeyboardButton(text=f"{msg(lang, 'close')}", callback_data="game:close")]]
        update.message.reply_text(text=get_rating(user.id), reply_markup=InlineKeyboardMarkup(close_button))
        update.message.delete()

    elif data == f"👤 {msg(lang, 'profile')}":
        close_button = [[InlineKeyboardButton(text=f"{msg(lang, 'close')}", callback_data="game:close")]]
        update.message.reply_text(text=get_user_profile(user.id), reply_markup=InlineKeyboardMarkup(close_button))
        update.message.delete()

    else:
        update.message.delete()

def users_query_router(update, context):
    query = update.callback_query
    user = update.effective_user

    parts = query.data.split(":")

    prefix = parts[0]
    data = parts[1]

    if prefix == "game":
        game_query_handler(query, data, user, context)
        return

    elif prefix == "start_language":
        start_language_query_handler(query, data, user)

    elif prefix == "change_language":
        change_language_query_handler(query, data, user)


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

def change_lang_command_handler(update, context):
    user = update.effective_user
    lang = get_user_lang(user.id)

    buttons = language_buttons("change_language", lang)

    cancel_button = [InlineKeyboardButton(text=f"{msg(lang, 'cancel')}", callback_data="change_language:cancel")]
    buttons.append(cancel_button)

    update.message.reply_text(text=f"{msg(lang, 'which_lang')}?", reply_markup=InlineKeyboardMarkup(buttons))
    update.message.delete()

def main_keyboards(lang):
    keyboards = [
        [KeyboardButton(text=f"🎮 {msg(lang, 'start_game')}"),
         KeyboardButton(text=f"🏆 {msg(lang, 'rating')}")],
        [KeyboardButton(text=f"👤 {msg(lang, 'profile')}")]
    ]
    return keyboards

def start_router(update, context):
    user = update.effective_user

    if is_admin(user.id):
        admin_start_command(update, context)
        return

    users_start_command(update, context)
    return

def keyboard_router(update, context):
    user = update.effective_user

    if is_admin(user.id):
        admin_keyboard_handler(update, context)
        return

    users_keyboard_handler(update, context)
    return

def query_router(update, context):
    user = update.effective_user

    if is_admin(user.id):
        admin_query_router(update, context)
        return

    users_query_router(update, context)
    return
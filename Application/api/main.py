from telegram.ext import Filters, MessageHandler, CallbackQueryHandler, Updater, CommandHandler

from router import start_router, query_router, keyboard_router
from handlers.commands import change_lang_command_handler
from quiz_app.config import API_TOKEN

if not API_TOKEN:
    raise ValueError("Not found API KEY in .env file")

def main():
    updater = Updater(token=API_TOKEN)
    dispatcher = updater.dispatcher


    dispatcher.add_handler(CommandHandler("start", start_router))
    dispatcher.add_handler(CommandHandler("changelang", change_lang_command_handler))
    dispatcher.add_handler(CallbackQueryHandler(query_router))
    dispatcher.add_handler(MessageHandler(Filters.text, keyboard_router))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
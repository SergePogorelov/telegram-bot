import logging

from telegram.ext import Updater, Filters, CommandHandler, MessageHandler, InlineQueryHandler, ConversationHandler, CallbackQueryHandler

from handlers import start, caps, trans, get_time, menu
from handlers import inline_trans
from handlers import get_anecdot, echo, unknow_comand

from handlers import hw, hws
from subscribe_news import subscribe_news_comand, news_button 
from questionnaire_hendler import start_anket, user_name, respect, user_age, user_phone, user_bio, user_evaluate, questionnaire_completing, dontknow

from handlers import inline_button_handler

from handlers import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    updater.bot.send_message(TELEGRAM_CHAT_ID, text='Сервер был перезагружен')


    dispatcher.add_handler(InlineQueryHandler(inline_trans))

    dispatcher.add_handler(CommandHandler("hw", hw))
    dispatcher.add_handler(CommandHandler("hws", hws))
    dispatcher.add_handler(CommandHandler('news', subscribe_news_comand))
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('caps', caps))
    dispatcher.add_handler(CommandHandler('trans', trans))
    dispatcher.add_handler(CommandHandler('time', get_time))
    dispatcher.add_handler(CommandHandler('menu', menu))

    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Хочу поболтать!'), start_anket)],
        states={
            'user_name': [MessageHandler(Filters.text & (~Filters.command), user_name)],
            'respect': [MessageHandler(Filters.regex('Конечно на Ты!|Лучше на Вы.'), respect)],
            'user_age': [MessageHandler(Filters.regex(r'^\d{,2}$'), user_age)],
            'user_phone':[MessageHandler(Filters.contact | Filters.regex('Мы еще не так близко знакомы, чтобы обмениваться телефонами!'), user_phone)],
            'user_bio': [MessageHandler(Filters.text & (~Filters.command | Filters.regex('Пропустить')), user_bio)],
            'user_evaluate': [MessageHandler(Filters.regex('^[1-5]$'), user_evaluate)],
            'user_comment': [MessageHandler(Filters.text & (~Filters.command) | Filters.regex('Пропустить'), questionnaire_completing)],
        },
        fallbacks = [MessageHandler(Filters.text | Filters.video | Filters.photo | Filters.document, dontknow)]
    ))

    dispatcher.add_handler(CallbackQueryHandler(inline_button_handler))

    dispatcher.add_handler(MessageHandler(Filters.command, unknow_comand))
    dispatcher.add_handler(MessageHandler(Filters.regex('Хочу анекдот!'), get_anecdot))
    dispatcher.add_handler(MessageHandler(Filters.regex('Хочу быть в курсе событий!'), news_button))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
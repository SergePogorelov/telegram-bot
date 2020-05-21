import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, InlineQueryHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent


TELEGRAM_TOKEN = "1088853276:AAH1th99WSIaU5aUBNPak_SQbErsEoTsO1w"


updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

dispatcher.add_handler(CommandHandler('start', start))


def echo(update, context):   
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)


def caps(update, context):
    text_caps = "Добавьте текст после /caps\nПример: '/caps текст'\nЯ верну: 'ТЕКСТ'"
    if context.args:
        text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

dispatcher.add_handler(CommandHandler('caps', caps))


def inline_caps(update, context):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)

dispatcher.add_handler(InlineQueryHandler(inline_caps))


def unknow_comand(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Эта команда не поддерживается.\nПопробуйте написать /caps")

dispatcher.add_handler(MessageHandler(Filters.command, unknow_comand))


updater.start_polling()
updater.idle()

import os
import logging
import time
import requests
from dotenv import load_dotenv

from telegram.ext import Updater, CommandHandler, MessageHandler, InlineQueryHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent


load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")

updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def parse_homework_status(homework):
    homework_name = homework["homework_name"]
    if homework["status"] == "rejected":
        verdict = "К сожалению в работе нашлись ошибки."
    else:
        verdict = "Ревьюеру всё понравилось, можно приступать к следующему уроку."
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'

def get_homework_statuses(current_timestamp):
    headers = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}
    params = {"from_date": current_timestamp}
    homework_statuses = requests.get("https://praktikum.yandex.ru/api/user_api/homework_statuses/", headers=headers, params=params)
    return homework_statuses.json()

def check_hw():
    current_timestamp = int(time.time()) - 60*60*24
    new_homework = get_homework_statuses(current_timestamp)
    if new_homework.get("homeworks"):
        return parse_homework_status(new_homework.get("homeworks")[0])
    return ("Работа еще не проверена!")
    

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

dispatcher.add_handler(CommandHandler('start', start))


def echo(update, context):
    if update.message.text.upper() == "HW" and update.effective_chat.id == int(TELEGRAM_CHAT_ID):
        context.bot.send_message(chat_id=update.effective_chat.id, text=check_hw())
    else:    
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

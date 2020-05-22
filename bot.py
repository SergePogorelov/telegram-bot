import os
import logging
import time
import requests
from dotenv import load_dotenv

from telegram.ext import Updater, CommandHandler, MessageHandler, InlineQueryHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")

LAYOUT = dict(zip(map(ord, "qwertyuiop[]asdfghjkl;'zxcvbnm,./`67йцукенгшщзхъфывапролджэячсмитьбю.ё67"
                            'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~^&ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё:?'),
                            "йцукенгшщзхъфывапролджэячсмитьбю.ё67qwertyuiop[]asdfghjkl;'zxcvbnm,./`67"
                            'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё:?QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~^&'))


def parse_homework_status(homework):
    homework_name = homework["homework_name"]
    if homework["status"] == "rejected":
        verdict = "К сожалению в работе нашлись ошибки."
    else:
        verdict = "Ревьюеру всё понравилось, можно приступать к следующему уроку."
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(context):
    current_timestamp = context.job.context
    headers = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}
    params = {"from_date": current_timestamp}
    homework_statuses = requests.get("https://praktikum.yandex.ru/api/user_api/homework_statuses/", headers=headers, params=params).json()
    if homework_statuses.get("homeworks"):
        context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=parse_homework_status(homework_statuses.get("homeworks")[0]))
        context.job.context = homework_statuses.get("current_date")


def hw(update, context):
    if update.effective_chat.id == int(TELEGRAM_CHAT_ID):
        current_timestamp = int(time.time()) 

        if context.args:
            try:
                arg = int(context.args[0])
            except (ValueError):
                update.message.reply_text('Попробуйте "/hw <часы>"')
                return

            current_timestamp = arg*60*60
            if current_timestamp < 0:
                update.message.reply_text('Простите, мы не можем вернуться в прошлое! :)')
                return

        if 'job_hw_check' in context.chat_data:
            old_job_hw_check = context.chat_data['job_hw_check']
            old_job_hw_check.schedule_removal()
        
        new_job_hw_check = context.job_queue.run_repeating(get_homework_statuses, interval=300, first=0, context=current_timestamp)
        context.chat_data['job_hw_check'] = new_job_hw_check
        update.message.reply_text('Пошел узнавать!\nКак только твою домашнюю работу проверят, сообщу результат.')

    else: 
        context.bot.send_message(chat_id=update.effective_chat.id, text="Эта команда не поддерживается.\nПопробуйте написать /caps")


def hws(update, context):
    if 'job_hw_check' not in context.chat_data:
        update.message.reply_text('Проверка статуса домашней работы еще не запущена.\nДля запуска напиши:\n"/hw <часы>"')
        return

    job = context.chat_data['job_hw_check']
    job.schedule_removal()
    del context.chat_data['job_hw_check']

    update.message.reply_text('Остановил проверку статуса. Для повторного запуска напиши:\n"/hw <часы>"')


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def caps(update, context):
    text_caps = "Добавьте текст после /caps\nПример: '/caps текст'\nЯ верну: 'ТЕКСТ'"
    if context.args:
        text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


def trans(update, context):
    text_trans = "Добавьте текст после /trans\nПример: '/trans ntrcn'\nЯ верну: 'текст'"
    if context.args:
        text_trans = ' '.join(context.args).translate(LAYOUT)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_trans)


def inline_trans(update, context):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query,
            title='Trans',
            description='EN->RU',
            input_message_content=InputTextMessageContent(query.translate(LAYOUT))
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)


def unknow_comand(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Эта команда не поддерживается.\nПопробуйте написать /caps")


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():

    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("hw", hw))
    dispatcher.add_handler(CommandHandler("hws", hws))
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('caps', caps))
    dispatcher.add_handler(CommandHandler('trans', trans))
    dispatcher.add_handler(InlineQueryHandler(inline_trans))
    dispatcher.add_handler(MessageHandler(Filters.command, unknow_comand))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))
    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
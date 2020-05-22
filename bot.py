import os
import logging
import time
import datetime

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from telegram.ext import Updater, CommandHandler, MessageHandler, InlineQueryHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
NEWSAPI = os.getenv("NEWSAPI")

LAYOUT = dict(zip(map(ord, "qwertyuiop[]asdfghjkl;'zxcvbnm,./`67йцукенгшщзхъфывапролджэячсмитьбю.ё67"
                            'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~^&ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё:?'),
                            "йцукенгшщзхъфывапролджэячсмитьбю.ё67qwertyuiop[]asdfghjkl;'zxcvbnm,./`67"
                            'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё:?QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~^&'))


def parse_homework_status(homework):
    homework_name = homework["lesson_name"]
    if homework["status"] == "rejected":
        verdict = "К сожалению в работе нашлись ошибки."
    else:
        verdict = "Ревьюеру всё понравилось, можно приступать к следующему уроку."
    return f'У вас проверили работу\n"_{homework_name}_"!\n\n*{verdict}*'


def check_homework_statuses(context):
    current_timestamp = context.job.context
    headers = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}
    params = {"from_date": current_timestamp}
    homework_statuses = requests.get("https://praktikum.yandex.ru/api/user_api/homework_statuses/", headers=headers, params=params)
    try:
        homework_statuses.raise_for_status()
    except requests.exceptions.HTTPError:
        context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text='Request Error')
        return

    homeworks = homework_statuses.json().get("homeworks")
    current_date = homework_statuses.json().get("current_date")

    if homeworks:
        context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=parse_homework_status(homeworks[0]), parse_mode='Markdown')
        if current_date:
            context.job.context = homework_statuses.json().get("current_date")


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
        
        new_job_hw_check = context.job_queue.run_repeating(check_homework_statuses, interval=300, first=0, context=current_timestamp)
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

    update.message.reply_text('Остановил проверку статуса.\nДля повторного запуска напиши:\n"/hw <часы>"')


def start(update, context):
    keyboard = ReplyKeyboardMarkup([['Хочу анекдот!'], ['Хочу быть в курсе событий!']], resize_keyboard=True, one_time_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Я могу отправить тебе случайный анекдот или последние новости.\nЧто выбираешь?", reply_markup=keyboard)


def get_anecdot(update, context):
    response = requests.get('http://anekdotme.ru/random')
    page = BeautifulSoup(response.text, 'html.parser')
    find = page.select('.anekdot_text')
    for text in find:
        page = text.getText().strip()
    update.message.reply_text(page)


def get_news(bot, chat_id, max_result=5):
    params = {'country': 'ru', 'apiKey': NEWSAPI}
    response = requests.get('http://newsapi.org/v2/top-headlines', params=params)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        bot.send_message(chat_id=chat_id, text='Request Error')
        return

    articles = response.json().get('articles')[:max_result]
    for article in articles:
        title = article['title']
        description = article['description']
        url = article['url']
        publishedAt = datetime.datetime.strptime(article['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
        bot.send_message(chat_id=chat_id, text=f'*{title}*\n_{publishedAt.strftime("%d.%m.%Y, %H:%M")}_\n\n{description}\n{url}\n', parse_mode='Markdown')


def news(update, context):
    get_news(bot=context.bot, chat_id=update.effective_chat.id)


def get_daily_news(context):
    get_news(bot=context.bot, chat_id=context.job.context)


def subscribe_news(update, context):
    subs_news = context.job_queue.run_daily(get_daily_news, time=datetime.time(hour=10, minute=30, second=0, tzinfo=datetime.timezone(datetime.timedelta(hours=3))), context=update.effective_chat.id)
    # context.chat_data['subs_news'] = subs_news
    update.message.reply_text(f'Вы подписались на ежедневную новостную рассылку.\n*Ждите новостей {datetime.datetime.strftime(subs_news.next_t, "%d.%m.%Y в %H:%M")}*')


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


    dispatcher.add_handler(InlineQueryHandler(inline_trans))

    dispatcher.add_handler(CommandHandler("hw", hw))
    dispatcher.add_handler(CommandHandler("hws", hws))
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('news', subscribe_news))
    dispatcher.add_handler(CommandHandler('caps', caps))
    dispatcher.add_handler(CommandHandler('trans', trans))

    
    dispatcher.add_handler(MessageHandler(Filters.command, unknow_comand))
    dispatcher.add_handler(MessageHandler(Filters.regex('Хочу анекдот!'), get_anecdot))
    dispatcher.add_handler(MessageHandler(Filters.regex('Хочу быть в курсе событий!'), news))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))


    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
import os
import time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from telegram import InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards import get_inline_keyboard
from subscribe_news import subscribe_news, unsubscribe_news

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")


LAYOUT = dict(zip(map(ord, "qwertyuiop[]asdfghjkl;'zxcvbnm,./`67йцукенгшщзхъфывапролджэячсмитьбю.ё67"
                            'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~^&ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё:?'),
                            "йцукенгшщзхъфывапролджэячсмитьбю.ё67qwertyuiop[]asdfghjkl;'zxcvbnm,./`67"
                            'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё:?QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~^&'))


# check YA homeworks status
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

            current_timestamp = current_timestamp - arg*60*60
            if current_timestamp < 0:
                update.message.reply_text('Простите, мы не можем вернуться в прошлое! :)')
                return

        if 'job_hw_check' in context.chat_data:
            old_job_hw_check = context.chat_data['job_hw_check']
            old_job_hw_check.schedule_removal()
        
        new_job_hw_check = context.job_queue.run_repeating(check_homework_statuses, interval=300, first=0, context=current_timestamp)
        context.chat_data['job_hw_check'] = new_job_hw_check
        update.message.reply_text('*Пошел узнавать!*\nКак только твою домашнюю работу проверят, сообщу результат.', parse_mode='Markdown')

    else: 
        context.bot.send_message(chat_id=update.effective_chat.id, text="Эта команда не поддерживается.\nПопробуйте написать /caps")


def hws(update, context):
    if 'job_hw_check' not in context.chat_data:
        update.message.reply_text('Проверка статуса домашней работы еще не запущена.\nДля запуска напиши:\n"/hw <часы>"')
        return

    job = context.chat_data['job_hw_check']
    job.schedule_removal()
    del context.chat_data['job_hw_check']

    update.message.reply_text('*Остановил проверку статуса*.\nДля повторного запуска напиши:\n"/hw <часы>"', parse_mode='Markdown')
# END check YA homeworks status


def get_anecdot(update, context):
    response = requests.get('http://anekdotme.ru/random')
    page = BeautifulSoup(response.text, 'html.parser')
    anecdot = page.select('.anekdot_text')[0].getText().strip()
    update.message.reply_text(anecdot)


# /COMANDS
def start(update, context):
    print(context.bot)
    keyboard = ReplyKeyboardMarkup([['Хочу анекдот!'], ['Хочу быть в курсе событий!'], ['Хочу поболтать!']], resize_keyboard=True, one_time_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Я могу отправить тебе *случайный анекдот* или *последние новости*.\n\nА можем просто поболтать.\n\nЧто выбираешь?", reply_markup=keyboard, parse_mode='Markdown')


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


def get_time(update, context):
    from subprocess import Popen, PIPE
    process = Popen('date', stdout=PIPE)
    result = process.communicate()
    text, error = result
    if error:
        text = 'Error'
    else:
        text = text.decode('utf-8')
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def unknow_comand(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Эта команда не поддерживается.\nПопробуйте написать /caps")
# END COMANDS

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


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def menu(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='ouwer menu" select some buttun: ', reply_markup=get_inline_keyboard(menu1=True))


def inline_button_handler(update, context):
    query = update.callback_query
    query.answer()

    if query.data == 'unsubscribe':
        unsubscribe_news(update, context)


    if query.data == 'subscribe':
        subscribe_news(update, context)

    if query.data == 'forward':
        query.edit_message_reply_markup(get_inline_keyboard(menu2=True))

    if query.data == 'back':
        query.edit_message_reply_markup(get_inline_keyboard(menu1=True))

    if query.data == 'botton1':
        query.edit_message_text(text='you shose botton1', reply_markup=get_inline_keyboard(menu1=True))
        context.bot.send_message(chat_id=update.effective_chat.id, text='hello', reply_markup=get_inline_keyboard(menu2=True))

if __name__ == "__main__":
    from bot import main
    main()
import os
import time

import requests
from bs4 import BeautifulSoup
import redis
from telegram import InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards import get_inline_keyboard, get_start_keyboard
from subscribe_news import subscribe_news, unsubscribe_news
from chat import generate_answer
from quiz_game import start_quiz


LAYOUT = dict(zip(map(ord, "qwertyuiop[]asdfghjkl;'zxcvbnm,./`67йцукенгшщзхъфывапролджэячсмитьбю.ё67"
                            'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~^&ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё:?'),
                            "йцукенгшщзхъфывапролджэячсмитьбю.ё67qwertyuiop[]asdfghjkl;'zxcvbnm,./`67"
                            'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё:?QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~^&'))


r = redis.StrictRedis()
if os.getenv('HEROKU'):
    r = redis.from_url(os.environ.get("REDIS_URL"))


def get_anecdot(update, context):
    response = requests.get('http://anekdotme.ru/random')
    page = BeautifulSoup(response.text, 'html.parser')
    anecdot = page.select('.anekdot_text')[0].getText().strip()
    update.message.reply_text(anecdot)


# /COMANDS
def start(update, context):
    r.sadd('users', update.effective_chat.id)
    text = "Я могу отправить тебе *случайный анекдот* или *последние новости*.\n\nА можем просто *поболтать* или *поиграть в КВИЗ*.\n\nЧто выбираешь?\n\n\n_А еще я умею переводить текст в ПРОПИСНЫЕ буквы и автоматически менять раскладку клавиатуры. Для этого воспользуйся командами\n/caps и /trans. \nКстати, команда /trans работает и в илайн-режиме!_"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=get_start_keyboard(), parse_mode='Markdown')


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
    context.bot.send_message(chat_id=update.effective_chat.id, text="Эта команда не поддерживается.\nПопробуйте написать /start")
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


def quiz(update, context):
    start_quiz(update, context)


def chat(update, context):
    update.message.reply_text(generate_answer(update.message.text))


def inline_button_news(update, context):
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
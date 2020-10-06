import logging
import os
import datetime
from dotenv import load_dotenv
import time

import redis

from telegram.ext import (
    Updater,
    Filters,
    CommandHandler,
    MessageHandler,
    InlineQueryHandler,
    ConversationHandler,
    CallbackQueryHandler,
)

from handlers import start, caps, trans, get_time
from handlers import inline_trans
from handlers import get_anecdot, chat, unknow_comand, quiz

from yandex_hw import hw, hws, check_homework_statuses
from subscribe_news import subscribe_news_comand, news_button, get_daily_news
from questionnaire_hendler import (
    start_anket,
    user_name,
    respect,
    user_age,
    user_phone,
    user_bio,
    user_evaluate,
    questionnaire_completing,
    dontknow,
)
from quiz_game import inline_button_quiz, inline_button_theme

from handlers import inline_button_news

load_dotenv()


TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

r = redis.StrictRedis()
if os.getenv("HEROKU"):
    r = redis.from_url(os.environ.get("REDIS_URL"))


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    updater.bot.send_message(TELEGRAM_CHAT_ID, text="Сервер был перезагружен")
    users_subscribe_news = r.smembers("users:subscribe:news")
    for user in users_subscribe_news:
        updater.job_queue.run_daily(
            get_daily_news,
            name=f"subscribe_news_for{int(user)}",
            time=datetime.time(
                hour=10,
                minute=30,
                second=0,
                tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
            ),
            context=int(user),
        )
    updater.bot.send_message(
        TELEGRAM_CHAT_ID,
        text=f"The following people have subscribed to the newsletter: {users_subscribe_news}",
    )

    job_hw_check = r.smembers("job_hw_check")
    if job_hw_check:
        current_timestamp = int(time.time())
        updater.job_queue.run_repeating(
            check_homework_statuses,
            name="job_hw_check",
            interval=300,
            first=0,
            context=current_timestamp,
        )
        updater.bot.send_message(
            TELEGRAM_CHAT_ID,
            text="Пошел узнавать!\nКак только твою домашнюю работу проверят, сообщу результат.",
        )

    dispatcher.add_handler(InlineQueryHandler(inline_trans))

    dispatcher.add_handler(CommandHandler("hw", hw))
    dispatcher.add_handler(CommandHandler("hws", hws))
    dispatcher.add_handler(CommandHandler("news", subscribe_news_comand))
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("caps", caps))
    dispatcher.add_handler(CommandHandler("trans", trans))
    dispatcher.add_handler(CommandHandler("time", get_time))

    dispatcher.add_handler(MessageHandler(Filters.command, unknow_comand))
    dispatcher.add_handler(
        MessageHandler(Filters.regex(r"^Хочу анекдот!$"), get_anecdot)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.regex(r"^Хочу быть в курсе событий!$"), news_button)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.regex(r"^Хочу поиграть в квиз!$"), quiz)
    )

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(Filters.regex(r"^Хочу поболтать!$"), start_anket)
            ],
            states={
                "user_name": [
                    MessageHandler(Filters.text & (~Filters.command), user_name)
                ],
                "respect": [
                    MessageHandler(
                        Filters.regex(r"^Конечно на Ты!$|^Лучше на Вы.$"), respect
                    )
                ],
                "user_age": [MessageHandler(Filters.regex(r"^\d{,2}$"), user_age)],
                "user_phone": [
                    MessageHandler(
                        Filters.contact
                        | Filters.regex(
                            r"^Мы еще не так близко знакомы, чтобы обмениваться телефонами!$"
                        ),
                        user_phone,
                    )
                ],
                "user_bio": [
                    MessageHandler(
                        Filters.text
                        & (~Filters.command | Filters.regex(r"^Пропустить$")),
                        user_bio,
                    )
                ],
                "user_evaluate": [
                    MessageHandler(Filters.regex(r"^[1-5]$"), user_evaluate)
                ],
                "user_comment": [
                    MessageHandler(
                        Filters.text & (~Filters.command)
                        | Filters.regex(r"^Пропустить$"),
                        questionnaire_completing,
                    )
                ],
            },
            fallbacks=[
                MessageHandler(
                    Filters.text | Filters.video | Filters.photo | Filters.document,
                    dontknow,
                )
            ],
        )
    )

    dispatcher.add_handler(
        CallbackQueryHandler(inline_button_news, pattern=(r"subscribe|unsubscribe"))
    )
    dispatcher.add_handler(
        CallbackQueryHandler(inline_button_quiz, pattern=(r"^[1-4]$"))
    )
    dispatcher.add_handler(
        CallbackQueryHandler(
            inline_button_theme, pattern=(r"^bot/quiz_questions/[\w\s]+.txt$")
        )
    )

    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), chat))

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
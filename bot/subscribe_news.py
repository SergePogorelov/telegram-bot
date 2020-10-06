import os
import datetime

import requests
import redis
from dotenv import load_dotenv

from keyboards import get_inline_keyboard


load_dotenv()


NEWSAPI = os.getenv("NEWSAPI")

r = redis.StrictRedis()
if os.getenv("HEROKU"):
    r = redis.from_url(os.environ.get("REDIS_URL"))


def get_news(bot, chat_id, max_result=5, unsubscribe_buttun=False):
    params = {"country": "ru", "apiKey": NEWSAPI}
    response = requests.get("http://newsapi.org/v2/top-headlines", params=params)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        bot.send_message(chat_id=chat_id, text="Request Error")
        return

    articles = response.json().get("articles")[:max_result]
    for article in articles:
        title = article["title"]
        # description = article['description']
        url = article["url"]
        publishedAt = datetime.datetime.strptime(
            article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
        )
        bot.send_message(
            chat_id=chat_id,
            text=f'{title}\n{publishedAt.strftime("%d.%m.%Y, %H:%M")}\n\n{url}\n',
        )

    if unsubscribe_buttun:
        bot.send_message(
            chat_id=chat_id,
            text="\n\n_Чтобы отписаться от рассылки, нажмите на кнопку ниже:_\n",
            parse_mode="Markdown",
            reply_markup=get_inline_keyboard(unsubscribe_buttun),
        )


def get_daily_news(context):
    get_news(bot=context.bot, chat_id=context.job.context, unsubscribe_buttun=True)


def subscribe_news(update, context):
    job = context.job_queue.get_jobs_by_name(
        name=f"subscribe_news_for{update.effective_chat.id}"
    )
    if not job or job[0].removed:
        subscr_news = context.job_queue.run_daily(
            get_daily_news,
            name=f"subscribe_news_for{update.effective_chat.id}",
            time=datetime.time(
                hour=10,
                minute=30,
                second=0,
                tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
            ),
            context=update.effective_chat.id,
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Вы подписались на ежедневную новостную рассылку.\n*Ждите первых новостей {datetime.datetime.strftime(subscr_news.next_t, "%d.%m.%Y в %H:%M")}*\n\n_Чтобы отписаться от рассылки, нажмите на кнопку ниже:_\n',
            parse_mode="Markdown",
            reply_markup=get_inline_keyboard(unsubscribe_buttun=True),
        )
        r.sadd("users:subscribe:news", update.effective_chat.id)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вы уже подписаны на нашу рассылку. 😜",
        )


def unsubscribe_news(update, context):
    job = context.job_queue.get_jobs_by_name(
        name=f"subscribe_news_for{update.effective_chat.id}"
    )
    if not job:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вы еще не подписаны на нашу рассылку.",
        )
    elif job[0].removed:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вы уже отписались от рассылки. 😣\nЧтобы подписаться еще раз, нажмите:",
            reply_markup=get_inline_keyboard(subscribe_buttun=True),
        )
    else:
        job[0].schedule_removal()
        r.srem("users:subscribe:news", update.effective_chat.id)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вы отписались от рассылки. 😣\nЧтобы подписаться еще раз, нажмите:",
            reply_markup=get_inline_keyboard(subscribe_buttun=True),
        )


def news_button(update, context):
    get_news(bot=context.bot, chat_id=update.effective_chat.id)


def subscribe_news_comand(update, context):
    subscribe_news(update, context)


if __name__ == "__main__":
    from bot import main

    main()
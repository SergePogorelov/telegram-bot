
import os
import time
import requests
import redis
from dotenv import load_dotenv


load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


r = redis.StrictRedis()
if os.getenv('HEROKU'):
    r = redis.from_url(os.environ.get("REDIS_URL"))


def parse_homework_status(homework):
    homework_name = homework["lesson_name"]
    if homework["status"] == "rejected":
        verdict = "К сожалению в работе нашлись ошибки."
    else:
        verdict = "Ревьюеру всё понравилось, можно приступать к следующему уроку."
        r.srem('job_hw_check', TELEGRAM_CHAT_ID)
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

        job = context.job_queue.get_jobs_by_name(name='job_hw_check')
        if not job or job[0].removed:
            context.job_queue.run_repeating(check_homework_statuses, name='job_hw_check', interval=300, first=0, context=current_timestamp)
            r.sadd('job_hw_check', TELEGRAM_CHAT_ID)
            update.message.reply_text('*Пошел узнавать!*\nКак только твою домашнюю работу проверят, сообщу результат.', parse_mode='Markdown')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='*Пока еще не проверили* 😒 \nКак только твою домашнюю работу проверят, сообщу результат.', parse_mode='Markdown')

    else: 
        context.bot.send_message(chat_id=update.effective_chat.id, text="Эта команда не поддерживается.\nПопробуйте написать /caps")

def hws(update, context):
    job = context.job_queue.get_jobs_by_name(name='job_hw_check')
    if not job or job[0].removed:
        update.message.reply_text('Проверка статуса домашней работы еще не запущена.\nДля запуска напиши:\n"/hw <часы>"')
    else:
        job[0].schedule_removal()
        r.srem('job_hw_check', TELEGRAM_CHAT_ID)
        context.bot.send_message(chat_id=update.effective_chat.id, text='*Остановил проверку статуса*.\nДля повторного запуска напиши:\n"/hw <часы>"', parse_mode='Markdown')


if __name__ == "__main__":
    from bot import main
    main()

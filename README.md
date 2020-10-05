# Telegram-bot
## Что умеет бот:
* может отправить случайный анекдот или последние новости;
* есть возможность подписаться/отписаться на ежедневную рассылку свежих новостей;
* с ботом можно поиграть в Квиз, заполнить небольшую анкету или просто поболтать на любые темы;
* через команду `/caps текст` - переводит текст из строчных в прописные `(текст -> ТЕКСТ)`;
* через команду `/trans ntrcn` переводит текст с английской раскладки на русскую `(ntrcn -> текст)` и обратно.


## Установка
Эти инструкции помогут вам создать копию проекта и запустить ее на локальном компьютере для целей разработки и тестирования.

### Запуск проекта (на примере Linux)

Перед тем, как начать: если вы не пользуетесь `Python 3`, вам нужно будет установить инструмент `virtualenv` при помощи `pip install virtualenv`. 
Если вы используете `Python 3`, у вас уже должен быть модуль [venv](https://docs.python.org/3/library/venv.html), установленный в стандартной библиотеке.

- Создайте на своем компютере папку проекта blog `mkdir tbot` и перейдите в нее `cd tbot`
- Склонируйте этот репозиторий в текущую папку `git clone https://github.com/SergePogorelov/telegram-bot.git .`
- Создайте виртуальное окружение `python3 -m venv venv`
- Установите зависимости `pip install -r requirements.txt`
- Создайте файл `.env` командой `touch .env` и добавьте в него переменные окружения:
```
NEWSAPI= #токен для получения новостей с https://newsapi.org/
PRACTICUM_TOKEN= #если вы студент Практикума, можно получать уведомления при проверке домашней работы
TELEGRAM_CHAT_ID= #ID администратора, для получения системных уведомлений от бота 
TELEGRAM_TOKEN= #токен телеграм бота
```
- Запустите бота `python3 bot/bot.py`

## В разработке использованы

- [Python](https://www.python.org/)
- [Python Telegram Bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Requests](https://requests.readthedocs.io/en/master/)
- [Beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
- [NewsApi](https://newsapi.org/)
- [Python-Levenshtein](https://pypi.org/project/python-Levenshtein/)
- [Redis](https://redis.io/)
- [Heroku](heroku.com)


# Telegram-bot
Написать боту: https://t.me/ToxicTeacher_Bot

## Что умеет бот:
* может отправить случайный анекдот или последние новости;
* предлогает подписаться на ежедневную рассылку свежих новостей командой `/news`;
* отписаться от рассылки можно кнопкой `отписаться`;
* с ботом можно поиграть в `Квиз`, заполнить небольшую `анкету` или просто `поболтать` на любые темы;
* через команду `/caps текст` - переводит текст из строчных в прописные `(текст -> ТЕКСТ)`;
* через команду `/trans ntrcn` переводит текст с английской раскладки на русскую `(ntrcn -> текст)` и обратно;
* командой `/hw` студенты Яндекс.Практикума могут зарашивать статус проверки своей домашней работы

![Bot-menu](https://i.imgur.com/q2VDdOC.png) ![news](https://i.imgur.com/DucFrec.png)

## Локальная установка
Эти инструкции помогут вам создать копию проекта и запустить ее на локальном компьютере для целей разработки и тестирования

### Запуск проекта (на примере Linux)

Перед тем, как начать: если вы не пользуетесь `Python 3`, вам нужно будет установить инструмент `virtualenv` при помощи `pip install virtualenv`. 
Если вы используете `Python 3`, у вас уже должен быть модуль [venv](https://docs.python.org/3/library/venv.html), установленный в стандартной библиотеке.

- Создайте на своем компютере папку проекта `mkdir tbot` и перейдите в нее `cd tbot`
- Склонируйте этот репозиторий в текущую папку `git clone https://github.com/SergePogorelov/telegram-bot.git .`
- Создайте виртуальное окружение `python3 -m venv venv`
- Активируйте виртуальное окружение `source venv/bin/activate`
- Установите зависимости `pip install -r requirements.txt`
- Создайте файл `.env` командой `touch .env` и добавьте в него переменные окружения:
```
NEWSAPI= #токен для получения новостей с https://newsapi.org/
PRACTICUM_TOKEN= #если вы студент Практикума, можно получать уведомления при проверке домашней работы
TELEGRAM_CHAT_ID= #ID администратора, для получения системных уведомлений от бота 
TELEGRAM_TOKEN= #токен телеграм бота
```
- Запустите бота `python3 bot/bot.py`


## Деплой на сервер Heroku
Эти инструкции помогут вам разместить вашего бота на сервере [Heroku](https://heroku.com)

### Как разместить бота на Heroku
- Зарегистрируйтесь на [Heroku](https://heroku.com)
- Создайте приложение (кнопка `New` → `Create new app`)

![Create new app](https://i.imgur.com/BQvCoS5.png)

- В разделе `Deploy`, выберите `GitHub` в разделе `Deployment method` и нажмите `Connect to GitHub`

![Connect to GitHub](https://i.imgur.com/TJ9sJN5.png)

- Введите названия репозитория в котором находтся код
- После нажатия кнопки `Deploy Branch` Heroku установит все зависимости и запустит приложение на сервере
- На вкладке `Resources` подключите [Redis](https://devcenter.heroku.com/articles/heroku-redis) и включите переключатель в разделе `Free dynos`

![Resources](https://i.imgur.com/Byi3UUd.png)

- Перейдите на вкладку `Settings` и в разделе `Config Vars` добавьте переменные окружения

![Config Vars](https://i.imgur.com/FMhDvYH.png)

- Перезапустите сервер, выключив и включив `Free dynos`

![Free dynos](https://i.imgur.com/BQBReQO.png)


## В разработке использованы

- [Python](https://www.python.org/)
- [Python Telegram Bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Requests](https://requests.readthedocs.io/en/master/)
- [Beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
- [NewsApi](https://newsapi.org/)
- [Python-Levenshtein](https://pypi.org/project/python-Levenshtein/)
- [Redis](https://redis.io/)
- [Heroku](https://heroku.com)

## Лицензия
Этот проект лицензируется по лицензии `BSD 3-Clause License` - см. [LICENSE.md](https://github.com/SergePogorelov/telegram-bot/blob/master/LICENSE) для получения подробной информации.

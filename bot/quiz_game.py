from glob import glob

from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, Updater


def open_file(path_to_file, mode="r"):
    try:
        file = open(path_to_file, mode, encoding="utf-8")
    except IOError as e:
        print(f"Файл с вопросами не найден!\n{e}")
    else:
        return file


def next_line(file):
    line = file.readline()
    line = line.replace("/", "\n")
    return line


def block(file):
    question = next_line(file)
    answers = []
    for _ in range(4):
        answers.append(next_line(file))
    try:
        correct = int(next_line(file))
    except ValueError:
        correct = None
    comment = next_line(file)
    return question, answers, correct, comment


def get_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data=1),
            InlineKeyboardButton("2", callback_data=2),
        ],
        [
            InlineKeyboardButton("3", callback_data=3),
            InlineKeyboardButton("4", callback_data=4),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_keyboard_theme():
    themes = glob("bot/quiz_questions/*")
    keyboard = []
    for path in themes:
        theme = path.rsplit("/", 1)[-1].strip(".txt")
        keyboard.append(InlineKeyboardButton(theme, callback_data=path))
    return InlineKeyboardMarkup([keyboard])


def welcome(theme, update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"""
Добро пожаловать в игру!
Сейчас я буду задавать вопросы и давать на выбор 4 варианта ответа.

Тема сегодняшней игры:
*{theme}*""",
        parse_mode=ParseMode.MARKDOWN,
    )


def get_next_question(update: Updater, context: CallbackContext):
    quiz_file = context.chat_data["quiz_file"]
    question, answers, correct, comment = block(quiz_file)

    if question:
        answers_text = []
        for i in range(4):
            answers_text.append(f"{i+1}: {answers[i]}")
        context.chat_data["correct"] = correct
        context.chat_data["comment"] = comment
        context.chat_data["num_q"] += 1
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'*Вопрос номер: {context.chat_data["num_q"]}*\n\n{question}\n{"".join(answers_text)}',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_keyboard(),
        )
    else:
        quiz_file.close()
        text = f'Это был последний вопрос!\nПравильных ответов: {context.chat_data["score"]} из {context.chat_data["num_q"]}'
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
        )


def inline_button_quiz(update: Updater, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if int(query.data) == int(context.chat_data["correct"]):
        context.chat_data["score"] += 1
        text = f'Ваш ответ: {int(query.data)}\n\nВерно!😉\n{context.chat_data["comment"]}\nПравильных ответов: {context.chat_data["score"]} из {context.chat_data["num_q"]}'
    else:
        text = f'Ваш ответ: {int(query.data)}\n\nНе верно. 😔\n{context.chat_data["comment"]}\nПравильных ответов: {context.chat_data["score"]} из {context.chat_data["num_q"]}'

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    get_next_question(update, context)


def inline_button_theme(update: Updater, context: CallbackContext):
    query = update.callback_query
    query.answer()
    quiz_file = open_file(query.data, "r")

    context.chat_data["quiz_file"] = quiz_file
    context.chat_data["score"] = 0
    context.chat_data["num_q"] = 0

    theme = next_line(quiz_file)
    welcome(theme, update, context)
    get_next_question(update, context)


def start_quiz(update: Updater, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите тему: ",
        reply_markup=get_keyboard_theme(),
    )


if __name__ == "__main__":
    from bot import main

    main()
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def get_inline_keyboard(
    unsubscribe_buttun=False, subscribe_buttun=False, menu1=False, menu2=False
):

    keyboard = []

    if unsubscribe_buttun:
        keyboard = [
            [
                InlineKeyboardButton("Отписаться", callback_data="unsubscribe"),
            ]
        ]

    if subscribe_buttun:
        keyboard = [
            [
                InlineKeyboardButton(
                    "Подписаться на новости", callback_data="subscribe"
                ),
            ]
        ]

    return InlineKeyboardMarkup(keyboard)


def get_start_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["Хочу анекдот!"],
            ["Хочу быть в курсе событий!"],
            ["Хочу поболтать!"],
            ["Хочу поиграть в квиз!"],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


if __name__ == "__main__":
    from bot import main

    main()
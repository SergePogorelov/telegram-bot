from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def get_inline_keyboard(
    unsubscribe_buttun=False, 
    subscribe_buttun=False, 
    menu1=False,
    menu2=False
    ):

    keyboard = []

    if unsubscribe_buttun:
        keyboard = [
            [
                InlineKeyboardButton('Отписаться', callback_data='unsubscribe'),
            ]
        ]

    if subscribe_buttun:
        keyboard = [
            [
                InlineKeyboardButton('Подписаться на новости', callback_data='subscribe'),
            ]
        ]

    if menu1:
        keyboard = [
            [
                InlineKeyboardButton('botton1', callback_data='botton1'),
                InlineKeyboardButton('botton2', callback_data='botton2'),
                InlineKeyboardButton('botton3', callback_data='botton3'),
            ],
            [
                InlineKeyboardButton('botton4', callback_data='botton4'),
                InlineKeyboardButton('botton5', callback_data='botton5'),
            ],
            [
                InlineKeyboardButton('forward', callback_data='forward'),
            ]
        ]

    if menu2:
        keyboard = [
            [
                InlineKeyboardButton('botton7', callback_data='botton7'),
                InlineKeyboardButton('botton8', callback_data='botton8'),
                InlineKeyboardButton('botton9', callback_data='botton9'),
            ],
            [
                InlineKeyboardButton('botton10', callback_data='botton10'),
                InlineKeyboardButton('botton11', callback_data='botton11'),
            ],
            [
                InlineKeyboardButton('back', callback_data='back'),
            ]
        ]

    return InlineKeyboardMarkup(keyboard)


def get_start_keyboard():
    return ReplyKeyboardMarkup(
        [
            ['Хочу анекдот!'], 
            ['Хочу быть в курсе событий!'], 
            ['Хочу поболтать!'],
            ['Хочу поиграть в квиз!']
        ], 
        resize_keyboard=True, 
        one_time_keyboard=True
    )


if __name__ == "__main__":
    from bot import main
    main()
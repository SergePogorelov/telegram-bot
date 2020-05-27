from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import ConversationHandler


#ANKETA
def start_anket(update, context):
    update.message.reply_text("- Привет! Меня зовут Профессор бот. Я проведу с вами беседу.\n\n Как вас зовут?", reply_markup=ReplyKeyboardRemove())
    return 'user_name'


def user_name(update, context):
    context.user_data['user_name'] = update.message.text
    update.message.reply_text('Можем перейти на *"ты"*?\nИли удобнее на *"вы"*?', reply_markup=ReplyKeyboardMarkup([['Конечно на Ты!'], ['Лучше на Вы.']], resize_keyboard=True, one_time_keyboard=True), parse_mode='Markdown')
    return 'respect'  


def respect(update, context):
    resp = 'вам'
    if update.message.text == 'Конечно на Ты!':
        resp = 'тебе'
    context.user_data['respect'] = resp
    update.message.reply_text(f'Запомнил!\nА сколько {resp} лет?')
    return 'user_age'


def user_age(update, context):
    context.user_data['user_age'] = update.message.text
    button1 = KeyboardButton('Конечно!', request_contact=True)
    button2 = KeyboardButton('Мы еще не так близко знакомы, чтобы обмениваться телефонами!')
    keyboard = ReplyKeyboardMarkup([[button1], [button2]], resize_keyboard=True, one_time_keyboard=True)
    text = 'Пришлите, свой номер телефона, пожалуйста.'
    if context.user_data['respect'] == 'тебе':
        text = 'Оставишь номерок?'
    update.message.reply_text(text=text, reply_markup=keyboard)
    return 'user_phone'


def user_phone(update, context):
    if update.message.contact:
        context.user_data['user_phone'] = update.message.contact.phone_number
    text = 'Расскажите'
    if context.user_data['respect'] == 'тебе':
        text = 'Расскажи'
    update.message.reply_text(text=f'{text}, пожалуйста пару слов о себе.', reply_markup=ReplyKeyboardMarkup([['Пропустить']], resize_keyboard=True, one_time_keyboard=True))
    return 'user_bio'


def user_bio(update, context):
    context.user_data['user_bio'] = update.message.text
    buttons = [[str(i)] for i in reversed(range(1, 6)) ]
    keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text(text='Оцените заполнение анкеты\n*от 1 до 5*?\n\n_5 - очень понравилось\n1- совсем плохо_', reply_markup=keyboard, parse_mode='Markdown')
    return 'user_evaluate'


def user_evaluate(update, context):
    context.user_data['user_evaluate'] = update.message.text
    text = 'Напишите короткий комментарий. Почему ваша оценка именно такая?'
    if context.user_data['respect'] == 'тебе':
        text = 'Оставь пару комментариев. Нам будет приятно:)'
    update.message.reply_text(text=text, reply_markup=ReplyKeyboardMarkup([['Пропустить']], resize_keyboard=True, one_time_keyboard=True))
    return 'user_comment'


def questionnaire_completing(update, context):
    context.user_data['user_comment'] = update.message.text

    phone = 'Ты скромняга, так что будем переписываться тут)'
    if context.user_data.get('user_phone'):
        phone = f'Твой номер телефона - *{context.user_data["user_phone"]}*, жди звонка ;)'
    
    user_bio = f'Твой рассказ о себе, поразил меня до глубины души: _{context.user_data["user_bio"]}_'
    if context.user_data['user_bio'] == 'Пропустить':
        user_bio = 'Жаль, что ты ничего не рассказал о себе :('
    user_comment = f'Твои слова запали на веки в мое железное сердце:\n    _{context.user_data["user_comment"]}_'
    
    if context.user_data['user_comment'] == 'Пропустить':
        user_comment = 'А тут мог быть твой комментарий...'

    end_message = f"""
    С тобой было приятно пообщаться, давай подведем итоги!
    Bот, что я о тебе узнал:

    Тебя зовут: *{context.user_data['user_name']}*
    Твой возраст: *{context.user_data['user_age']}*
    {phone}
    {user_bio}
    Ты оценил нас на *{context.user_data['user_evaluate']}* 
    {user_comment}

    Приходи еще - пообщаемся! Чао!"""
    
    update.message.reply_text(text=end_message, parse_mode='Markdown', reply_markup=ReplyKeyboardMarkup([['/start']], resize_keyboard=True, one_time_keyboard=True))
    return ConversationHandler.END


def dontknow(update, context):
    update.message.reply_text(text='Непоняяятненько, можно еще раз)')

from telebot.types import ReplyKeyboardMarkup


def dashboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=1)

    markup.row('Пополнить баланс')
    markup.row('Посмотреть историю пополнений')
    markup.row('Задать настройки комиссии')

    return markup

import telebot
import os
import keyboards
import db
from decorators import login_required
from ligaAPI import user_exists, send_payment

bot = telebot.TeleBot(os.getenv('LIGA_TAXI_TOKEN'))


def sum_range_step(message, user_data):
    user_data.start = message.text.split(' ')[0]
    user_data.end = message.text.split(' ')[1]
    bot.send_message(message.chat.id, 'Введите процент комиссии:')
    bot.register_next_step_handler(message, percent_commission_step, user_data)


def percent_commission_step(message, user_data):
    user_data.percent = message.text
    bot.send_message(message.chat.id, 'Введите фиксированую сумму комиссии:')
    bot.register_next_step_handler(message, fixed_commission_step, user_data)


def fixed_commission_step(message, user_data):
    user_data.fixed = message.text
    success_status = db.add_commission_settings(user_data.tg_id, user_data.start, user_data.end, user_data.fixed,
                                                user_data.percent)
    if success_status:
        bot.send_message(message.chat.id, 'Настройки успешно сохранены.')


def send_payment_step(message, user_data):
    user_data.user_id = message.chat.id
    user_data.payment_sum = message.text
    user = db.get_user(user_data.user_id)
    # пароль будет предпоследим  елементом в кортеже
    user_data.password = user[-2]
    if user_exists(user_data.name, user_data.password):
        try:
            payment_status, driver_balance = send_payment(user_data.user_id, user_data.name, user_data.password,
                                                          user_data.driver_id, user_data.payment_sum)
            if payment_status:
                bot.send_message(message.chat.id, f'Новый баланс водителя - {driver_balance}')
        except ValueError:
            bot.send_message(message.chat.id, 'Неверные данные, попробуйте снова')
    else:
        bot.send_message(message.chat.id, 'Неверные данные, попробуйте снова')


def input_driver_id_step(message, user_data):
    user_data.name = message.text
    bot.send_message(message.chat.id, 'Введите id водителя(в условиях демо версии):')
    bot.register_next_step_handler(message, input_transfer_amount_step, user_data)


def input_transfer_amount_step(message, user_data):
    user_data.driver_id = message.text
    bot.send_message(message.chat.id, 'Введите сумму пополнения:')
    bot.register_next_step_handler(message, send_payment_step, user_data)


def input_domain_step(message, user_data):
    bot.send_message(message.chat.id, 'Введите api name:')
    user_data.hostname = message.text
    bot.register_next_step_handler(message, input_api_name_step, user_data)


def input_api_name_step(message, user_data):
    bot.send_message(message.chat.id, 'Введите api password:')
    user_data.name = message.text
    bot.register_next_step_handler(message, input_api_password_step, user_data)


def input_api_password_step(message, user_data):
    user_data.password = message.text
    login_step(message, user_data)


def login_step(message, user_data):
    if user_exists(user_data.name, user_data.password):
        db.create_user(tg_id=user_data.tg_id,
                       hostname=user_data.hostname,
                       name=user_data.name,
                       password=user_data.password)
        db.login(message.chat.id)
        bot.send_message(message.chat.id, text='Успешный вход', reply_markup=keyboards.dashboard())
    else:
        bot.send_message(message.chat.id, 'Некоректные данные попробуйте снова')


@bot.message_handler(commands=['start'])
def start_handler(message):
    if db.get_user(message.chat.id):
        if db.user_is_logged(message.chat.id):
            bot.send_message(message.chat.id, text='Меню', reply_markup=keyboards.dashboard())
    else:
        user_data = type('UserData', (), {})  # создание экземпляра класса UserData
        user_data.tg_id = message.chat.id
        bot.send_message(message.chat.id, 'Введите домен учетной записи:')
        bot.register_next_step_handler(message, input_domain_step, user_data)


@bot.message_handler(func=lambda message: message.text == 'Пополнить баланс')
@login_required
def update_balance_handler(message):
    user_data = type('UserData', (), {})  # создание экземпляра класса UserData
    bot.send_message(message.chat.id, 'Введите api name: ')
    bot.register_next_step_handler(message, input_driver_id_step, user_data)


@bot.message_handler(func=lambda message: message.text == 'Посмотреть историю пополнений')
@login_required
def update_balance_handler(message):
    payments_history = db.get_payment_history(message.chat.id)
    if payments_history is []:
        bot.send_message(message.chat.id, 'История пустая')

    else:
        bot.send_message(message.chat.id, 'История пополнений')
        for payment in payments_history:
            bot.send_message(message.chat.id,
                             f'Сумма - {payment[1]} Время - {payment[2].strftime("%m/%d/%Y, %H:%M:%S")}')


@bot.message_handler(func=lambda message: message.text == 'Задать настройки комиссии')
@login_required
def update_balance_handler(message):
    count = db.count_commission_settings(message.chat.id)
    if count is None:
        user_data = type('UserData', (), {})
        user_data.tg_id = message.chat.id
        bot.send_message(message.chat.id, 'Введите сумму от и до через пробел:')
        bot.register_next_step_handler(message, sum_range_step, user_data)

    elif count < 3:
        user_data = type('UserData', (), {})
        user_data.tg_id = message.chat.id
        bot.send_message(message.chat.id, 'Введите сумму от и до через пробел:')
        bot.register_next_step_handler(message, sum_range_step, user_data)
    else:
        bot.send_message(message.chat.id, 'Задано максимально количество настроек')


if __name__ == '__main__':
    db.create_tables()

    bot.polling()

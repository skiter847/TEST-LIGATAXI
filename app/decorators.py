from db import user_is_logged


def login_required(func):
    """ Вызывает функцию только если пользыватель авторизован """

    def wrapper(message):
        if user_is_logged(message.chat.id):
            func(message)

    return wrapper

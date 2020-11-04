import psycopg2
from datetime import datetime
import os


def create_tables():
    queries = (
        '''CREATE TABLE IF NOT EXISTS users (
                           tg_id INTEGER PRIMARY KEY,
                           hostname VARCHAR(200) NOT NULL,
                           name VARCHAR(200)  NOT NULL,
                           password VARCHAR(200) NOT NULL,
                           islogged BOOLEAN DEFAULT false NOT NULL)
        ''',
        '''CREATE TABLE IF NOT EXISTS payment_history (
                    id SERIAL PRIMARY KEY,
                    sum_transfer INTEGER NOT NULL,
                    created TIMESTAMP NOT NULL,                    
                    user_id INTEGER NOT NULL)
        ''',
        '''CREATE TABLE IF NOT EXISTS commission_settings (
            id SERIAL PRIMARY KEY,
            sum_start INTEGER NOT NULL,
            sum_end INTEGER NOT NULL,
            percent_commission INTEGER NOT NULL,
            fixed_commission INTEGER NOT NULL,
            user_id INTEGER NOT NULL
        )
        '''
    )

    with psycopg2.connect(dbname='postgres', user='postgres', password='secret',
                          host='localhost',
                          port=5432) as conn:
        with conn.cursor() as cursor:
            for query in queries:
                cursor.execute(query)


def login(tg_id):
    with psycopg2.connect(dbname='postgres', user='postgres', password='secret',
                          host='localhost',
                          port=5432) as conn:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE users SET isLogged = True WHERE tg_id = %s', (tg_id,))

            conn.commit()


def create_user(tg_id, hostname, name, password):
    with psycopg2.connect(dbname='postgres', user='postgres', password='secret',
                          host='localhost',
                          port=5432) as conn:
        with conn.cursor() as cursor:
            values = (tg_id, hostname, name, password)
            cursor.execute('INSERT INTO users (tg_id, hostname, name, password) VALUES (%s, %s, %s, %s)', values)

            conn.commit()


def user_is_logged(tg_id):
    with psycopg2.connect(dbname='postgres', user='postgres', password='secret',
                          host='localhost',
                          port=5432) as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT isLogged FROM users WHERE tg_id = %s', (tg_id,))
            login_status = cursor.fetchone()
            if login_status is not None:
                return login_status[0]


def add_payment_history(tg_id, payment_sum):
    with psycopg2.connect(dbname='postgres', user='postgres', password='secret',
                          host='localhost',
                          port=5432) as conn:
        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO payment_history (sum_transfer, created, user_id) VALUES(%s, %s, %s)',
                           (payment_sum, datetime.now(), tg_id))
            conn.commit()


def get_user(tg_id):
    with psycopg2.connect(dbname='postgres', user='postgres', password='secret',
                          host='localhost',
                          port=5432) as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE tg_id = %s', (tg_id,))
            user = cursor.fetchone()
            return user


def add_commission_settings(tg_id, start, end, fixed, percent):
    with psycopg2.connect(dbname='postgres', user='postgres', password='secret',
                          host='localhost',
                          port=5432) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO commission_settings(sum_start, sum_end, percent_commission, fixed_commission, user_id) VALUES (%s, %s, %s, %s, %s)',
                (start, end, percent, fixed, tg_id))
            conn.commit()

            return True


def count_commission_settings(tg_id):
    with psycopg2.connect(dbname='postgres', user='postgres', password='secret',
                          host='localhost',
                          port=5432) as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT COUNT(%s) FROM commission_settings', (tg_id,))
            return cursor.fetchone()[0]


def get_payment_history(tg_id):
    with psycopg2.connect(dbname='postgres', user='postgres', password='secret',
                          host='localhost',
                          port=5432) as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM payment_history WHERE user_id = %s ORDER BY created DESC LIMIT 10', (tg_id,))

            result = cursor.fetchall()
            return result

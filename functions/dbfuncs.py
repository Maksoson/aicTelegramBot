#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datafiles import config
from contextlib import closing
import dj_database_url
import psycopg2
import datetime
from functions import otherfuncs


class DatabaseFuncs:

    def __init__(self, bot):
        self.bot = bot
        self.other_funcs = otherfuncs.OtherFuncs()

    # Проверка данных о пользователе из БД на актуальность
    def check_user(self, message):
        if self.get_user_id(message) is not None:
            if not self.other_funcs.compare_user_data(self.get_user(message), message):
                self.update_user(message)
                return True
        else:
            return False

    # Добавить пользователя
    def add_user(self, message):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'INSERT INTO public.users (user_accname, user_firstname, user_lastname, ' \
                                                  'user_id, user_chat_id, user_language, user_isbot) ' \
                        'VALUES (%s, %s, %s, %s, %s, %s, %s)'
                try:
                    cursor.execute(query,
                                   [self.other_funcs.check_none(message.from_user.username),
                                    self.other_funcs.check_none(message.from_user.first_name),
                                    self.other_funcs.check_none(message.from_user.last_name),
                                    message.from_user.id, message.chat.id,
                                    message.from_user.language_code, message.from_user.is_bot])
                    connection.commit()

                    return True
                except:
                    return False

    # Обновить данные о пользователе
    def update_user(self, message):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'UPDATE public.users ' \
                        'SET user_accname = %s, user_firstname = %s, user_lastname = %s, user_id = %s, ' \
                            'user_chat_id = %s, user_language = %s, user_isbot = %s ' \
                        'WHERE user_id = %s'
                cursor.execute(query,
                               [self.other_funcs.check_none(message.from_user.username),
                                self.other_funcs.check_none(message.from_user.first_name),
                                self.other_funcs.check_none(message.from_user.last_name),
                                message.from_user.id, message.chat.id,
                                message.from_user.language_code, message.from_user.is_bot, message.from_user.id])
                connection.commit()

    # Получить id пользователя по telegram_id (user_id)
    def get_user_id(self, message):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT id FROM public.users WHERE user_id = %s'
                cursor.execute(query, [message.from_user.id])

                return cursor.fetchone()

    # Получить данные о пользователе по telegram_id
    def get_user(self, message):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT * FROM public.users WHERE user_id = %s'
                cursor.execute(query, [message.from_user.id])

                return cursor.fetchone()

    # Получить все чаты для рассылки
    def get_all_chat_ids(self):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT users.user_chat_id FROM public.users'
                cursor.execute(query)

                return cursor.fetchall()

    # Добавить запись на переговорку
    def add_to_timetable(self, message, collection):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                start_time = self.other_funcs.check_time_before(collection['start_time'])
                end_time = self.other_funcs.check_time_before(collection['end_time'])
                day_reg = int(collection['day_reg'])
                month_reg = int(collection['month_reg'])
                date_create = datetime.datetime.today().date()
                date_update = date_create

                query = 'INSERT INTO public.timetable (user_id, day_use, month_use, start_time, ' \
                                                      'end_time, date_create, date_update) ' \
                        'VALUES (%s, %s, %s, %s, %s, %s::date, %s::date)'
                try:
                    cursor.execute(query, [self.get_user_id(message)[0], day_reg, month_reg,
                                           start_time, end_time, date_create, date_update])
                    connection.commit()

                    return True
                except:
                    return False

    # Изменение записи
    def update_timetable(self, row_id, new_data):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                print(new_data)
                query = 'UPDATE public.timetable SET day_use = %s, month_use = %s, start_time = %s, end_time = %s ' \
                        'WHERE id = %s'
                try:
                    cursor.execute(query, [int(new_data['day_reg']), int(new_data['month_reg']), new_data['start_time'],
                                           new_data['end_time'], row_id])
                    connection.commit()

                    return True
                except:
                    return False

    # Удаление записи (разрешено удалять только свои записи)
    def delete_from_timetable(self, time_id):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'DELETE FROM public.timetable WHERE id = %s'
                try:
                    cursor.execute(query, [time_id])
                    connection.commit()

                    return True
                except:
                    return False

    # Получить мои записи на переговорку
    def get_my_times(self, user_id):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT * FROM public.timetable WHERE user_id = %s'
                cursor.execute(query, [user_id])

                return cursor.fetchall()

    # Получить все записи на переговорку
    def get_all_times(self):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT public.users.*, public.timetable.* FROM public.timetable ' \
                        'INNER JOIN public.users ON public.users.id = public.timetable.user_id ' \
                        'WHERE (public.timetable.day_use >= %s AND public.month_use = %s) ' \
                        'OR (public.timetable.day_use < %s AND public.month_use > %s) '
                cursor.execute(query, [datetime.datetime.today().day, datetime.datetime.today().month,
                                       datetime.datetime.today().day, datetime.datetime.today().month])

                return cursor.fetchall()

    # Получить мои сегодняшние записи на переговорку
    def get_times_day(self, day):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT public.users.*, public.timetable.* FROM public.timetable ' \
                        'INNER JOIN public.users ON public.users.id = public.timetable.user_id WHERE day_use = %s'
                cursor.execute(query, [day])

                return cursor.fetchall()

    # Удалить все записи за прошедший день из БД
    def delete_old_times(self):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'DELETE FROM public.timetable WHERE day_use = %s AND month_use = %s'
                cursor.execute(query, [datetime.datetime.today().day, datetime.datetime.today().month])
                connection.commit()

    # Добавить запись в таблицу временных данных
    def add_self_database(self, user_id):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'INSERT INTO public.self_data (user_id) VALUES (%s)'
                cursor.execute(query, [user_id])
                connection.commit()

    # Удалить запись из таблицы временных данных
    def del_self_database(self, user_id):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'DELETE FROM public.self_data WHERE user_id = %s'
                cursor.execute(query, [user_id])
                connection.commit()

    # Добавить день потенциальной записи
    def set_day_reg(self, day_reg, user_id):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'UPDATE public.self_data SET day_reg = %s WHERE user_id = %s'
                cursor.execute(query, [day_reg, user_id])
                connection.commit()

    # Достать день потенциальной записи
    def get_day_reg(self, user_id):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT self_data.day_reg FROM public.self_data WHERE user_id = %s'
                cursor.execute(query, [user_id])

                return cursor.fetchone()[0]

    # Добавить месяц потенциальной записи
    def set_month_reg(self, month_reg, user_id):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'UPDATE public.self_data SET month_reg = %s WHERE user_id = %s'
                cursor.execute(query, [month_reg, user_id])
                connection.commit()

    # Достать месяц потенциальной записи
    def get_month_reg(self, user_id):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT self_data.month_reg FROM public.self_data WHERE user_id = %s'
                cursor.execute(query, [user_id])

                return cursor.fetchone()[0]

    # Добавить начальное время потенциальной записи
    def set_start_time(self, start_time, user_id):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'UPDATE public.self_data SET start_time = %s WHERE user_id = %s'
                cursor.execute(query, [start_time, user_id])
                connection.commit()

    # Достать начаотное время потенциальной записи
    def get_start_time(self, user_id):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT self_data.start_time FROM public.self_data WHERE user_id = %s'
                cursor.execute(query, [user_id])

                return cursor.fetchone()[0]

    # Добавить конечное время потенциальной записи
    def set_end_time(self, end_time, user_id):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'UPDATE public.self_data SET end_time = %s WHERE user_id = %s'
                cursor.execute(query, [end_time, user_id])
                connection.commit()

    # Достать конечное время потенциальной записи
    def get_end_time(self, user_id):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT self_data.end_time FROM public.self_data WHERE user_id = %s'
                cursor.execute(query, [user_id])

                return cursor.fetchone()[0]

    # Достать информацию о потенциальной записи
    def get_new_info(self, user_id):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT self_data.day_reg, self_data.month_reg, self_data.start_time, self_data.end_time ' \
                        'FROM public.self_data WHERE user_id = %s'
                cursor.execute(query, [user_id])

                return cursor.fetchone()

    # Добавить информацию удаляемой/изменяемой записи
    def set_last_info(self, last_info, user_id):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'UPDATE public.self_data SET last_func = %s, last_row_id = %s, last_day_reg = %s, ' \
                        'last_month_reg = %s, last_start_time = %s, last_end_time = %s ' \
                        'WHERE user_id = %s'
                cursor.execute(query, [last_info[0], last_info[1], last_info[2],
                                       last_info[3], last_info[4], last_info[5], user_id])
                connection.commit()

    # Добавить информацию удаляемой/изменяемой записи
    def get_last_info(self, user_id):
        with closing(self.get_connection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT self_data.last_func, self_data.last_row_id, self_data.last_day_reg, ' \
                        'self_data.last_month_reg, self_data.last_start_time, self_data.last_end_time ' \
                        'FROM public.self_data WHERE user_id = %s'
                cursor.execute(query, [user_id])

                return cursor.fetchone()

    # Связь с БД
    @staticmethod
    def get_connection():
        database_link = config.DATABASELINK

        db_info = dj_database_url.config(default=database_link)
        connection = psycopg2.connect(database=db_info.get('NAME'),
                                      user=db_info.get('USER'),
                                      password=db_info.get('PASSWORD'),
                                      host=db_info.get('HOST'),
                                      port=db_info.get('PORT'))

        return connection

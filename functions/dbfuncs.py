from datafiles import config
from contextlib import closing
import dj_database_url
import psycopg2
import datetime
import re


class DatabaseFuncs:

    def __init__(self, bot):
        self.bot = bot

    # Проверка данных о пользователе из БД на актуальность
    def checkUser(self, message):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT * FROM public.users WHERE user_id = %s'
                cursor.execute(query, [message.from_user.id])

                if cursor.rowcount > 0:
                    for row in cursor:
                        if not self.compareUserData(row, message):
                            self.updateUser(message)
                            return True
                else:
                    self.addUser(message)
                    return False

    # Сравнение старых и текущих данных о пользователе
    def compareUserData(self, old_user_data, new_user_data):
        for row in old_user_data:
            print(row)
        if str(old_user_data[1]).strip() != new_user_data.from_user.username:
            return False
        if str(old_user_data[2]).strip() != new_user_data.from_user.first_name:
            return False
        if str(old_user_data[3]).strip() != new_user_data.from_user.last_name:
            return False
        if str(old_user_data[5]).strip() != new_user_data.from_user.language_code:
            return False
        if str(old_user_data[7]).strip() != new_user_data.from_user.is_bot:
            return False

        return True

    # Добавить пользователя
    def addUser(self, message):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'INSERT INTO public.users (user_accname, user_firstname, user_lastname, user_id, user_chat_id, user_language, user_isbot) ' \
                        'VALUES (%s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(query,
                               [self.checkNone(message.from_user.username), self.checkNone(message.from_user.first_name), self.checkNone(message.from_user.last_name),
                                message.from_user.id, message.chat.id, str(message.from_user.language_code).strip(), message.from_user.is_bot])
                connection.commit()

    # Обновить данные о пользователе
    def updateUser(self, message):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'UPDATE public.users ' \
                        'SET user_accname = %s, user_firstname = %s, user_lastname = %s, user_id = %s, user_chat_id = %s, user_language = %s, user_isbot = %s ' \
                        'WHERE user_id = %s'
                cursor.execute(query,
                               [self.checkNone(message.from_user.username), self.checkNone(message.from_user.first_name), self.checkNone(message.from_user.last_name),
                                message.from_user.id, message.chat.id, str(message.from_user.language_code).strip(), message.from_user.is_bot, message.from_user.id])
                connection.commit()

    # Получить id пользователя по telegram_id (user_id)
    def getUserId(self, message):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT id FROM public.users WHERE user_id = %s'
                cursor.execute(query, [message.from_user.id])

                return cursor.fetchone()

    # Добавить запись на переговорку
    def addToTimetable(self, message, collection):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                start_time = self.checkTimeBefore(collection['start_time'])
                end_time = self.checkTimeBefore(collection['end_time'])
                day_reg = int(collection['day_reg'])
                month_reg = int(collection['month_reg'])
                date_create = datetime.datetime.today().date()
                date_update = date_create

                query = 'INSERT INTO public.timetable (user_id, day_use, month_use, start_time, end_time, date_create, date_update) ' \
                        'VALUES (%s, %s, %s, %s, %s, %s::date, %s::date)'
                cursor.execute(query, [self.getUserId(message)[0], day_reg, month_reg,
                                       start_time, end_time, date_create, date_update])
                connection.commit()

    # Удаление записи (разрешено удалять только свои записи)
    def deleteFromTimetable(self, time_id):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'DELETE FROM public.timetable WHERE id = %s'
                cursor.execute(query, [time_id])
                connection.commit()

    # Получить мои записи на переговорку
    def getMyTimes(self, user_id):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT * FROM public.timetable WHERE user_id = %s'
                cursor.execute(query, [user_id])

                return cursor.fetchall()

    # Получить мои сегодняшние записи на переговорку
    def getMyTimesToday(self, user_id, day):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT * FROM public.timetable WHERE user_id = %s AND day_use = %s'
                cursor.execute(query, [user_id, day])

                return cursor.fetchall()

    # Получить все записи на переговорку
    def getAllTimes(self):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT public.users.*, public.timetable.* FROM public.timetable ' \
                        'INNER JOIN public.users ON public.users.id = public.timetable.user_id'
                cursor.execute(query)

                return cursor.fetchall()

    # Получить все сегодняшние записи на переговорку
    def getAllTimesToday(self, day):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT public.users.*, public.timetable.* FROM public.timetable ' \
                        'INNER JOIN public.users ON public.users.id = public.timetable.user_id WHERE day_use = %s'
                cursor.execute(query, [day])

                return cursor.fetchall()

    # Удалить все записи за прошедший день из БД
    def deleteOldTimes(self):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'DELETE FROM public.timetable WHERE day_use = %s AND month_use = %s'
                cursor.execute(query, [datetime.datetime.today().day, datetime.datetime.today().month])
                connection.commit()

    # Замена None на пустую строку
    @staticmethod
    def checkNone(string):
        return '' if str(string).strip() == 'None' else str(string).strip()

    # Сортировка списка записей по времени по возрастанию
    @staticmethod
    def sortTimes(times_data, type_func):
        new_times_data = []
        print(times_data)

        if type_func == 1:
            new_times_data = sorted(times_data, key=lambda row: (row[2], row[4], row[3]), reverse=False)
        elif type_func == 2:
            new_times_data = sorted(times_data, key=lambda row: (row[10], row[12], row[11]), reverse=False)

        return new_times_data

    # Преобразование к формату ЦЦ:ЦЦ
    @staticmethod
    def checkTimeBefore(data_time):
        if len(data_time) == 5:
            if re.match(r'^[0-9]{0,2}(:|\s)[0-9]{2}$', data_time):
                return data_time.replace(' ', ':')
            return data_time
        elif len(data_time) == 4:
            if re.match(r'^[0-9]{0,2}(:|\s)[0-9]{2}$', data_time):
                return '0' + data_time.replace(' ', ':')
            return '0' + data_time
        elif len(data_time) == 2:
            return data_time + ':00'
        elif len(data_time) == 1:
            return '0' + data_time + ':00'

    # Связь с БД
    @staticmethod
    def getConnection():
        database_link = config.DATABASELINK

        db_info = dj_database_url.config(default=database_link)
        connection = psycopg2.connect(database=db_info.get('NAME'),
                                      user=db_info.get('USER'),
                                      password=db_info.get('PASSWORD'),
                                      host=db_info.get('HOST'),
                                      port=db_info.get('PORT'))

        return connection

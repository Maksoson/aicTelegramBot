import config
from contextlib import closing
import dj_database_url
import psycopg2
import datetime
import re


class DatabaseFuncs:

    def __init__(self, bot):
        self.bot = bot

    def createUsersTable(self):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = """CREATE TABLE public.users ( id SERIAL PRIMARY KEY,
                          user_accname character(90) DEFAULT NULL,
                          user_firstname character(90) DEFAULT NULL,
                          user_lastname character(90) DEFAULT NULL,
                          user_id integer NOT NULL,
                          user_language character(20) DEFAULT NULL,
                          user_rank character(45) NOT NULL DEFAULT 'Beginner',
                          user_isbot boolean NOT NULL );
                        """

                cursor.execute(query)

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

    def compareUserData(self, old_user_data, new_user_data):
        if old_user_data[1] != new_user_data.from_user.username:
            return False
        if old_user_data[2] != new_user_data.from_user.first_name:
            return False
        if old_user_data[3] != new_user_data.from_user.last_name:
            return False
        if old_user_data[5] != new_user_data.from_user.language_code:
            return False
        if old_user_data[7] != new_user_data.from_user.is_bot:
            return False

        return True

    def addUser(self, message):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'INSERT INTO public.users (user_accname, user_firstname, user_lastname, user_id, user_language, user_isbot) ' \
                        'VALUES (%s, %s, %s, %s, %s, %s)'
                cursor.execute(query,
                               (self.checkNone(message.from_user.username), self.checkNone(message.from_user.first_name), self.checkNone(message.from_user.last_name),
                                message.from_user.id, message.from_user.language_code, message.from_user.is_bot))
                connection.commit()

    def updateUser(self, message):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'UPDATE public.users ' \
                        'SET user_accname = %s, user_firstname = %s, user_lastname = %s, user_id = %s, user_language = %s, user_isbot = %s'
                cursor.execute(query,
                               (self.checkNone(message.from_user.username), self.checkNone(message.from_user.first_name), self.checkNone(message.from_user.last_name),
                                message.from_user.id, message.from_user.language_code, message.from_user.is_bot))
                connection.commit()

    def getUserId(self, message):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT id FROM public.users WHERE user_id = %s'
                cursor.execute(query, [message.from_user.id])

                return cursor.fetchone()

    def addToTimetable(self, message, collection):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                start_time = self.checkTimeBefore(collection['start_time'])
                end_time = self.checkTimeBefore(collection['end_time'])
                date_create = datetime.datetime.today().date()
                date_update = date_create

                query = 'INSERT INTO public.timetable (user_id, day_use, start_time, end_time, date_create, date_update) ' \
                        'VALUES (%s, %s, %s, %s, %s::date, %s::date)'
                cursor.execute(query, [self.getUserId(message)[0], datetime.datetime.today().day,
                                       start_time, end_time, date_create, date_update])
                connection.commit()

    def getMyTimes(self, user_id, day):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT * FROM public.timetable WHERE user_id = %s AND day_use = %s'
                cursor.execute(query, [user_id, day])

                return cursor.fetchall()

    def getAllTimes(self, day):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT public.users.*, public.timetable.* FROM public.timetable ' \
                        'INNER JOIN public.users ON public.users.id = public.timetable.user_id WHERE day_use = %s'
                cursor.execute(query, [day])

                return cursor.fetchall()

    def deleteOldTimes(self):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'DELETE FROM public.timetable WHERE day_use = %s'
                cursor.execute(query, [datetime.datetime.today().day])
                connection.commit()

    @staticmethod
    def checkNone(string):
        return '' if str(string).strip() == 'None' else str(string).strip()

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

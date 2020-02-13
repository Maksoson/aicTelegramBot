import config
from contextlib import closing
import dj_database_url
import psycopg2
import datetime
import time


class DatabaseFuncs:

    def __init__(self, bot):
        self.bot = bot

    def createUsersTable(self, message):
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
                self.bot.send_message(message.chat.id, "success")

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

    def compareUserData(self, old_userdata, new_userdata):
        if old_userdata[1] != new_userdata.from_user.username:
            return False
        if old_userdata[2] != new_userdata.from_user.first_name:
            return False
        if old_userdata[3] != new_userdata.from_user.last_name:
            return False
        if old_userdata[5] != new_userdata.from_user.language_code:
            return False
        if old_userdata[7] != new_userdata.from_user.is_bot:
            return False

        return True

    def addUser(self, message):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'INSERT INTO public.users (user_accname, user_firstname, user_lastname, user_id, user_language, user_isbot) ' \
                        'VALUES (%s, %s, %s, %s, %s, %s)'
                cursor.execute(query,
                               (message.from_user.username, message.from_user.first_name, message.from_user.last_name,
                                message.from_user.id, message.from_user.language_code, message.from_user.is_bot))
                connection.commit()

    def updateUser(self, message):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'UPDATE public.users ' \
                        'SET user_accname = %s, user_firstname = %s, user_lastname = %s, user_id = %s, user_language = %s, user_isbot = %s'
                cursor.execute(query,
                               (message.from_user.username, message.from_user.first_name, message.from_user.last_name,
                                message.from_user.id, message.from_user.language_code, message.from_user.is_bot))
                connection.commit()

    def getUserId(self, message):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT id FROM public.users WHERE user_id = %s'
                cursor.execute(query, [message.from_user.id])

    def addToTimetable(self, collection, message):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'INSERT INTO public.timetable (user_id, day_use, start_time, end_time, date_create, date_update) ' \
                        'VALUES (%s, %s, %s, %s, %s, %s)'
                date_create = time.time()
                date_update = date_create
                cursor.execute(query, (self.getUserId(message), datetime.datetime.today().day,
                                       collection['start_time'], collection['end_time'],
                                       date_create, date_update))
                connection.commit()

    def getAllTimes(self, day):
        with closing(self.getConnection()) as connection:
            with connection.cursor() as cursor:
                query = 'SELECT * FROM public.timetable WHERE day_use = %s'
                result = cursor.execute(query, [day])
                connection.commit()

                return result

    @staticmethod
    def getConnection():
        databaselink = config.DATABASELINK

        db_info = dj_database_url.config(default=databaselink)
        connection = psycopg2.connect(database=db_info.get('NAME'),
                                      user=db_info.get('USER'),
                                      password=db_info.get('PASSWORD'),
                                      host=db_info.get('HOST'),
                                      port=db_info.get('PORT'))

        return connection

import telebot
import datetime
import config
import os
from contextlib import closing
import pymysql
from pymysql.cursors import DictCursor
from flask import Flask, request
import logging
import dj_database_url
import psycopg2


bot = telebot.TeleBot(config.TOKEN)
start_keyboard = telebot.types.ReplyKeyboardMarkup(True)
start_keyboard.row('Занять переговорную', 'Вывести список занятости')
start_keyboard.row('Время', 'День')
start_keyboard.row('Регистрация', 'Помощь')

name = ''
surname = ''
age = 0


@bot.message_handler(commands=['start', 'help'])
def sendWelcome(message):
    # checkUser(message)
    addUsersTable(message)
    bot.send_message(message.chat.id, 'Привет , ' + message.from_user.username + ' (:')


def addUsersTable(message):
    with closing(getConnection()) as connection:
        with connection.cursor() as cursor:
            query = """CREATE TABLE IF NOT EXISTS users ( id serial,
                      user_accname varchar(90) DEFAULT NULL,
                      user_firstname varchar(90) DEFAULT NULL,
                      user_lastname varchar(90) DEFAULT NULL,
                      user_id integer NOT NULL,
                      user_language varchar(20) DEFAULT NULL,
                      user_rank varchar(45) NOT NULL DEFAULT 'Beginner',
                      user_isbot boolean NOT NULL,
                      PRIMARY KEY (id) );
                    """

            cursor.execute(query)
            bot.send_message(message.chat.id, "success")


def checkUser(message):
    with closing(getConnection()) as connection:
        with connection.cursor() as cursor:
            query = 'SELECT * FROM aicroboticsbot.users WHERE user_id = %s'
            cursor.execute(query, message.from_user.id)

            if cursor.rowcount > 0:
                for row in cursor:
                    if not compareUserData(row, message):
                        updateUser(message)
            else:
                addUser(message)


def compareUserData(old_userdata, new_userdata):
    if old_userdata['user_accname'] != new_userdata.from_user.username:
        return False
    if old_userdata['user_firstname'] != new_userdata.from_user.first_name:
        return False
    if old_userdata['user_lastname'] != new_userdata.from_user.last_name:
        return False
    if old_userdata['user_language'] != new_userdata.from_user.language_code:
        return False
    if old_userdata['user_isbot'] != new_userdata.from_user.is_bot:
        return False

    return True


def addUser(message):
    with closing(getConnection()) as connection:
        with connection.cursor() as cursor:
            query = 'INSERT INTO aicroboticsbot.users (user_accname, user_firstname, user_lastname, user_id, user_language, user_isbot) ' \
                    'VALUES (%s, %s, %s, %s, %s, %s)'
            cursor.execute(query, (message.from_user.username, message.from_user.first_name, message.from_user.last_name,
                                   message.from_user.id, message.from_user.language_code, message.from_user.is_bot))
            connection.commit()


def updateUser(message):
    with closing(getConnection()) as connection:
        with connection.cursor() as cursor:
            query = 'UPDATE aicroboticsbot.users ' \
                    'SET user_accname = %s, user_firstname = %s, user_lastname = %s, user_id = %s, user_language = %s, user_isbot = %s'
            cursor.execute(query, (message.from_user.username, message.from_user.first_name, message.from_user.last_name,
                                   message.from_user.id, message.from_user.language_code, message.from_user.is_bot))
            connection.commit()


def get_name(message):
    global name
    name = message.text
    bot.send_message(message.from_user.id, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(message, get_surname)


def get_surname(message):
    global surname
    surname = message.text
    bot.send_message(message.from_user.id, 'Сколько тебе лет?')
    bot.register_next_step_handler(message, get_age)


def get_age(message):
    global age
    age = message.text
    keyboard = telebot.types.InlineKeyboardMarkup(True)
    key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    question = 'Тебе ' + str(age) + ' лет, тебя зовут ' + name + ' ' + surname + '?'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def send_text(message):
    print(message)
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет, ' + message.from_user.first_name)
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'Прощай, ' + message.from_user.first_name)
    elif message.text.lower() == 'я тебя люблю':
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAO2Xj1y-l94-VPFiR-cso1Jy9R_QE0AAt8DAAKJ6uUHt_QHFuQiXjgYBA')
    elif message.text.lower() == 'время':
        now = datetime.datetime.now()
        bot.send_message(message.chat.id, 'Текущее время - ' + str(now.hour) + ':' + str(now.minute))
    elif message.text.lower() == 'регистрация':
        bot.send_message(message.from_user.id, "Как тебя зовут?")
        bot.register_next_step_handler(message, get_name)


@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":
        bot.send_message(call.message.chat.id, 'Запомню :)')
    elif call.data == "no":
        bot.send_message(call.message.chat.id, "Повтори, как тебя зовут?")
        bot.register_next_step_handler(call.message, get_name)


def getConnection():
#     connection = pymysql.connect(
#         host=config.DBHOST,
#         user=config.DBUSER,
#         password=config.DBPASSWORD,
#         db=config.DBNAME,
#         charset=config.DBCHARSET,
#         cursorclass=DictCursor
#     )
    DATABASELINK = config.DATABASELINK

    db_info = dj_database_url.config(default=DATABASELINK)
    connection = psycopg2.connect(database=db_info.get('NAME'),
                        user=db_info.get('USER'),
                        password=db_info.get('PASSWORD'),
                        host=db_info.get('HOST'),
                        port=db_info.get('PORT'))

    return connection


server = Flask(__name__)


@server.route("/{}".format(config.TOKEN), methods=['POST'])
def getMessage():
    update = bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode('utf-8'))])

    return "!", 200


@server.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    bot.remove_webhook()
    s = bot.set_webhook('{URL}{HOOK}'.format(URL=config.URL, HOOK=config.TOKEN))
    if s:
        return "webhook setup ok", 200
    else:
        return "webhook setup failed", 200


@server.route('/')
def index():
    return '.'


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

import telebot
import datetime
import config
import os
import bothome
from flask import Flask, request

from functions import dbfuncs, botfuncs


bot = telebot.TeleBot(config.TOKEN)
bot_home = bothome.BotHome()
bot_home.setBot(bot)

db_funcs = dbfuncs.DatabaseFuncs(bot)
bot_funcs = botfuncs.BotFuncs(bot)

start_keyboard = telebot.types.ReplyKeyboardMarkup(True)
start_keyboard.row('Занять переговорку', 'Моя занятость', 'Удалить запись')
start_keyboard.row('Занятость переговорки на сегодня')
start_keyboard.row('Дата', 'Справка')
bot_home.setKeyboard(start_keyboard)


# ------------------------------------------------ #
@bot.message_handler(commands=['start'])
def startFunc(message):
    if db_funcs.checkUser(message):
        bot.send_message(message.chat.id, 'Я тебя знаю , ' + message.from_user.username + ' (:',
                         reply_markup=start_keyboard)
    else:
        bot.send_message(message.chat.id, 'Привет, ' + message.from_user.username + '!\n'
                                          'Я - бот компании Russian Robotics, предназначенный для ведения расписания переговорки!\n\n'
                                          'Нажми на "Справка" или введи /help, чтобы увидеть мои возможности (:\n'
                                          'Надеюсь тебе понравится со мной работать!\n\n', reply_markup=start_keyboard)
        bot_funcs.printHelp(message)


@bot.message_handler(commands=['help'])
def pleaseHelp(message):
    db_funcs.checkUser(message)
    bot_funcs.printHelp(message)


@bot.message_handler(commands=['add'])
def addUserTime(message):
    bot_funcs.regTime(message)


@bot.message_handler(commands=['time'])
def printTime(message):
    bot_funcs.printToday(message.chat.id, datetime.datetime.today())


@bot.message_handler(commands=['all'])
def printAll(message):
    bot_funcs.printAllTimes(message, datetime.datetime.today())


@bot.message_handler(commands=['delete'])
def deleteTime(message):
    bot_funcs.seeTimesListFor(message, datetime.datetime.today(), 1)


# @bot.message_handler(commands=['update'])
# def updateTime(message):
#     bot_funcs.seeTimesListFor(message, datetime.datetime.today(), 2)


@bot.message_handler(commands=['my'])
def printAllMy(message):
    bot_funcs.printMyTimes(message, datetime.datetime.today())


@bot.message_handler(commands=['update, cat'])
def deleteUserTime(message):
    bot.send_message(message.chat.id, 'Эта функция пока что не доступна :(')


@bot.message_handler(regexp='((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)')
def command_url(message):
    bot.reply_to(message, "По ссылкам, пока что, переходить я не умею :(")


@bot.message_handler(content_types=['text'])
def send_text(message):
    print(message)

    user_message = message.text.lower()
    chat_id = message.chat.id
    user_first_name = message.from_user.first_name
    today = datetime.datetime.today()
    now_day = today.day

    if user_message == 'привет':
        bot.send_message(chat_id, 'Привет, ' + user_first_name)
    elif user_message == 'пока':
        bot.send_message(chat_id, 'Удачи тебе, ' + user_first_name)
    elif user_message == 'дата':
        bot_funcs.printToday(chat_id, today)
    elif user_message == 'моя занятость':
        bot_funcs.printMyTimes(message, today)
    elif user_message == 'удалить запись':
        bot_funcs.seeTimesListFor(message, datetime.datetime.today(), 1)
    elif user_message == 'занять переговорку':
        bot_funcs.regTime(message)
    elif user_message == 'занятость переговорки на сегодня':
        bot_funcs.printAllTimes(message, today)
    elif user_message == 'справка':
        db_funcs.checkUser(message)
        bot_funcs.printHelp(message)


@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(message)


def deleteOldTimes():
    db_funcs.deleteOldTimes()


# ------------------------------------------------ #
server = Flask(__name__)


@server.route("/{}".format(config.TOKEN), methods=['POST'])
def getMessage():
    updates = bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode('utf-8'))])
    print(updates)

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


# ------------------------------------------------ #
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

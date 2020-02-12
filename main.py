import telebot
import datetime
import config
import os
from flask import Flask, request

from functions import dbfuncs, botfuncs

bot = telebot.TeleBot(config.TOKEN)
db_funcs = dbfuncs.DatabaseFuncs(bot)
botfuncs = botfuncs.BotFuncs(bot)

start_keyboard = telebot.types.ReplyKeyboardMarkup(True)
start_keyboard.row('Занять переговорную', 'Моя занятость')
start_keyboard.row('Вывести общий список занятости')
start_keyboard.row('Мои данные', 'Дата', 'Помощь')


# ------------------------------------------------ #
@bot.message_handler(commands=['start'])
def startFunc(message):
    if db_funcs.checkUser(message):
        bot.send_message(message.chat.id, 'Я тебя знаю , ' + message.from_user.username + ' (:', reply_markup=start_keyboard)
    else:
        bot.send_message(message.chat.id, 'Добро пожаловать, ' + message.from_user.username + '. Располагайся как дома! (:', reply_markup=start_keyboard)


@bot.message_handler(commands=['help'])
def pleaseHelp(message):
    db_funcs.checkUser(message)
    bot.send_message(message.chat.id, 'Вас приветствует компания AIC Robotics!\n\n'
                                      'Данный бот предназначен для бронирования расписания переговорки.\n'
                                      'На клавиатуре представлен весь функционал.\n'
                                      'Приятного использования!\n\n')


@bot.message_handler(regexp='((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)')
def command_url(message):
    bot.reply_to(message, "I shouldn't open that url, should I?")


@bot.message_handler(content_types=['text'])
def send_text(message):
    print(message)
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет, ' + message.from_user.first_name)
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'Прощай, ' + message.from_user.first_name)
    # elif message.text.lower() == 'я тебя люблю':
    #     bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAO2Xj1y-l94-VPFiR-cso1Jy9R_QE0AAt8DAAKJ6uUHt_QHFuQiXjgYBA')
    elif message.text.lower() == 'время':
        bot.send_message(message.chat.id, 'Текущее время:\n' + str(datetime.datetime.today().strftime("%H:%M - %d.%m.%Y")))
    elif message.text.lower() == 'занять переговорную':
        botfuncs.regTime(message)
    # elif message.text.lower() == 'регистрация':
    #     bot.send_message(message.from_user.id, "Как тебя зовут?")
    #     bot.register_next_step_handler(message, botfuncs.get_name)


@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(message)


# @bot.callback_query_handler(func=lambda call: True)
# def callback_worker(call):
#     if call.data == "yes":
#         bot.send_message(call.message.chat.id, 'Запомню :)')
#     elif call.data == "no":
#         bot.send_message(call.message.chat.id, "Повтори, как тебя зовут?")
#         bot.register_next_step_handler(call.message, botfuncs.get_name)


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

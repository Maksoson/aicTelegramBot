#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
import datetime
from datafiles import config
import os
import bothome
from flask import Flask, request

from functions import dbfuncs, botfuncs, otherfuncs


bot = telebot.TeleBot(config.TOKEN)
bot_home = bothome.BotHome()
bot_home.set_bot(bot)

db_funcs = dbfuncs.DatabaseFuncs(bot)
bot_funcs = botfuncs.BotFuncs(bot)
other_funcs = otherfuncs.OtherFuncs()


# ------------------------------------------------ #
@bot.message_handler(commands=['start', 'help', 'add', 'time', 'all', 'my', 'delete', 'update', 'cat'])
def start_func(message):
    if bot_funcs.is_user_exist(message):
        command = str(message.text).strip()
        if command == '/start':
            user_name = other_funcs.check_none(message.from_user.username)
            user_name = ', ' + user_name if user_name != '' else '!'
            bot.send_message(message.chat.id, 'Я тебя уже знаю' + user_name,
                             reply_markup=other_funcs.get_start_keyboard())
        elif command == '/help':
            bot_funcs.print_help(message)
        elif command == '/add':
            bot_funcs.reg_time(message)
        elif command == '/time':
            bot_funcs.print_today(message.chat.id, datetime.datetime.today())
        elif command == '/all':
            bot_funcs.print_all_times(message)
        elif command == '/delete':
            bot_funcs.see_times_list_for(message, 1)
        elif command == '/update':
            bot_funcs.see_times_list_for(message, 2)
        elif command == '/my':
            bot_funcs.print_my_times(message)
        elif command == '/cat':
            bot.send_message(message.chat.id, 'Мяу', reply_markup=other_funcs.get_start_keyboard())


@bot.message_handler(content_types=['text'])
def send_text(message):
    print(message)
    if bot_funcs.is_user_exist(message):
        user_message = message.text.lower()
        chat_id = message.chat.id
        today = datetime.datetime.today()

        if user_message == 'дата':
            bot_funcs.print_today(chat_id, today)
        elif user_message == 'моя занятость':
            bot_funcs.print_my_times(message)
        elif user_message == 'удалить запись':
            bot_funcs.see_times_list_for(message, 1)
        elif user_message == 'изменить запись':
            bot_funcs.see_times_list_for(message, 2)
        elif user_message == 'занять переговорку':
            bot_funcs.reg_time(message)
        elif user_message == 'занятость переговорки':
            bot_funcs.print_all_times(message)
        elif user_message == 'справка':
            bot_funcs.print_help(message)
        elif user_message == 'кот':
            bot.send_message(message.chat.id, 'Мяу', reply_markup=other_funcs.get_start_keyboard())


bot.polling(interval=2, none_stop=True)

# # ------------------------------------------------ #
# server = Flask(__name__)
#
#
# @server.route("/{}".format(config.TOKEN), methods=['POST'])
# def get_message():
#     updates = bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode('utf-8'))])
#     print(updates)
#
#     return "!", 200
#
#
# @server.route('/setwebhook', methods=['GET', 'POST'])
# def set_web_hook():
#     bot.remove_webhook()
#     s = bot.set_webhook('{URL}{HOOK}'.format(URL=config.URL, HOOK=config.TOKEN))
#     if s:
#         return "web_hook setup ok", 200
#     else:
#         return "web_hook setup failed", 200
#
#
# @server.route('/')
# def index():
#     return '.'
#
#
# # ------------------------------------------------ #
# if __name__ == "__main__":
#     server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

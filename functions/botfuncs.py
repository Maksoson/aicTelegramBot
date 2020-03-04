#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from datetime import datetime
import calendar
import telebot
import bothome
import time
from emoji import emojize
from datafiles import config
from functions import dbfuncs, otherfuncs


class BotFuncs:

    def __init__(self, bot):
        self.bot = bot
        self.db_funcs = dbfuncs.DatabaseFuncs(self.bot)
        self.other_funcs = otherfuncs.OtherFuncs()
        self.bot_home = bothome.BotHome()

        self.added_days = []
        self.day_names = ['(пн)', '(вт)', '(ср)', '(чт)', '(пт)', '(сб)', '(вск)']
        self.days_dict = {}

        self.error = emojize("❌", use_aliases=True)
        self.success = emojize("✅", use_aliases=True)
        self.pushpin = emojize("📌", use_aliases=True)
        self.memo = emojize("📝", use_aliases=True)
        self.interrobang = emojize("⁉", use_aliases=True)
        self.minus = emojize("➖", use_aliases=True)
        self.plus = emojize("➕", use_aliases=True)
        self.rupor_head = emojize("🗣", use_aliases=True)

    # Стартовый диалог
    def is_user_exist(self, message):
        if self.db_funcs.check_user(message):
            return True
        else:
            self.bot.send_message(message.chat.id, self.get_hello_part(message.from_user.username) +
                               'Пожалуйста, введи секретное слово, чтобы начать пользоваться моими возможностями :)')
            self.bot.register_next_step_handler(message, self.validate_secret_word)

    # Проверка секретного слова
    def validate_secret_word(self, message):
        secret_word = str(message.text).strip()
        if secret_word == config.SECRET_WORD:
            if self.db_funcs.add_user(message):
                self.bot.send_message(message.chat.id, self.get_hello_part(message.from_user.username) +
                                        'Я - бот компании Russian Robotics, предназначенный для ведения расписания переговорки!\n\n'
                                        'Нажми на "Справка" или введи /help, чтобы увидеть мои возможности (:\n'
                                        'Надеюсь тебе понравится со мной работать!\n\n',
                                        reply_markup=self.other_funcs.get_start_keyboard())
                self.print_help(message)
        else:
            self.bot.send_message(message.chat.id,  self.error + ' Ты ввел неверное секретное слово. Попробуй снова')
            self.bot.register_next_step_handler(message, self.validate_secret_word)

    # Записи за выбранный день
    def get_day_list(self, message):
        day_reg = self.db_funcs.get_day_reg(message.from_user.id)
        data = self.other_funcs.sort_times(self.db_funcs.get_times_day(int(day_reg)), 2)
        counter = 1
        result_list = self.memo + ' '
        now_day = str(self.other_funcs.check_date_format(day_reg))
        now_month = str(self.other_funcs.check_date_format(self.db_funcs.get_month_reg(message.from_user.id)))
        if len(data) > 0:
            for row in data:
                if counter == 1:
                    result_list += 'Занятость на ' + now_day + '.' + now_month + '.' + \
                                   str(datetime.today().year) + ' ' + self.days_dict[now_day] + ':\n\n'
                result_list += str(counter) + '. ' + row[13] + ' - ' + row[14] + '  ---  ' \
                               + row[2] + ' ' + row[3] + ' (@' + row[1] + ')\n'
                counter += 1
            result_list += '\n'
        else:
            result_list += 'Занятость на ' + now_day + '.' + now_month + '.' + \
                                   str(datetime.today().year) + ' ' + self.days_dict[now_day] + ':\n\n'
            result_list += 'Список пуст\n\n'

        return result_list

    # Занять переговорку (следующие 4 функции)
    def reg_time(self, message):
        self.db_funcs.add_self_database(message.from_user.id)
        self.get_days_data()
        self.bot.send_message(message.chat.id, 'Выбери или введи день из предложенных:',
                              reply_markup=self.get_days_keyboard())
        self.bot.register_next_step_handler(message, self.reg_day_time)

    def reg_day_time(self, message):
        if message.text.lower().strip() != 'отмена':
            day_reg = str(message.text[0:2]).strip()
            if not re.match(r'^[0-9]{1,2}$', day_reg.lower()):
                self.bot.send_message(message.chat.id, self.error + ' Неверно, выбери снова:',
                                      reply_markup=self.get_days_keyboard())
                self.bot.register_next_step_handler(message, self.reg_day_time)
                return
            if int(day_reg) in self.added_days:
                if int(day_reg) < datetime.today().day:
                    if datetime.today().month != 12:
                        month_reg = str(datetime.today().month + 1)
                    else:
                        month_reg = '1'
                else:
                    month_reg = str(datetime.today().month)

                self.db_funcs.set_day_reg(day_reg, message.from_user.id)
                self.db_funcs.set_month_reg(month_reg, message.from_user.id)
                day_list = self.get_day_list(message)
                self.bot.send_message(message.chat.id, day_list + 'Во сколько тебе нужна переговорка?',
                                      reply_markup=self.other_funcs.get_cancel_button())
                self.bot.register_next_step_handler(message, self.reg_start_time)
            else:
                self.bot.send_message(message.chat.id, self.error + ' Неверно, выбери снова',
                                      reply_markup=self.get_days_keyboard())
                self.bot.register_next_step_handler(message, self.reg_day_time)
        else:
            self.db_funcs.del_self_database(message.from_user.id)
            self.bot.send_message(message.chat.id, 'Ввод отменен', reply_markup=self.other_funcs.get_start_keyboard())

    def reg_start_time(self, message):
        self.db_funcs.set_start_time('', message.from_user.id)
        start_time = str(message.text).strip()
        if start_time.lower() != 'отмена':
            if not re.match(r'^[0-9]{0,2}(:|\s)[0-9]{2}$', start_time.lower()):
                if not re.match(r'^[0-9]{1,2}$', start_time.lower()):
                    self.bot.send_message(message.chat.id, self.error + ' Неверные данные, повтори ввод',
                                          reply_markup=self.other_funcs.get_cancel_button())
                    self.bot.register_next_step_handler(message, self.reg_start_time)
                    return

            start_time = self.other_funcs.check_time_before(start_time)
            if not self.other_funcs.check_time_before(start_time):
                self.bot.send_message(message.chat.id, self.error + ' Неверные данные, повтори ввод',
                                      reply_markup=self.other_funcs.get_cancel_button())
                self.bot.register_next_step_handler(message, self.reg_start_time)
                return

            intersection_times = self.check_times_intersection(message, self.db_funcs.get_day_reg(message.from_user.id),
                                                               self.db_funcs.get_month_reg(message.from_user.id),
                                                               start_time)
            if len(intersection_times) > 0:
                answer = self.error + ' Твое время пересекается с:\n\n'
                counter = 1
                for row in intersection_times:
                    answer += str(counter) + '. ' + row[13] + ' - ' + row[14] + '  ---  ' \
                              + row[2] + ' ' + row[3] + ' (@' + row[1] + ')\n'
                    counter += 1
                answer += '\nПовтори ввод'
                self.bot.send_message(message.chat.id, answer)
                self.bot.register_next_step_handler(message, self.reg_start_time)
                return

            self.db_funcs.set_start_time(start_time, message.from_user.id)
            self.bot.send_message(message.chat.id, 'До скольки тебе нужна переговорка?')
            self.bot.register_next_step_handler(message, self.end_reg_time)
        else:
            self.db_funcs.del_self_database(message.from_user.id)
            self.bot.send_message(message.chat.id, 'Ввод отменен', reply_markup=self.other_funcs.get_start_keyboard())

    def end_reg_time(self, message):
        end_time = str(message.text).strip()
        if end_time.lower() != 'отмена':
            if not re.match(r'^[0-9]{0,2}(:|\s)[0-9]{2}$', end_time.lower()):
                if not re.match(r'^[0-9]{1,2}$', end_time.lower()):
                    self.bot.send_message(message.chat.id, self.error + ' Неверные данные, повтори ввод')
                    self.bot.register_next_step_handler(message, self.end_reg_time)
                    return
            end_time = self.other_funcs.check_time_before(end_time)
            if not self.other_funcs.check_time_before(end_time):
                self.bot.send_message(message.chat.id, self.error + ' Неверные данные, повтори ввод',
                                      reply_markup=self.other_funcs.get_cancel_button())
                self.bot.register_next_step_handler(message, self.reg_start_time)
                return
            start_time = self.db_funcs.get_start_time(message.from_user.id)
            day_reg = self.db_funcs.get_day_reg(message.from_user.id)
            month_reg = self.db_funcs.get_month_reg(message.from_user.id)
            if end_time > start_time:
                intersection_times = self.check_times_intersection(message, day_reg, month_reg, end_time)
                if len(intersection_times) > 0:
                    answer = self.error + ' Твое время пересекается с:\n\n'
                    counter = 1
                    for row in intersection_times:
                        answer += str(counter) + '. ' + row[13] + ' - ' + row[14] + '  ---  ' \
                                  + row[2] + ' ' + row[3] + ' (@' + row[1] + ')\n'
                        counter += 1
                    answer += '\nПовтори ввод'
                    self.bot.send_message(message.chat.id, answer)
                    self.bot.register_next_step_handler(message, self.reg_start_time)
                    return

                self.added_days = []
                self.db_funcs.set_end_time(end_time, message.from_user.id)
                data_reg = {'day_reg': day_reg, 'month_reg': month_reg, 'start_time': start_time, 'end_time': end_time}
                last_info = self.db_funcs.get_last_info(message.from_user.id)
                if last_info[0] == 'update':
                    row_id = int(last_info[1])
                    last_day = str(self.other_funcs.check_date_format(last_info[2]))
                    last_month = str(self.other_funcs.check_date_format(last_info[3]))
                    start_time = str(self.other_funcs.check_time_before(last_info[4]))
                    end_time = str(self.other_funcs.check_time_before(last_info[5]))
                    if self.db_funcs.update_timetable(row_id, data_reg):
                        self.bot.send_message(message.chat.id,
                                              self.success + ' Запись успешно перенесена:\n\n' + self.minus + ' '
                                              + start_time + ' - ' + end_time + ', ' + last_day + '.' + last_month + ' '
                                              + self.days_dict[last_day] + '\n\n' + self.plus + ' '
                                              + data_reg['start_time'] + ' - ' + data_reg['end_time'] +
                                              ' ' + str(self.other_funcs.check_date_format(data_reg['day_reg'])) + '.'
                                              + str(self.other_funcs.check_date_format(data_reg['month_reg'])) + ' '
                                              + self.days_dict[str(self.other_funcs.check_date_format(data_reg['day_reg']))],
                                              reply_markup=self.other_funcs.get_start_keyboard())
                    else:
                        self.bot.send_message(message.chat.id, self.interrobang +
                                              ' Запись не изменена! Произошла ошибка. Попробуй позже',
                                              reply_markup=self.other_funcs.get_start_keyboard())
                        self.db_funcs.del_self_database(message.from_user.id)
                        return
                else:
                    if self.db_funcs.add_to_timetable(message, data_reg):
                        self.bot.send_message(message.chat.id, self.success + ' Записал тебя на:\n\n' + self.plus + ' '
                                              + data_reg['start_time'] + " - " + data_reg['end_time'] + ", "
                                              + str(self.other_funcs.check_date_format(data_reg['day_reg']))
                                              + '.' + str(self.other_funcs.check_date_format(data_reg['month_reg'])) + ' ' +
                                              self.days_dict[str(self.other_funcs.check_date_format(data_reg['day_reg']))],
                                              reply_markup=self.other_funcs.get_start_keyboard())
                    else:
                        self.bot.send_message(message.chat.id, self.interrobang +
                                              ' Запись не добавлена! Произошла ошибка. Попробуй позже',
                                              reply_markup=self.other_funcs.get_start_keyboard())
                        self.db_funcs.del_self_database(message.from_user.id)
                        return
                self.send_timetable_news(message)
            else:
                self.bot.send_message(message.chat.id, self.error + ' Повтори ввод')
                self.bot.register_next_step_handler(message, self.end_reg_time)
        else:
            self.db_funcs.del_self_database(message.from_user.id)
            self.bot.send_message(message.chat.id, 'Ввод отменен', reply_markup=self.other_funcs.get_start_keyboard())

    # Рассылка о добавленной записи
    def send_timetable_news(self, message):
        chat_ids = self.db_funcs.get_all_chat_ids()
        user_data = self.db_funcs.get_user(message)
        last_info = self.db_funcs.get_last_info(message.from_user.id)

        print(last_info)
        if last_info[0] != 'delete':
            new_info = self.db_funcs.get_new_info(message.from_user.id)
            day_reg = str(self.other_funcs.check_date_format(new_info[0]))
            month_reg = str(self.other_funcs.check_date_format(new_info[1]))
            start_time = new_info[2]
            end_time = new_info[3]

        self.db_funcs.del_self_database(message.from_user.id)

        if last_info[0] in ['update', 'delete']:
            last_day = str(self.other_funcs.check_date_format(last_info[2]))
            last_month = str(self.other_funcs.check_date_format(last_info[3]))
            last_start_time = str(self.other_funcs.check_time_before(last_info[4]))
            last_end_time = str(self.other_funcs.check_time_before(last_info[5]))

        for chat_id in chat_ids:
            if chat_id[0] != message.chat.id:
                try:
                    time.sleep(0.5)
                    if last_info[0] == 'update':
                        self.bot.send_message(chat_id[0], self.rupor_head + ' Пользователь ' + user_data[2] + ' ' +
                                              user_data[3] + ' (@' + user_data[1] + ') перенес запись:\n\n' + self.minus
                                              + ' ' + last_start_time + ' - ' + last_end_time + ', ' + last_day + '.' +
                                              last_month + ' ' + self.days_dict[last_day] + '\n\n' + self.plus + ' ' +
                                              start_time + ' - ' + end_time + ', ' + day_reg + '.' + month_reg + ' ' +
                                              self.days_dict[day_reg])
                    elif last_info[0] == 'delete':
                        self.bot.send_message(chat_id[0], self.rupor_head + ' Пользователь ' + user_data[2] + ' ' +
                                              user_data[3] + ' (@' + user_data[1] + ') удалил запись:\n\n' + self.minus
                                              + ' ' + last_start_time + ' - ' + last_end_time + ', ' + last_day + '.' +
                                              last_month + ' ' + self.days_dict[last_day])
                    else:
                        self.bot.send_message(chat_id[0], self.rupor_head + ' Пользователь ' + user_data[2] + ' ' +
                                              user_data[3] + ' (@' + user_data[1] + ') занял переговорку:\n\n' +
                                              self.plus + ' ' + start_time + ' - ' + end_time + ', ' + day_reg + '.' +
                                              month_reg + ' ' + self.days_dict[day_reg])
                except:
                    pass

    # Проверка введенного времени на пересечение с уже существующими записями
    def check_times_intersection(self, message, day, month, data_time):
        data = self.other_funcs.sort_times(self.db_funcs.get_all_times(), 2)
        start_time = self.other_funcs.check_time_before(self.db_funcs.get_start_time(message.from_user.id))
        intersect_times = []
        if len(data) > 0:
            for row in data:
                is_error = False
                if int(day) == int(row[11]) and int(month) == int(row[12]):
                    if start_time == '':
                        if row[13] <= data_time < row[14]:
                            is_error = True
                    else:
                        if row[13] <= start_time < row[14]:
                            is_error = True
                        if row[13] < data_time <= row[14]:
                            is_error = True
                        if start_time <= row[13] and data_time >= row[14]:
                            is_error = True

                if is_error:
                    intersect_times.append(row)

        return intersect_times

    # Вывод списка на удаление/изменение
    def see_times_list_for(self, message, func_type):
        self.get_days_data()
        self.db_funcs.add_self_database(message.from_user.id)
        data = self.other_funcs.sort_times(self.db_funcs.get_my_times(self.db_funcs.get_user_id(message)[0]), 1)
        result_list = ''
        chat_id = message.chat.id
        counter = 1
        last_day = 0
        if len(data) > 0:
            if func_type == 1:
                result_list += 'Введи номер записи, которую хочешь отменить:\n'
            elif func_type == 2:
                result_list += 'Введи номер записи, которую хочешь изменить:\n'
            for row in data:
                now_month = str(self.other_funcs.check_date_format(row[3]))
                if last_day != self.other_funcs.check_date_format(row[2]):
                    last_day = self.other_funcs.check_date_format(row[2])
                    if last_day != 0:
                        result_list += '\n'
                    result_list += self.pushpin + " " + str(last_day) + '.' + now_month + '.' + \
                                   str(datetime.today().year) + ' ' + self.days_dict[str(last_day)] + ':\n\n'

                result_list += str(counter) + '. ' + row[4] + ' - ' + row[5] + '\n'
                counter += 1
            self.bot.send_message(chat_id, result_list, reply_markup=self.other_funcs.get_cancel_button())
            if func_type == 1:
                self.bot.register_next_step_handler(message, self.delete_time)
            elif func_type == 2:
                self.bot.register_next_step_handler(message, self.update_time)
        else:
            result_list += 'Сегодня переговорку ты не занимал'
            self.bot.send_message(chat_id, result_list, reply_markup=self.other_funcs.get_start_keyboard())

    # Удаление записи
    def delete_time(self, message):
        delete_time_id = str(message.text).strip()
        if delete_time_id.lower() != 'отмена':
            if not delete_time_id.isdigit():
                self.bot.send_message(message.chat.id, 'Неверно, введи номер еще раз')
                self.bot.register_next_step_handler(message, self.delete_time)
            counter = 1
            data = self.other_funcs.sort_times(self.db_funcs.get_my_times(self.db_funcs.get_user_id(message)[0]), 1)
            for row in data:
                if counter == int(delete_time_id):
                    if self.db_funcs.delete_from_timetable(row[0]):
                        last_info = ['delete', row[0], row[2], row[3], row[4], row[5]]
                        self.db_funcs.set_last_info(last_info, message.from_user.id)
                        
                        self.bot.send_message(message.chat.id,
                                              self.success + ' Запись успешно удалена:\n\n' +
                                              self.minus + ' ' + row[4] + " - " + row[5] + ", " +
                                              str(self.other_funcs.check_date_format(row[2])) + "." +
                                              str(self.other_funcs.check_date_format(row[3])) + " " +
                                              self.days_dict[str(self.other_funcs.check_date_format(row[2]))],
                                              reply_markup=self.other_funcs.get_start_keyboard())
                        self.send_timetable_news(message)
                        break
                    else:
                        self.bot.send_message(message.chat.id, self.interrobang +
                                              ' Запись не удалена! Произошла ошибка. Попробуй позже',
                                              reply_markup=self.other_funcs.get_start_keyboard())
                        self.db_funcs.del_self_database(message.from_user.id)
                        break
                counter += 1
        else:
            self.db_funcs.del_self_database(message.from_user.id)
            self.bot.send_message(message.chat.id, 'Ввод отменен', reply_markup=self.other_funcs.get_start_keyboard())

    # Изменение записи
    def update_time(self, message):
        update_time_id = str(message.text).strip()
        if update_time_id.lower() != 'отмена':
            if not update_time_id.isdigit():
                self.bot.send_message(message.chat.id, 'Неверно, введи номер еще раз')
                self.bot.register_next_step_handler(message, self.update_time)
            counter = 1
            data = self.other_funcs.sort_times(self.db_funcs.get_my_times(self.db_funcs.get_user_id(message)[0]), 1)
            for row in data:
                if counter == int(update_time_id):
                    last_info = ['update', row[0], row[2], row[3], row[4], row[5]]
                    self.db_funcs.set_last_info(last_info, message.from_user.id)
                    self.reg_time(message)
                    break
                counter += 1
        else:
            self.db_funcs.del_self_database(message.from_user.id)
            self.bot.send_message(message.chat.id, 'Ввод отменен', reply_markup=self.other_funcs.get_start_keyboard())

    # Моя занятость
    def print_my_times(self, message):
        self.get_days_data()
        is_empty = False
        if self.other_funcs.check_none(message.from_user.username) == '':
            is_empty = True
            result_list = self.memo + ' Твоя занятость на:'
        else:
            result_list = self.memo + ' @' + message.from_user.username + ', '
        data = self.other_funcs.sort_times(self.db_funcs.get_my_times(self.db_funcs.get_user_id(message)[0]), 1)
        counter = 1
        last_day = 0
        if len(data) > 0:
            result_list += 'занятость на:\n' if not is_empty else ''
            for row in data:
                now_month = str(self.other_funcs.check_date_format(row[3]))
                if last_day != self.other_funcs.check_date_format(row[2]):
                    last_day = self.other_funcs.check_date_format(row[2])
                    counter = 1
                    if last_day != 0:
                        result_list += '\n'
                    result_list += self.pushpin + " " + str(last_day) + '.' + now_month + '.' + \
                                   str(datetime.today().year) + ' ' + self.days_dict[str(last_day)] + ':\n\n'
                result_list += str(counter) + '. ' + row[4] + ' - ' + row[5] + '\n'
                counter += 1
            self.bot.send_message(message.chat.id, result_list, reply_markup=self.other_funcs.get_start_keyboard())
        else:
            result_list += 'сегодня переговорку ты не занимал'
            self.bot.send_message(message.chat.id, result_list, reply_markup=self.other_funcs.get_start_keyboard())

    # Занятость переговорки на сегодня
    def print_all_times(self, message):
        self.get_days_data()
        result_list = self.memo + ' Занятость на:\n'
        data = self.other_funcs.sort_times(self.db_funcs.get_all_times(), 2)
        counter = 1
        last_day = 0
        if len(data) > 0:
            for row in data:
                now_month = str(self.other_funcs.check_date_format(row[12]))
                if last_day != self.other_funcs.check_date_format(row[11]):
                    last_day = self.other_funcs.check_date_format(row[11])
                    counter = 1
                    if last_day != 0:
                        result_list += '\n'
                    result_list += self.pushpin + " " + str(last_day) + '.' + now_month + '.' \
                                   + str(datetime.today().year) + ' ' + self.days_dict[str(last_day)] + ':\n\n'
                result_list += str(counter) + '. ' + row[13] + ' - ' + row[14] + '  ---  ' \
                               + row[2] + ' ' + row[3] + ' (@' + row[1] + ')\n'
                counter += 1
            self.bot.send_message(message.chat.id, result_list, reply_markup=self.other_funcs.get_start_keyboard())
        else:
            self.bot.send_message(message.chat.id, 'Сегодня переговорку еще никто не занимал! Успей '
                                                   'забрать лучшее время ;)', reply_markup=self.other_funcs.get_start_keyboard())

    # Клавиатура выбора дней
    def get_days_keyboard(self):
        keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
        row_width = 7
        buttons_added = []
        now = datetime.today()
        now_day_num = now.weekday()
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        for num in range(now.day, now.day + 14):
            if num > days_in_month:
                day_num = num - days_in_month
            else:
                day_num = num
            buttons_added.append(telebot.types.InlineKeyboardButton(text=str(day_num) + ' ' + self.day_names[now_day_num]))
            if now_day_num != 6:
                now_day_num += 1
            else:
                now_day_num = 0
            if len(buttons_added) == row_width:
                keyboard.row(*buttons_added)
                buttons_added = []
        keyboard.row('Отмена')

        return keyboard

    # Информация на следующие 14 дней
    def get_days_data(self):
        added_days = []
        days_dict = {}
        now = datetime.today()
        now_day_num = now.weekday()
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        for num in range(now.day, now.day + 14):
            if num > days_in_month:
                day_num = num - days_in_month
            else:
                day_num = num
            added_days.append(day_num)
            days_dict[str(self.other_funcs.check_date_format(day_num))] = self.day_names[now_day_num]
            if now_day_num != 6:
                now_day_num += 1
            else:
                now_day_num = 0

        self.added_days = added_days
        self.days_dict = days_dict

    # Проверка юзернейма на пустоту и выдача части приветствия
    def get_hello_part(self, user_name):
        hello_part = 'Привет'
        user_name = self.other_funcs.check_none(user_name)
        if user_name == '':
            hello_part += '!\n'
        else:
            hello_part += ', ' + user_name + '!\n'
        
        return hello_part
            
    # Время
    def print_today(self, chat_id, today):
        self.bot.send_message(chat_id, str(today.strftime("%H:%M  %d.%m.%Y")), reply_markup=self.other_funcs.get_start_keyboard())

    # Справка
    def print_help(self, message):
        self.bot.send_message(message.chat.id, 'Список команд:\n\n'
                                               '/help - вывести список команд.\n'
                                               '/add - занять переговорку:\n'
                                               '-- Тебе нужно будет 2 раза ввести время.\n'
                                               '-- Примеры ввода времени: 15, 15 00, 15 30, 15:30\n'
                                               '/delete - перейти в режим удаления своей записи.\n'
                                               '/update - перейти в режим правки своих записей.\n'
                                               '/all - вывести весь список забронированного времени.\n'
                                               '/my - вывести только твое забронированное время.\n'
                                               '/time - вывести текущую дату и время.\n\n'
                                               # '/cat - вывести случайную гифку с котом. (offed)\n\n'
                                               'Версия бота: 0.8.33\n'
                                               'Последнее обновление: 20.02.2020\n',
                              reply_markup=self.other_funcs.get_start_keyboard())

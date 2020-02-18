import re
from datetime import datetime
import calendar
import telebot
import bothome
import time
import urllib.parse
from functions import dbfuncs


class BotFuncs:

    def __init__(self, bot):
        self.bot = bot
        self.dataReg = {'start_time': '', 'end_time': '', 'day_reg': '', 'month_reg': ''}
        self.db_funcs = dbfuncs.DatabaseFuncs(self.bot)
        self.bot_home = bothome.BotHome()
        self.data = []
        self.first_time = ''
        self.added_days = []
        self.error = u'\xE2\x9D\x8C'
        self.success = u'\xE2\x9C\x85'

    # Занять переговорку (следующие 4 функции)
    def regTime(self, message):
        self.bot.send_message(message.chat.id, 'Выбери или введи день из предложенных:',
                              reply_markup=self.getDaysKeyboard())
        self.bot.register_next_step_handler(message, self.regDayTime)

    def regDayTime(self, message):
        self.dataReg['day_reg'] = str(message.text[0:2]).strip()
        if self.dataReg['day_reg'] != '-':
            if not re.match(r'^[0-9]{1,2}$', self.dataReg['day_reg'].lower()):
                self.bot.send_message(message.chat.id, self.error + '\nНеверно, выбери снова:',
                                      reply_markup=self.getDaysKeyboard())
                self.bot.register_next_step_handler(message, self.regDayTime)
                return
            if int(self.dataReg['day_reg']) in self.added_days:
                if int(self.dataReg['day_reg']) < datetime.today().day:
                    if datetime.today().month != 12:
                        self.dataReg['month_reg'] = str(datetime.today().month + 1)
                    else:
                        self.dataReg['month_reg'] = '1'
                else:
                    self.dataReg['month_reg'] = str(datetime.today().month)
                self.bot.send_message(message.chat.id, 'Во сколько тебе нужна переговорка?',
                                      reply_markup=self.getCancelButton())
                self.bot.register_next_step_handler(message, self.regStartTime)
            else:
                self.bot.send_message(message.chat.id, self.error + '\nНеверно, выбери снова',
                                      reply_markup=self.getDaysKeyboard())
                self.bot.register_next_step_handler(message, self.regDayTime)
        else:
            self.first_time = ''
            self.bot.send_message(message.chat.id, 'Ввод отменен', reply_markup=self.getStartKeyboard())

    def regStartTime(self, message):
        self.first_time = ''
        self.dataReg['start_time'] = str(message.text).strip()
        if self.dataReg['start_time'] != '-':
            if not re.match(r'^[0-9]{0,2}(:|\s)[0-9]{2}$', self.dataReg['start_time'].lower()):
                if not re.match(r'^[0-9]{1,2}$', self.dataReg['start_time'].lower()):
                    self.bot.send_message(message.chat.id, self.error + '\nНеверные данные, повтори ввод',
                                          reply_markup=self.getCancelButton())
                    self.bot.register_next_step_handler(message, self.regStartTime)
                    return
            self.dataReg['start_time'] = self.db_funcs.checkTimeBefore(self.dataReg['start_time'])
            intersection_times = self.checkTimesIntersection(self.dataReg['day_reg'], self.dataReg['month_reg'], self.dataReg['start_time'])
            if len(intersection_times) > 0:
                answer = self.error + '\nТвое время пересекается с:\n\n'
                counter = 1
                for row in intersection_times:
                    answer += str(counter) + '. ' + row[13] + ' - ' + row[14] + '  ---  ' \
                              + row[2] + ' ' + row[3] + ' (@' + row[1] + ')\n'
                    counter += 1
                answer += '\nПовтори ввод'
                self.bot.send_message(message.chat.id, answer, reply_markup=self.getCancelButton())
                self.bot.register_next_step_handler(message, self.regStartTime)
                return
            self.bot.send_message(message.chat.id, 'До скольки тебе нужна переговорка?',
                                  reply_markup=self.getCancelButton())
            self.bot.register_next_step_handler(message, self.endRegTime)
        else:
            self.first_time = ''
            self.bot.send_message(message.chat.id, 'Ввод отменен', reply_markup=self.getStartKeyboard())

    def endRegTime(self, message):
        self.dataReg['end_time'] = str(message.text).strip()
        if self.dataReg['end_time'] != '-':
            if not re.match(r'^[0-9]{0,2}(:|\s)[0-9]{2}$', self.dataReg['end_time'].lower()):
                if not re.match(r'^[0-9]{1,2}$', self.dataReg['end_time'].lower()):
                    self.bot.send_message(message.chat.id, self.error + '\nНеверные данные, повтори ввод',
                                          reply_markup=self.getCancelButton())
                    self.bot.register_next_step_handler(message, self.endRegTime)
                    return
            self.dataReg['end_time'] = self.db_funcs.checkTimeBefore(self.dataReg['end_time'])
            if self.dataReg['end_time'] > self.dataReg['start_time']:
                intersection_times = self.checkTimesIntersection(self.dataReg['day_reg'], self.dataReg['month_reg'],
                                                                 self.dataReg['end_time'])
                if len(intersection_times) > 0:
                    answer = self.error + '\nТвое время пересекается с:\n\n'
                    counter = 1
                    for row in intersection_times:
                        answer += str(counter) + '. ' + row[13] + ' - ' + row[14] + '  ---  ' \
                                  + row[2] + ' ' + row[3] + ' (@' + row[1] + ')\n'
                        counter += 1
                    answer += '\nПовтори ввод'
                    self.bot.send_message(message.chat.id, answer, reply_markup=self.getCancelButton())
                    self.bot.register_next_step_handler(message, self.regStartTime)
                    return
                final_add_text = 'Записал тебя c ' + self.dataReg['start_time'] + " до " + self.dataReg[
                                  'end_time'] + ", на " + self.checkDateFormat(self.dataReg['day_reg']) + '.' \
                                 + self.checkDateFormat(self.dataReg['month_reg']) + ' ' + self.success
                self.bot.send_message(message.chat.id, final_add_text, reply_markup=self.getStartKeyboard())
                self.first_time = ''
                self.added_days = []
                self.db_funcs.addToTimetable(message, self.dataReg)
                # self.sendTimetableNews(message)
            else:
                self.bot.send_message(message.chat.id, self.error + '\nПовтори ввод', reply_markup=self.getCancelButton())
                self.bot.register_next_step_handler(message, self.endRegTime)
        else:
            self.first_time = ''
            self.bot.send_message(message.chat.id, 'Ввод отменен', reply_markup=self.getStartKeyboard())

    # Рассылка о добавленной записи
    def sendTimetableNews(self, message):
        chat_ids = self.db_funcs.getAllChatIds()
        user_data = self.db_funcs.getUser(message)[0]
        day_reg = self.checkDateFormat(self.dataReg['day_reg'])
        month_reg = self.checkDateFormat(self.dataReg['month_reg'])
        # day_reg = self.dataReg['day_reg'] if int(self.dataReg['day_reg']) > 9 else '0' + self.dataReg['day_reg']
        # month_reg = self.dataReg['month_reg'] if int(self.dataReg['month_reg']) > 9 else '0' + self.dataReg['month_reg']

        for chat_id in chat_ids:
            if chat_id[0] != message.chat.id:
                try:
                    time.sleep(1)
                    self.bot.send_message(chat_id[0], 'Пользователь ' + user_data[2] + ' ' + user_data[3] +
                                          ' (@' + user_data[1] + ') занял переговорку ' + day_reg + '.' + month_reg +
                                          ' с ' + self.dataReg['start_time'] + ' до ' + self.dataReg['end_time'])
                except:
                    pass

        self.dataReg = {'start_time': '', 'end_time': '', 'day_reg': '', 'month_reg': ''}

    # Проверка введенного времени на пересечение с уже существующими записями
    def checkTimesIntersection(self, day, month, data_time):
        data = self.db_funcs.sortTimes(self.db_funcs.getAllTimes(), 2)
        intersect_times = []
        if len(data) > 0:
            for row in data:
                if int(day) == int(row[11]) and int(month) == int(row[12]):
                    if self.first_time == '' and data_time >= row[13]:
                        if data_time < row[14]:
                            intersect_times.append(row)
                    elif self.first_time != '' and data_time > row[13]:
                        if data_time < row[14]:
                            intersect_times.append(row)
                    if self.first_time != '':
                        if self.first_time < row[13] and data_time >= row[14]:
                            intersect_times.append(row)
            if self.first_time == '':
                self.first_time = data_time

        return intersect_times

    # Вывод списка на удаление/изменение
    def seeTimesListFor(self, message, func_type):
        result_list = ''
        chat_id = message.chat.id
        self.data = self.db_funcs.sortTimes(self.db_funcs.getMyTimes(self.db_funcs.getUserId(message)), 1)
        counter = 1
        last_day = 0
        if len(self.data) > 0:
            if func_type == 1:
                result_list += 'Введи номер записи, которую хочешь отменить:\n' \
                               '(Отмени ввод символом `-`)\n'
            elif func_type == 2:
                result_list += 'Введи номер записи, которую хочешь изменить:\n' \
                               '(Отмени ввод символом `-`)\n'
            for row in self.data:
                now_month = self.checkDateFormat(row[3])
                if last_day != row[2]:
                    last_day = self.checkDateFormat(row[2])
                    if last_day != 0:
                        result_list += '\n'
                    result_list += str(last_day) + '.' + str(now_month) + '.' + str(datetime.today().year) + ':\n\n'
                result_list += str(counter) + '. ' + row[4] + ' - ' + row[5] + '\n'
                counter += 1
            self.bot.send_message(chat_id, result_list)
            if func_type == 1:
                self.bot.register_next_step_handler(message, self.deleteTime)
            # elif func_type == 2:
            #     self.bot.register_next_step_handler(message, self.updateTime)
        else:
            result_list += 'Сегодня переговорку ты не занимал'
            self.bot.send_message(chat_id, result_list)

    # Удаление записи
    def deleteTime(self, message):
        delete_time_id = str(message.text).strip()
        if delete_time_id != '-':
            if not delete_time_id.isdigit():
                self.bot.send_message(message.chat.id, 'Неверно, введи номер еще раз')
                self.bot.register_next_step_handler(message, self.deleteTime)
            counter = 1
            for row in self.data:
                if counter == int(delete_time_id):
                    self.db_funcs.deleteFromTimetable(row[0])
                    self.bot.send_message(message.chat.id, 'Запись на ' + row[4] + " - " + row[5] + " удалена!")
                    self.data = []
                    break
                counter += 1
        else:
            self.first_time = ''
            self.bot.send_message(message.chat.id, 'Ввод отменен', reply_markup=self.getStartKeyboard())

    # # Изменение записи
    # Не забудь раскомментить вызов функции выше!
    # def updateTime(self, message):
    #     update_time_id = str(message.text).strip()
    #     if not update_time_id.isdigit():
    #         self.bot.send_message(message.chat.id, 'Неверно, введи номер еще раз')
    #         self.bot.register_next_step_handler(message, self.updateTime)
    #     counter = 1
    #     for row in self.data:
    #         if counter == int(update_time_id):
    #             self.db_funcs.updateTimetable()

    # Моя занятость
    def printMyTimes(self, message):
        result_list = '@' + message.from_user.username + ', '
        data = self.db_funcs.sortTimes(self.db_funcs.getMyTimes(self.db_funcs.getUserId(message)), 1)
        counter = 1
        last_day = 0
        if len(data) > 0:
            result_list += 'занятость на:\n'
            for row in data:
                now_month = self.checkDateFormat(row[3])
                if last_day != row[2]:
                    last_day = self.checkDateFormat(row[2])
                    counter = 1
                    if last_day != 0:
                        result_list += '\n'
                    result_list += str(last_day) + '.' + str(now_month) + '.' + str(datetime.today().year) + ':\n\n'
                result_list += str(counter) + '. ' + row[4] + ' - ' + row[5] + '\n'
                counter += 1
        else:
            result_list += 'сегодня переговорку ты не занимал'

        self.bot.send_message(message.chat.id, result_list)

    # Занятость переговорки на сегодня
    def printAllTimes(self, message):
        result_list = 'Занятость на:\n'
        data = self.db_funcs.sortTimes(self.db_funcs.getAllTimes(), 2)
        counter = 1
        last_day = 0
        if len(data) > 0:
            for row in data:
                now_month = self.checkDateFormat(row[12])
                if last_day != row[11]:
                    last_day = self.checkDateFormat(row[11])
                    counter = 1
                    if last_day != 0:
                        result_list += '\n'
                    result_list += str(last_day) + '.' + str(now_month) + '.' + str(datetime.today().year) + ':\n\n'
                result_list += str(counter) + '. ' + row[13] + ' - ' + row[14] + '  ---  ' \
                               + row[2] + ' ' + row[3] + ' (@' + row[1] + ')\n'
                counter += 1
        else:
            result_list = 'Сегодня переговорку еще никто не занимал! Успей забрать лучшее время ;)'

        self.bot.send_message(message.chat.id, result_list, reply_markup=self.getStartKeyboard())

    def getDaysKeyboard(self):
        self.added_days = []
        day_names = ['(пн)', '(вт)', '(ср)', '(чт)', '(пт)', '(сб)', '(вск)', ]
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
            self.added_days.append(day_num)
            buttons_added.append(telebot.types.InlineKeyboardButton(text=str(day_num) + ' ' + day_names[now_day_num]))
            if now_day_num != 6:
                now_day_num += 1
            else:
                now_day_num = 0
            if len(buttons_added) == row_width:
                keyboard.row(*buttons_added)
                buttons_added = []
        keyboard.row('Отмена')

        return keyboard

    # Время
    def printToday(self, chat_id, today):
        self.bot.send_message(chat_id, str(today.strftime("%H:%M  %d.%m.%Y")))

    # Справка
    def printHelp(self, message):
        self.bot.send_message(message.chat.id, 'Список команд:\n\n'
                                               '/help - вывести список команд.\n'
                                               '/add - занять переговорку:\n'
                                               '-- Тебе нужно будет 2 раза ввести время.\n'
                                               '-- Примеры ввода времени: 15, 15 00, 15 30, 15:30\n'
                                               '/delete - перейти в режим удаления своей записи.\n'
                                               '/update - перейти в режим правки своих записей. (offed)\n'
                                               '/all - вывести весь список забронированного времени.\n'
                                               '/my - вывести только твои забронированное время.\n'
                                               '/time - вывести текущую дату и время.\n'
                                               '/cat - вывести случайную гифку с котом. (offed)\n\n'
                                               'Версия бота: 0.7.17\n'
                                               'Последнее обновление: 18.02.2020\n')


    @staticmethod
    def getStartKeyboard():
        start_keyboard = telebot.types.ReplyKeyboardMarkup(True)
        start_keyboard.row('Занять переговорку', 'Моя занятость', 'Удалить запись')
        start_keyboard.row('Занятость переговорки на сегодня')
        start_keyboard.row('Дата', 'Справка')

        return start_keyboard

    @staticmethod
    def checkDateFormat(date_data):
        if int(date_data) < 10:
            return '0' + str(date_data)
        else:
            return date_data

    @staticmethod
    def getCancelButton():
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        keyboard.row('Отмена')

        return keyboard


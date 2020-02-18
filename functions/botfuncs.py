import re
import datetime
import telebot
import bothome
from functions import dbfuncs


class BotFuncs:

    def __init__(self, bot):
        self.bot = bot
        self.dataReg = {'start_time': '', 'end_time': '', 'day_reg': ''}
        self.db_funcs = dbfuncs.DatabaseFuncs(self.bot)
        self.bot_home = bothome.BotHome()
        self.data = []
        self.first_time = ''

    # Занять переговорку (следующие 4 функции)
    def regTime(self, message):
        self.bot.send_message(message.chat.id, 'Выбери или введи число из предложенных:\n'
                                               '(Отмени ввод символом `-`)',
                              reply_markup=self.getDaysKeyboard())
        self.bot.register_next_step_handler(message, self.regDayTime)

    def regDayTime(self, message):
        self.dataReg['day_reg'] = str(message.text).strip()
        if self.dataReg['day_reg'] != '-':
            if not re.match(r'^[0-9]{1,2}$', self.dataReg['day_reg'].lower()):
                self.bot.send_message(message.chat.id, 'Выбери или введи число из предложенных:\n'
                                                       '(Отмени ввод символом `-`)',
                                      reply_markup=self.getDaysKeyboard())
                self.bot.register_next_step_handler(message, self.regDayTime)
                return
            if int(self.dataReg['day_reg']) < datetime.datetime.today().day:
                self.bot.send_message(message.chat.id, 'Неверно, повтори ввод:\n'
                                                       '(Отмени ввод символом `-`)',
                                      reply_markup=self.getDaysKeyboard())
                self.bot.register_next_step_handler(message, self.regDayTime)
                return
            self.bot.send_message(message.chat.id, 'Во сколько тебе нужна переговорка?\n'
                                                   '(Отмени ввод символом `-`)')
            self.bot.register_next_step_handler(message, self.regStartTime)
        else:
            self.first_time = ''
            self.bot.send_message(message.chat.id, 'Ввод отменен', reply_markup=self.getStartKeyboard())

    def regStartTime(self, message):
        self.first_time = ''
        self.dataReg['start_time'] = str(message.text).strip()
        if self.dataReg['start_time'] != '-':
            if not re.match(r'^[0-9]{0,2}(:|\s)[0-9]{2}$', self.dataReg['start_time'].lower()):
                if not re.match(r'^[0-9]{1,2}$', self.dataReg['start_time'].lower()):
                    self.bot.send_message(message.chat.id, 'Не понял тебя, пожалуйста повтори')
                    self.bot.register_next_step_handler(message, self.regStartTime)
                    return
            self.dataReg['start_time'] = self.db_funcs.checkTimeBefore(self.dataReg['start_time'])
            intersection_times = self.checkTimesIntersection(self.dataReg['day_reg'], self.dataReg['start_time'])
            if len(intersection_times) > 0:
                answer = 'Ваше время пересекается с:\n\n'
                counter = 1
                for row in intersection_times:
                    print(row)
                    answer += str(counter) + '. ' + row[11] + ' - ' + row[12] + '  ---  ' \
                              + row[2] + ' ' + row[3] + ' (@' + row[1] + ')\n'
                    counter += 1
                answer += '\nПоменяй время или отмени ввод символом `-`'
                self.bot.send_message(message.chat.id, answer)
                self.bot.register_next_step_handler(message, self.regStartTime)
                return
            self.bot.send_message(message.chat.id, 'До скольки тебе нужна переговорка?\n(Отмени ввод символом `-`)')
            self.bot.register_next_step_handler(message, self.endRegTime)
        else:
            self.first_time = ''
            self.bot.send_message(message.chat.id, 'Ввод отменен', reply_markup=self.getStartKeyboard())

    def endRegTime(self, message):
        self.dataReg['end_time'] = str(message.text).strip()
        if self.dataReg['end_time'] != '-':
            if not re.match(r'^[0-9]{0,2}(:|\s)[0-9]{2}$', self.dataReg['end_time'].lower()):
                if not re.match(r'^[0-9]{1,2}$', self.dataReg['end_time'].lower()):
                    self.bot.send_message(message.chat.id, 'Не понял тебя, пожалуйста повтори')
                    self.bot.register_next_step_handler(message, self.endRegTime)
                    return
            self.dataReg['end_time'] = self.db_funcs.checkTimeBefore(self.dataReg['end_time'])
            if self.dataReg['end_time'] > self.dataReg['start_time']:
                intersection_times = self.checkTimesIntersection(self.dataReg['day_reg'], self.dataReg['end_time'])
                if len(intersection_times) > 0:
                    answer = 'Ваше время пересекается с:\n\n'
                    counter = 1
                    for row in intersection_times:
                        answer += str(counter) + '. ' + row[11] + ' - ' + row[12] + '  ---  ' \
                                  + row[2] + ' ' + row[3] + ' (@' + row[1] + ')\n'
                        counter += 1
                    answer += '\nПоменяй время или отмени ввод символом `-`'
                    self.bot.send_message(message.chat.id, answer)
                    self.bot.register_next_step_handler(message, self.endRegTime)
                    return

                self.bot.send_message(message.chat.id, 'Записал тебя на ' + self.dataReg['start_time'] + " - " + self.dataReg[
                                      'end_time'] + ", " + self.dataReg['day_reg'] + " число", reply_markup=self.getStartKeyboard())
                self.first_time = ''
                self.db_funcs.addToTimetable(message, self.dataReg)
            else:
                self.bot.send_message(message.chat.id, 'Кажется, ты ошибся. Пожалуйста, повтори ввод')
                self.bot.register_next_step_handler(message, self.endRegTime)
                return
        else:
            self.first_time = ''
            self.bot.send_message(message.chat.id, 'Ввод отменен', reply_markup=self.getStartKeyboard())

    # Проверка введенного времени на пересечение с уже существующими записями
    def checkTimesIntersection(self, day, time):
        data = self.db_funcs.sortTimes(self.db_funcs.getAllTimes(), 2)
        intersect_times = []
        if len(data) > 0:
            for row in data:
                if int(day) == int(row[10]):
                    if time >= row[11]:
                        if self.first_time != '':
                            if time <= row[12]:
                                intersect_times.append(row)
                        else:
                            if time < row[12]:
                                intersect_times.append(row)
                    if self.first_time != '':
                        if self.first_time < row[11] and time > row[12]:
                            intersect_times.append(row)
            if self.first_time == '':
                self.first_time = time

        return intersect_times

    # Вывод списка на удаление/изменение
    def seeTimesListFor(self, message, func_type):
        result_list = ''
        chat_id = message.chat.id
        self.data = self.db_funcs.sortTimes(self.db_funcs.getMyTimes(self.db_funcs.getUserId(message)), 1)
        counter = 1
        last_day = 0
        now_month = datetime.datetime.today().month
        if len(self.data) > 0:
            if func_type == 1:
                result_list += 'Введи номер записи, которую хочешь отменить:\n' \
                               '(Отмени ввод символом `-`)\n'
            elif func_type == 2:
                result_list += 'Введи номер записи, которую хочешь изменить:\n' \
                               '(Отмени ввод символом `-`)\n'
            if now_month < 10:
                now_month = '0' + str(now_month)
            for row in self.data:
                if last_day != row[2]:
                    last_day = row[2]
                    if last_day != 0:
                        result_list += '\n'
                    result_list += str(last_day) + '.' + now_month + '.' + str(datetime.datetime.today().year) + ':\n\n'
                result_list += str(counter) + '. ' + row[3] + ' - ' + row[4] + '\n'
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
                    self.bot.send_message(message.chat.id, 'Запись на ' + row[3] + " - " + row[4] + " удалена!")
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
        result_list = '@' + message.from_user.username + ', занятость на:\n'
        data = self.db_funcs.sortTimes(self.db_funcs.getMyTimes(self.db_funcs.getUserId(message)), 1)
        counter = 1
        last_day = 0
        now_month = datetime.datetime.today().month
        if now_month < 10:
            now_month = '0' + str(now_month)
        if len(data) > 0:
            for row in data:
                if last_day != row[2]:
                    last_day = row[2]
                    counter = 1
                    if last_day != 0:
                        result_list += '\n'
                    result_list += str(last_day) + '.' + now_month + '.' + str(datetime.datetime.today().year) + ':\n\n'
                result_list += str(counter) + '. ' + row[3] + ' - ' + row[4] + '\n'
                counter += 1
        else:
            result_list += 'Сегодня переговорку ты не занимал'

        self.bot.send_message(message.chat.id, result_list)

    # Занятость переговорки на сегодня
    def printAllTimes(self, message):
        result_list = 'Занятость на:\n'
        data = self.db_funcs.sortTimes(self.db_funcs.getAllTimes(), 2)
        counter = 1
        last_day = 0
        now_month = datetime.datetime.today().month
        if now_month < 10:
            now_month = '0' + str(now_month)
        if len(data) > 0:
            for row in data:
                if last_day != row[10]:
                    last_day = row[10]
                    counter = 1
                    if last_day != 0:
                        result_list += '\n'
                    result_list += str(last_day) + '.' + now_month + '.' + str(datetime.datetime.today().year) + ':\n\n'
                result_list += str(counter) + '. ' + row[11] + ' - ' + row[12] + '  ---  ' \
                               + row[2] + ' ' + row[3] + ' (@' + row[1] + ')\n'
                counter += 1
        else:
            result_list += 'Сегодня переговорку еще никто не занимал! Успей забрать лучшее время ;)'

        self.bot.send_message(message.chat.id, result_list)

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
                                               'Версия бота: 0.7.13\n'
                                               'Последнее обновление: 14.02.2020\n')

    @staticmethod
    def getStartKeyboard():
        start_keyboard = telebot.types.ReplyKeyboardMarkup(True)
        start_keyboard.row('Занять переговорку', 'Моя занятость', 'Удалить запись')
        start_keyboard.row('Занятость переговорки на сегодня')
        start_keyboard.row('Дата', 'Справка')

        return start_keyboard

    @staticmethod
    def getDaysKeyboard():
        keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
        row_width = 7
        buttons_added = []
        today = datetime.datetime.today().day
        for num in range(today, today + 14):
            buttons_added.append(telebot.types.KeyboardButton(text=num))
            if len(buttons_added) == row_width:
                keyboard.row(*buttons_added)
                buttons_added = []

        return keyboard


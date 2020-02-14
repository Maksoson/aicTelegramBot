import re
import datetime
from functions import dbfuncs


class BotFuncs:

    def __init__(self, bot):
        self.bot = bot
        self.dataReg = {'start_time': '', 'end_time': ''}
        self.db_funcs = dbfuncs.DatabaseFuncs(self.bot)
        self.data = []

    # Занять переговорку
    def regTime(self, message):
        self.bot.send_message(message.chat.id, 'Во сколько тебе нужна переговорка?')
        self.bot.register_next_step_handler(message, self.regEndTime)

    def regEndTime(self, message):
        self.dataReg['start_time'] = str(message.text).strip()
        if not re.match(r'^[0-9]{0,2}(:|\s)[0-9]{2}$', self.dataReg['start_time'].lower()):
            if not re.match(r'^[0-9]{1,2}$', self.dataReg['start_time'].lower()):
                self.bot.send_message(message.chat.id, 'Не понял тебя, повтори пожалуйста')
                self.bot.register_next_step_handler(message, self.regEndTime)
                return

        self.bot.send_message(message.chat.id, 'До скольки тебе нужна переговорка?')
        self.bot.register_next_step_handler(message, self.endRegTime)

    def endRegTime(self, message):
        self.dataReg['end_time'] = str(message.text).strip()
        if not re.match(r'^[0-9]{0,2}(:|\s)[0-9]{2}$', self.dataReg['end_time'].lower()):
            if not re.match(r'^[0-9]{1,2}$', self.dataReg['end_time'].lower()):
                self.bot.send_message(message.chat.id, 'Не понял тебя, повтори пожалуйста')
                self.bot.register_next_step_handler(message, self.endRegTime)
                return

        self.bot.send_message(message.chat.id, 'Записал тебя на ' + self.db_funcs.checkTimeBefore(self.dataReg['start_time']) + " - " + self.db_funcs.checkTimeBefore(self.dataReg['end_time']))
        self.db_funcs.addToTimetable(message, self.dataReg)

    # Удалить запись
    def whatTimeDelete(self, message, today):
        result_list = ''
        chat_id = message.chat.id
        self.data = self.db_funcs.sortTimes(self.db_funcs.getMyTimes(self.db_funcs.getUserId(message), today.day), 1)
        counter = 1
        if len(self.data) > 0:
            result_list += 'Введи номер записи, которую хочешь отменить:\n\n'
            for row in self.data:
                result_list += str(counter) + '. ' + row[3] + ' - ' + row[4] + '\n'
                counter += 1
            self.bot.send_message(chat_id, result_list)
            self.bot.register_next_step_handler(message, self.deleteTime)
        else:
            result_list += 'Сегодня переговорку ты не занимал'
            self.bot.send_message(chat_id, result_list)

    def deleteTime(self, message):
        delete_time_id = str(message.text).strip()
        if not delete_time_id.isdigit():
            self.bot.send_message(message.chat.id, 'Неверно, введи номер записи снова')
            self.bot.register_next_step_handler(message, self.deleteTime)
        counter = 1
        # self.data = self.db_funcs.sortTimes(self.db_funcs.getMyTimes(self.db_funcs.getUserId(message), today.day), 1)
        for row in self.data:
            print(row)
            if counter == int(delete_time_id):
                self.db_funcs.deleteFromTimetable(row[8])
                self.bot.send_message(message.chat.id, 'Запись на ' + row[11] + " - " + row[12] + " удалена!")
                self.data = []
                break
            counter += 1

    # Моя занятость
    def printMyTimes(self, message, today):
        result_list = '@' + message.from_user.username + ', занятость на ' + today.strftime('%d.%m.%y') + '\n\n'
        data = self.db_funcs.sortTimes(self.db_funcs.getMyTimes(self.db_funcs.getUserId(message), today.day), 1)
        counter = 1
        if len(data) > 0:
            for row in data:
                result_list += str(counter) + '. ' + row[3] + ' - ' + row[4] + '\n'
                counter += 1
        else:
            result_list += 'Сегодня переговорку ты не занимал'

        self.bot.send_message(message.chat.id, result_list)

    # Занятость переговорки на сегодня
    def printAllTimes(self, message, today):
        result_list = 'Занятость на ' + today.strftime('%d.%m.%y') + '\n\n'
        data = self.db_funcs.sortTimes(self.db_funcs.getAllTimes(today.day), 2)
        counter = 1
        print(data)
        if len(data) > 0:
            for row in data:
                result_list += str(counter) + '. ' + row[11] + ' - ' + row[12] + '  ---  ' \
                               + row[2] + ' ' + row[3] + ' (@' + row[1] + ')\n'
                counter += 1
        else:
            result_list += 'Сегодня переговорку еще никто не занял! Успей занять лучшее время ;)'

        self.bot.send_message(message.chat.id, result_list)

    # Время
    def printToday(self, chat_id, today):
        self.bot.send_message(chat_id, str(today.strftime("%H:%M  %d.%m.%Y")))

    # Справка
    def printHelp(self, message):
        self.bot.send_message(message.chat.id, 'Список команд:\n\n'
                                               '/keyboard - вызвать/убрать клавиатуру.\n'
                                               '/help - вывести список команд.\n'
                                               '/add - занять переговорку:\n'
                                               '-- Тебе нужно будет 2 раза ввести время.\n'
                                               '-- Примеры ввода времени: 15, 15 00, 15 30, 15:30\n'
                                               '/update - перейти в режим правки своей занятости. (off)\n'
                                               '/all - вывести весь список забронированного времени.\n'
                                               '/my - вывести только твое забронированное время.\n'
                                               '/time - вывести текущую дату и время.\n'
                                               '/cat - вывести случайную гифку с котом. (off)\n\n'
                                               'Версия бота: 0.7.13\n'
                                               'Последнее обновление: 14.02.2020\n')

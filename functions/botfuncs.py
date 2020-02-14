import re
import datetime
from functions import dbfuncs


class BotFuncs:

    def __init__(self, bot):
        self.bot = bot
        self.dataReg = {'start_time': '', 'end_time': ''}
        self.db_funcs = dbfuncs.DatabaseFuncs(self.bot)

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

        self.bot.send_message(message.chat.id, 'Добавил запись на ' + self.db_funcs.checkTimeBefore(self.dataReg['start_time']) + " - " + self.db_funcs.checkTimeBefore(self.dataReg['end_time']))
        self.db_funcs.addToTimetable(message, self.dataReg)

    # Моя занятость
    def printMyTimes(self, message, today):
        result_list = '@' + message.from_user.username + ', занятость на ' + today.strftime('%d.%m.%y') + '\n\n'
        data = self.db_funcs.sortTimes(self.db_funcs.getMyTimes(self.db_funcs.getUserId(message), today.day), 1)
        print(str(len(data)) + ' LEN')
        counter = 1
        if len(data) > 0:
            for row in data:
                result_list += str(counter) + '. ' + row[3] + ' - ' + row[4] + '\n'
                counter += 1
        else:
            result_list += 'Твой список занятости пуст'

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
            result_list += 'Cписок занятости пуст, успей занять лучшее время ;)'

        self.bot.send_message(message.chat.id, result_list)

    # Справка
    def printHelp(self, message):
        self.bot.send_message(message.chat.id, 'Список команд:\n'
                                               '/keyboard - вызвать/убрать клавиатуру\n'
                                               '/help - вывести список команд\n'
                                               '/add - занять переговорку\n'
                                               '/update - перейти в режим правки своей занятости\n'
                                               '/all - вывести весь список забронированного времени\n'
                                               '/my - вывести только твое забронированное время\n'
                                               '/time - вывести текущую дату и время\n'
                                               '/cat - вывести случайную гифку с котом\n\n'
                                               'Версия бота: 0.7.13\n'
                                               'Последнее обновление: 14.02.2020\n')

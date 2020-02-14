from functions import dbfuncs
import datetime
import re


class BotFuncs:

    def __init__(self, bot):
        self.bot = bot
        self.dataReg = {'start_time': '', 'end_time': ''}
        self.db_funcs = dbfuncs.DatabaseFuncs(self.bot)

    # Занять переговорку
    def regTime(self, message):
        msg = self.bot.reply_to(message, 'Во сколько тебе нужна переговорка?')
        self.bot.register_next_step_handler(msg, self.regEndTime)

    def regEndTime(self, message):
        self.dataReg['start_time'] = message.text
        if not re.match(r'^[0-9]{0,2}(:|\s)[0-9]{2}', self.dataReg['start_time'].lower()) or not re.match(r'^[0-9]{1,2}', self.dataReg['start_time'].lower()):
            msg = self.bot.reply_to(message, 'Не понял тебя, повтори пожалуйста')
            self.bot.register_next_step_handler(msg, self.regEndTime)
        self.bot.reply_to(message.chat.id, 'До скольки тебе нужна переговорка?')
        self.bot.register_next_step_handler(message, self.endRegTime)

    def endRegTime(self, message):
        self.dataReg['end_time'] = message.text
        if not re.match(r'^[0-9]{0,2}(:|\s)[0-9]{2}', self.dataReg['start_end'].lower()) or not re.match(r'^[0-9]{1,2}', self.dataReg['start_end'].lower()):
            msg = self.bot.reply_to(message, 'Не понял тебя, повтори пожалуйста')
            self.bot.register_next_step_handler(msg, self.regEndTime)

        self.bot.send_message(message.chat.id, 'Добавил запись на ' + self.dataReg['start_time'] + " - " + self.dataReg['end_time'])
        self.db_funcs.addToTimetable(message, self.dataReg)

    # Моя занятость
    def printMyTimes(self, message, today):
        result_list = '@' + message.from_user.username + ', занятость на ' + today.strftime('%d.%m.%y') + '\n\n'
        data = self.db_funcs.getMyTimes(self.db_funcs.getUserId(message), today.day)
        counter = 1
        if len(data) > 0:
            for row in data:
                result_list += str(counter) + '. ' + str(row[3]).strip() + ' - ' + str(row[4]).strip() + '\n'
                counter += 1
        else:
            result_list += 'Твой список занятости пуст'

        self.bot.send_message(message.chat.id, result_list)

    # Занятость переговорки на сегодня
    def printAllTimes(self, message, today):
        result_list = 'Занятость на ' + today.strftime('%d.%m.%y') + '\n\n'
        data = self.db_funcs.getAllTimes(today.day)
        counter = 1
        if len(data) > 0:
            for row in data:
                result_list += str(counter) + '. ' + str(row[11]).strip() + ' - ' + str(row[12]).strip() + '  ---  ' \
                               + str(row[2]).strip() + ' ' + str(row[3]).strip() + ' (@' + str(row[1]).strip() + ')\n'
                counter += 1
        else:
            result_list += 'Cписок занятости пуст, успей занять лучшее время ;)'

        self.bot.send_message(message.chat.id, result_list)

    # Справка
    def printHelp(self, message):
        self.bot.send_message(message.chat.id, 'Привет, ' + message.from_user.username + '!\n\n'
                                               'Список команд:\n'
                                               '/start\n/keyboard\n/help\n/add\n/delete\n/all\n/my\n/time\n/snow\n\n'
                                               'Версия бота: 0.7.11, 13.02.2020\n')

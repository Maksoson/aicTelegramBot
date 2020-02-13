from functions import dbfuncs
import datetime


class BotFuncs:

    def __init__(self, bot):
        self.bot = bot
        self.dataReg = {'start_time': '', 'end_time': ''}
        self.db_funcs = dbfuncs.DatabaseFuncs(self.bot)

    # Занять переговорку
    def regTime(self, message):
        self.bot.send_message(message.chat.id, 'Когда тебе нужна переговорка?')
        self.bot.register_next_step_handler(message, self.regEndTime)

    def regEndTime(self, message):
        self.dataReg['start_time'] = message.text
        self.bot.send_message(message.chat.id, 'До скольки тебе нужна переговорка?')
        self.bot.register_next_step_handler(message, self.endRegTime)

    def endRegTime(self, message):
        self.dataReg['end_time'] = message.text
        self.db_funcs.addToTimetable(message, self.dataReg)

    # Моя занятость
    def printMyTimes(self, message, today):
        result_list = '@' + message.from_user.username + ', ' + today.strftime('%d.%m.%y') + '\n\n'
        data = self.db_funcs.getMyTimes(self.db_funcs.getUserId(message), today.day)
        counter = 1
        for row in data:
            result_list += str(counter) + '. ' + str(row[3]).strip() + ' - ' + str(row[4]).strip() + '\n'
            counter += 1
        self.bot.send_message(message.chat.id, result_list)

    # Занятость переговорки на сегодня
    def printAllTimes(self, message, today):
        result_list = today.strftime('%d.%m.%y') + '\n\n'
        data = self.db_funcs.getAllTimes(today.day)
        counter = 1
        for row in data:
            user_name = '' if row[1] is None else row[1]
            first_name = '' if row[2] is None else row[2]
            last_name = '' if row[3] is 'None' else row[3]
            print(row[3])
            print(type(row[3]))

            result_list += str(counter) + '. ' + str(row[11]).strip() + ' - ' + str(row[12]).strip() + '; ' \
                           + str(first_name).strip() + ' ' + str(last_name).strip() + ' (@' + str(user_name).strip() + ')\n'
            counter += 1
        self.bot.send_message(message.chat.id, result_list)

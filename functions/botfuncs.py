from functions import dbfuncs


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
    def printMyTimes(self, message, day):
        result_list = ''
        data = self.db_funcs.getMyTimes(self.db_funcs.getUserId(message.from_user.id), day)
        for row in data:
            result_list += str(row) + ';\n'
        self.bot.send_message(message.chat.id, result_list)

    # Занятость переговорки на сегодня
    def printAllTimes(self, message, day):
        result_list = ''
        data = self.db_funcs.getAllTimes(day)
        for row in data:
            result_list += str(row) + ';\n'
        self.bot.send_message(message.chat.id, result_list)

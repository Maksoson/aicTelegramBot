from functions import dbfuncs


class BotFuncs:

    def __init__(self, bot):
        self.bot = bot

    # def get_name(self, message):
    #     global name
    #     name = message.text
    #     self.bot.send_message(message.from_user.id, 'Какая у тебя фамилия?')
    #     self.bot.register_next_step_handler(message, self.get_surname)
    #
    # def get_surname(self, message):
    #     global surname
    #     surname = message.text
    #     self.bot.send_message(message.from_user.id, 'Сколько тебе лет?')
    #     self.bot.register_next_step_handler(message, self.get_age)
    #
    # def get_age(self, message):
    #     global age
    #     age = message.text
    #     keyboard = self.bot.types.InlineKeyboardMarkup(True)
    #     key_yes = self.bot.types.InlineKeyboardButton(text='Да', callback_data='yes')
    #     keyboard.add(key_yes)
    #     key_no = self.bot.types.InlineKeyboardButton(text='Нет', callback_data='no')
    #     keyboard.add(key_no)
    #     question = 'Тебе ' + str(age) + ' лет, тебя зовут ' + name + ' ' + surname + '?'
    #     self.bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

    def regTime(self, message):
        self.bot.send_message(message.chat.id, 'Когда тебе нужна переговорка?')
        self.bot.register_next_step_handler(message, self.regEndTime(message))

    def regEndTime(self, message):
        startTime = message.text
        self.bot.send_message(message.chat.id, 'До скольки тебе нужна переговорка?')
        db_funcs = dbfuncs.DatabaseFuncs(self.bot)
        self.bot.register_next_step_handler(message, db_funcs.addToTimetable(message))



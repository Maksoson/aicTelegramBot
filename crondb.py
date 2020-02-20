import telebot
import bothome
from apscheduler.schedulers.blocking import BlockingScheduler
from functions import dbfuncs


bot_home = bothome.BotHome()
bot = telebot.TeleBot(bot_home.getBot)
scheduler = BlockingScheduler()
db_funcs = dbfuncs.DatabaseFuncs(bot)


@scheduler.scheduled_job('cron', day_of_week='0-6', hour=0, minute=17)
def scheduled_job():
    # db_funcs.deleteOldTimes()
    print('qq')

scheduler.start()

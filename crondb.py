import telebot
import bothome
from apscheduler.schedulers.blocking import BlockingScheduler
from functions import dbfuncs


bot_home = bothome.BotHome()
bot = telebot.TeleBot(bot_home.getBot)
scheduler = BlockingScheduler()
db_funcs = dbfuncs.DatabaseFuncs(bot)


@scheduler.scheduled_job('cron', day_of_week='mon-sun', hour=23, minute=58)
def scheduled_job():
    db_funcs.deleteOldTimes()
    

scheduler.start()

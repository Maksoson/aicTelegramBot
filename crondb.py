import telebot
import config
from apscheduler.schedulers.blocking import BlockingScheduler

import bothome
from functions import dbfuncs


bot_home = bothome.BotHome()
bot = telebot.TeleBot(bot_home.getBot)
scheduler = BlockingScheduler()
db_funcs = dbfuncs.DatabaseFuncs(bot)


@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=23, minutes=59)
def scheduled_job():
    db_funcs.deleteOldTimes()


scheduler.start()

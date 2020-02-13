import telebot
import config
from apscheduler.schedulers.blocking import BlockingScheduler

import bothome
from functions import dbfuncs, botfuncs


bot_home = bothome.BotHome()
bot = telebot.TeleBot(bot_home.getBot)
scheduler = BlockingScheduler()
db_funcs = dbfuncs.DatabaseFuncs(bot)

@scheduler.scheduled_job('interval', minutes=2)
def timed_job():
    print("Otrabotalo")
    db_funcs.deleteOldTimes()


@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=23)
def scheduled_job():
    print("Cron otrabotal")
    db_funcs.deleteOldTimes()


scheduler.start()

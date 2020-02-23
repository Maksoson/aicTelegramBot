import telebot
import bothome
from apscheduler.schedulers.blocking import BlockingScheduler
from functions import dbfuncs


bot_home = bothome.BotHome()
bot = telebot.TeleBot(bot_home.get_bot)
scheduler = BlockingScheduler()
db_funcs = dbfuncs.DatabaseFuncs(bot)


@scheduler.scheduled_job('cron', day_of_week='0-6', hour=22, minute=18)
def scheduled_job():
    db_funcs.delete_old_times()
    print('qq')


scheduler.start()

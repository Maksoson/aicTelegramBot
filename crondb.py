from apscheduler.schedulers.blocking import BlockingScheduler
from functions import dbfuncs, botfuncs


scheduler = BlockingScheduler()

@scheduler.scheduled_job('interval', minutes=2)
def timed_job():
    # print("Otrabotalo")
    db_funcs.deleteOldTimes()


@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=23)
def scheduled_job():
    print("Cron otrabotal")
    db_funcs.deleteOldTimes()


scheduler.start()
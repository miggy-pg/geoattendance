import os
import psycopg2
import pytz
import time
import threading

from datetime import datetime, timedelta
from threading import Thread, Event
from threading import Event as evt
from typing import Callable

from dashboard.models import (
    StudentFeedback,
    EventDay,
    EventActivity,
)
from user.models import User


class TimedCalls(Thread):
    def __init__(self, func: Callable, interval: datetime.now() ) -> None:
        super().__init__()
        self.func = func
        self.interval = interval
        self.stopped = Event()
    
    def cancel(self):
        self.stopped.set()

    def run(self):
        next_call = time.time()
        while not self.stopped.is_set():
            self.func()  # Target activity.
            next_call = next_call + self.interval
            # Block until beginning of next interval (unless canceled).
            self.stopped.wait(next_call - time.time())


def my_function():
    event_day = EventDay.objects.filter(daily_active=True)[0]
    user = User.objects.all()
    FMT = '%H:%M:%S'
    s1 = event_day.daily_login_time.strftime(FMT)
    s2 = event_day.daily_logout_time.strftime(FMT)
    tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
    print('this tdelta', type(tdelta))
    print(type(s1), type(s2))
    for row in user:
        reachable = os.system('ping -n 1 ' + row.ip)
        prevStatus = row.status
        tz_Manila = pytz.timezone('Asia/Manila')
        datetime_Manila = datetime.now(tz_Manila)
        current_time = datetime_Manila.strftime("%H:%M:%S")

        if reachable == 0:
            execute = User.objects.get(user_idnumber=row.user_idnumber)
            execute.status = "Online"
            execute.present = True
            execute.save()
        elif reachable != 0 and row.timeout is None:
            execute = User.objects.get(user_idnumber=row.user_idnumber)
            execute.timeout = current_time
            execute.status = "Offline"
            execute.present = False
            execute.save()
        elif reachable != 0 and row.timeout != None and row.status == 'Online':
            execute = User.objects.get(user_idnumber=row.user_idnumber)
            execute.timeout = current_time
            execute.prev_timeout = execute.timeout
            execute.status = "Offline"
            execute.present = False
            execute.save()
        elif reachable != 0 and prevStatus == 'Offline':
            execute = User.objects.get(user_idnumber=row.user_idnumber)
            execute.status = "Offline"
            execute.save()
        else:
            execute = User.objects.get(user_idnumber=row.user_idnumber)
            execute.status = "Offline"
            execute.present = False
            execute.save()

    for row in user:
        prevStatus = row.status
        tz_Manila = pytz.timezone('Asia/Manila')
        datetime_Manila = datetime.now(tz_Manila)
        current_time = datetime_Manila.strftime("%H:%M:%S")
        timeout_status = ''
        FMT = '%H:%M:%S'
        timeout = row.timeout.strftime(FMT)
        strp_timeout = datetime.strptime(timeout, FMT)

        if strp_timeout is not None:
            if strp_timeout >= datetime.strptime(s2, FMT):
                timeout_status = 'On Time' 
            else: 
                timeout_status = 'Early'
            execute = User.objects.get(user_idnumber=row.user_idnumber)
            execute.timeout_status = timeout_status
            execute.save()
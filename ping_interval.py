#!/usr/bin/python

import os
import psycopg2
from datetime import datetime
import pytz

conn = psycopg2.connect(database="demo", user="postgres", password="admin", host="localhost", port="5432")

cur = conn.cursor()
cur.execute("SELECT  daily_logout_time from dashboard_eventday")
dashboard = cur.fetchall()
dailytimeout = dashboard[0][0]

cur.execute(
    "SELECT user_idnumber, email, user_fname, user_lname,present,ip,status,timeout, prev_timeout,timeout_status from user_user")
rows = cur.fetchall()
for row in rows:
    reachable = os.system('ping -n 1 ' + row[5])
    prevStatus = row[6]
    tz_Manila = pytz.timezone('Asia/Manila')
    datetime_Manila = datetime.now(tz_Manila)
    current_time = datetime_Manila.strftime("%H:%M:%S")
    timeout_status = ''

    if reachable == 0:
        cur.execute(f"UPDATE user_user set status = 'Online', present = 'True' where user_idnumber = '{row[0]}'")
        conn.commit()
    elif reachable != 0 and row[7] is None:
        cur.execute(f"UPDATE user_user set timeout = '{current_time}', status = 'Offline', present = 'False' where user_idnumber = '{row[0]}'")
        conn.commit()
    elif reachable != 0 and row[7] != None and row[6] == 'Online':
        cur.execute(f"UPDATE user_user set timeout = '{current_time}', timeout_status = '{timeout_status}', prev_timeout = '{row[7]}', status = 'Offline', present = 'False' where user_idnumber = '{row[0]}'")
        conn.commit()
    elif reachable != 0 and prevStatus == 'Offline':
        cur.execute(f"UPDATE user_user set status = 'Offline' where user_idnumber = '{row[0]}'")
        conn.commit()
    else:
        cur.execute(f"UPDATE user_user set status = 'Offline', present = 'False' where user_idnumber = '{row[0]}'")
        conn.commit()

cur.execute("SELECT user_idnumber, timeout,prev_timeout from user_user")
rows = cur.fetchall()
for row in rows:
    if row[1] is not None:
        timeout_status = 'On Time' if row[1] >= dailytimeout else 'Early'
        cur.execute(f"UPDATE user_user set timeout_status = '{timeout_status}' where user_idnumber = '{row[0]}'")
        conn.commit()

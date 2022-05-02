#!/usr/bin/python

import os
import psycopg2

conn = psycopg2.connect(database = "postgres", user = "postgres", password = "postgres", host = "db", port = "5432")
print("Opened database successfully")

cur = conn.cursor()
cur.execute("SELECT user_idnumber, email, user_fname, user_lname,present,ip,status from user_user")
rows = cur.fetchall()
for row in rows:
   print("ID = ", row[0])
   print("email = ", row[1])
   print("user_fname = ", row[2])
   print("user_lname = ", row[3])
   print("present = ", row[4])
   print("ip = ", row[5])
   print("status = ", row[6], "\n")
   reachable = os.system('ping -c 1 '+row[5])

   if reachable == 0:
       cur.execute("UPDATE user_user set status = 'Online', present = 'True'  where user_idnumber = '" + row[0] + "'")
       conn.commit()
       print("Total number of rows updated :", cur.rowcount)
   else:
       cur.execute("UPDATE user_user set status = 'Offline', present = 'False'  where user_idnumber = '" + row[0] + "'")
       conn.commit()
       print("Total number of rows updated :", cur.rowcount)

cur.execute("SELECT user_idnumber, email, user_fname, user_lname,present,ip,status from user_user")
rows = cur.fetchall()
for row in rows:
   print("ID = ", row[0])
   print("email = ", row[1])
   print("user_fname = ", row[2])
   print("user_lname = ", row[3])
   print("present = ", row[4])
   print("ip = ", row[5])
   print("status = ", row[6], "\n")

print("Operation done successfully")
conn.close()
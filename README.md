# GeoAttendance
CRONJOB
FOLLOW THE STEPS BELOW
Run docker exec -it geoattendance-dev_web_1 bash
Install cron in docker apt-get install cron
Install nano text editor in docker apt-get install nano
Install python postgres in docker apt-get install python-psycopg2
Run the comman crontab -e
append this on the file * * * * * /usr/local/bin/python /app/ping_interval.py > /app/cron.log 2>&1
NOTE: Do not use ctrl v to paste on the nano text editor. Just right click on the editor to automatically paste the copied text

Run cron command to start the cron job
NOTE: refresh is needed in the admin page or in the attendance page to see the changes of the status
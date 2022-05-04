1. Since database flush and migrate commands are commented in entrypoint.sh script, you can run them manually, after the containers spin up, like so:

docker-compose exec web python manage.py flush --no-input
docker-compose exec web python manage.py migrate

2. Build the production images and spin up the containers:

docker-compose -f docker-compose.prod.yml up -d --build

3. Update the file permissions locally:

chmod +x app/entrypoint.prod.sh

4. Try out the docker-compose prod docker:

$ docker-compose -f docker-compose.prod.yml down -v
$ docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
$ docker-compose -f docker-compose.prod.yml up -d --build
$ docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear

$ docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

5. To test:

Upload an image at http://localhost:1337/.
Then, view the image at http://localhost:1337/media/IMAGE_FILE_NAME.


'' Commands to bash ''
$ docker exec -it < container-id/ name > ip addr
$ docker exec -it < container-id/ name > //bin/sh
$ docker exec -it geoattendance_web_1 //bin/sh


'' Dive into your container ''
:/web$  ls -la

'' Simple way to Reload Nginx in Docker container ''
$ docker exec -it {container_name} nginx -s reload
$ docker exec -it geoattendance_nginx_1 nginx -s reload

# Pull portainer
docker pull portainer/portainer

# Start portiner
sudo docker run -d -p 9000:9000 -v /var/run/docker.sock:/var/run/docker.sock portainer/portainer


# Start portainer
sudo docker start portainer

# Stop portainer
sudo docker stop portainer

#
docker network create \
--subnet=192.168.1.0/24 \
--ip-range=192.168.1.0/24d \ 
--gateway=192.168.1.150 \
--attachable \
-o"com.docker.network.bridge.name"="br0" \
-o"com.docker.network.bridge.default_bridge"="true" \
-o"com.docker.network.bridge.enable_icc"="true"\
-o"com.docker.network.bridge.enable_ip_masquerade"="false" \
-o"com.docker.network.bridge.host_binding_ipv4"="0.0.0.0" \
-o"com.docker.network.driver.mtu"="1500" \
mynet192

# CRONJOB
FOLLOW THE STEPS BELOW
Run docker exec -it geoattendance-dev_web_1 bash
Install cron in docker apt-get install cron
Install nano text editor in docker apt-get install nano
Install python postgres in docker apt-get install python-psycopg2
Run the command crontab -e
append this on the file * * * * * /usr/local/bin/python /app/ping_interval.py > /app/cron.log 2>&1
NOTE: Do not use ctrl v to paste on the nano text editor. Just right click on the editor to automatically paste the copied text

Run cron command to start the cron job
NOTE: refresh is needed in the admin page or in the attendance page to see the changes of the status
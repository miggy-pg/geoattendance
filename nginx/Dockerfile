FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p /var/www/media
RUN mkdir -p /var/www/static

WORKDIR /var/www/media
RUN chown -R nginx:nginx /var/www/media

WORKDIR /var/wwww/static
RUN chown -R nginx:nginx /var/www/static
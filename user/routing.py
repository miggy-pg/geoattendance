from django.conf.urls import url

from user.consumers import NewUserConsumer


websocket_urlpatterns = [
    url('ws/new_user/', NewUserConsumer.as_asgi()),
]

"""
ASGI config for smartattendance project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""
import os
import user 

from channels.auth import AuthMiddlewareStack
from channels.routing import (
    ProtocolTypeRouter, 
    URLRouter
)
from django.core.asgi import get_asgi_application

from user.routing import websocket_urlpatterns


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "captiveportal.settings")

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        URLRouter(
            user.routing.websocket_urlpatterns
        )
    ),
})

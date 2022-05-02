from django.conf.urls import url

from user import views
from user.views import (
    LoginView, 
    RegisterView
)


urlpatterns = [
    url(r'register/$', RegisterView.as_view(), name='register'),
    url(r'login/$', LoginView.as_view(), name='login'),
    url(r'logout/$', views.logoutUser, name='logout'),
]
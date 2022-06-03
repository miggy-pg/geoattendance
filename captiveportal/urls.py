from django.contrib import admin
from django.conf.urls import (
    include,
    url
)
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from user import views


urlpatterns = [
    url(r"admin/", admin.site.urls),    
    path("", views.index, name="index"),
    url(r"user/", include("user.urls"), name="user"),
    url(r"dashboard/", include("dashboard.urls"), name="dashboard"),
    url(r"students", csrf_exempt(views.students), name="students"),


]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG: 
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
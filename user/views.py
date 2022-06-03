import json
import os 
import platform
import subprocess

from django.contrib.auth.decorators import login_required
from django.contrib.auth import (
    authenticate, 
    login, 
    get_user_model, 
    logout
)
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.views.generic import (
    CreateView, 
    FormView
)

from user.decorators import student_only
from dashboard.models import (
    StudentFeedback, 
    Event, 
    EventDay,
    EventActivity,
)
from dashboard.views import student_feedback
from user.forms import (
    LoginForm, 
    RegisterForm
)
from user.models import (
    Attendance, 
    User
)


@login_required(redirect_field_name=None)
def students(request): 
    if request.method == 'GET':
        students = User.objects.all()
        data = students.values()
        return JsonResponse(list(data), safe=False)
        

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required(redirect_field_name=None)
def index(request):
    ip = get_client_ip(request)

    name = request.user
    print("IP", ip, 'Name', name)
    event_info = Event.objects.filter(Q(event_active='True'))

    get_eventday = EventDay.objects.filter(Q(activity_active='True'))
    print('this eventday', get_eventday)

    get_activity = EventActivity.objects.filter(event_day__activity_active=True)
    print('this activity', get_activity)

    all_activity = EventActivity.objects.all()
    print('this all activity', all_activity)

    all_eventday = EventDay.objects.all()
    print('this all eventday', all_eventday)
    
    all_offline = User.objects.filter(status="Offline")
    print('this all offline', all_offline)

    if request.user.is_authenticated:
        User.objects.filter(user_idnumber=request.user.user_idnumber).update(present=True)
        User.objects.filter(user_idnumber=request.user.user_idnumber).update(ip=ip)
    else:
        User.objects.filter(user_idnumber=request.user.user_idnumber).update(present=False)

    if request.method == "POST":
        if request.user.is_authenticated:
            input_user = StudentFeedback(student_id=request.user)
            if request.POST.get('feedback') :
                input_user.student_feedback = request.POST.get('feedback')
            input_user.save()

    context = {
        'get_activity': get_activity,
        'get_eventday': get_eventday,
        'event_info': event_info,
    }
    return render(request, 'users/index.html', context)


class LoginView(FormView):
    template_name = 'users/login.html'
    form_class = LoginForm
    success_url = '/'
    redirect_authenticated_user = True

    def form_valid(self, form):
        request = self.request 
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None

        user_idnumber = form.cleaned_data.get("user_idnumber")
        password = form.cleaned_data.get("password")
        user = authenticate(
            request,
            username=user_idnumber, 
            password=password
            )
        if user is not None:
            login(request, user)
            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)
            else:
                return redirect("/")
        return super(LoginView, self).form_invalid(form)


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'users/register.html'
    success_url = '/user/login/'


def logoutUser(request):
    logout(request)
    return redirect('login')


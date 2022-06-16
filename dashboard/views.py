import csv
from datetime import datetime, timedelta
import time
import json
import os


from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q
from django.http import (
    request,
    response,
    HttpResponseRedirect,
    JsonResponse,
    HttpResponse,
    HttpResponseNotAllowed,
    Http404,
)
from django.forms.forms import Form
from django.shortcuts import (
    redirect, 
    render, 
    get_object_or_404
)
from django.template import RequestContext
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response

from dashboard.models import (
    Event,
    StudentFeedback,
    EventDay,
    EventActivity,
)
from dashboard.forms import (
    EventScheduleForm,
    EventTimeTableForm,
    EventDailyActivity,
)
from user.models import User
from dashboard.filters import StudentFilter
from .thread import TimedCalls, my_function

User = get_user_model()

@login_required(login_url="login")
def dashboard(request):
    event = Event.objects.filter(Q(event_active='True'))
    event_day = EventDay.objects.filter(Q(daily_active='True'))
    daily_schedule = EventActivity.objects.filter(event_day__daily_active=True)

    start_time = datetime.now() + timedelta(seconds=2)
    run_time = timedelta(minutes=20)  # How long to iterate function.
    end_time = start_time + run_time

    assert start_time > datetime.now()
    timed_calls = TimedCalls(my_function, 60)  # Thread to call function every 10 secs.

    print(f'waiting until {start_time.strftime("%H:%M:%S")} to begin...')
    wait_time = start_time - datetime.now()
    time.sleep(wait_time.total_seconds())

    print('starting')
    timed_calls.start()  # Start thread.
    while datetime.now() < end_time:
        time.sleep(1)  # Twiddle thumbs while waiting.
    print('done')
    timed_calls.cancel()

    # day_event = EventDay.objects.filter(event_name__event_active=True)[0]
    # print('this day_event', day_event)
    # print('this day_event login and logout time', day_event.daily_login_time, day_event.daily_logout_time)
    
    context = {
        "event": event, 
        "daily_schedule": daily_schedule, 
        "event_day": event_day
        }
    return render(request, "dashboard/dashboard.html", context)


@login_required(login_url="login")
def attendance(request):
    return render(request, "dashboard/attendance.html")


class DataView(View):
    def get(self, request, *awgs, **kwargs):
        return render(request, "dashboard/data-presentation.html")


class ChartData(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        qbar_seven = User.objects.filter(yearlevel__icontains=7).count()
        qbar_eight = User.objects.filter(yearlevel__icontains=8).count()
        qbar_nine = User.objects.filter(yearlevel__icontains=9).count()
        qbar_ten = User.objects.filter(yearlevel__icontains=10).count()
        qbar_eleven = User.objects.filter(yearlevel__icontains=11).count()
        qbar_twelve = User.objects.filter(yearlevel__icontains=12).count()
        labels_bar = ["Grade 7", "Grade 8", "Grade 9", "Grade 10", "Grade 11", "Grade 12"]
        items_bar = [qbar_seven, qbar_eight, qbar_nine, qbar_ten, qbar_eleven, qbar_twelve]

        # qpie_bsit = User.objects.filter(course__icontains="BSIT").count()
        # qpie_bsis = User.objects.filter(course__icontains="BSIS").count()
        # qpie_bsca = User.objects.filter(course__icontains="BSCA").count()
        # qpie_bscs = User.objects.filter(course__icontains="BSCS").count()
        labels_pie = ["BSIT", "BSIS", "BSCA", "BSCS"]
        # items_pie = [qpie_bsit, qpie_bsis, qpie_bsca, qpie_bscs]

        # qline_early = User.objects.filter(status__icontains="Early").count()
        # qline_late = User.objects.filter(status__icontains="Late").count()
        # labels_line = ["Red", "Green", "Blue", "Orange"]
        # labels_line_early = ["Early"]
        # labels_line_late = ["Late"]
        # items_line_early = [1,5,20,40,50,60]
        # items_line_late = [10,20,1,15,20,30]


        start = ''
        end = ''
        if EventActivity.objects.filter(event_day__activity_active=True):
            event = EventDay.objects.filter(activity_active__icontains=True)
            for time in event:
                print(time.daily_login_time)
                print(time.daily_logout_time)
                start = datetime.strptime(str(time.daily_login_time), "%H:%M:%S").strftime("%H:%M:%S")
                end = datetime.strptime(str(time.daily_logout_time), "%H:%M:%S").strftime("%H:%M:%S")
                print('this start:' + str(start) + 'this end:' + str(end))
            # print('this eventday', event)

        delta = timedelta(minutes=5)
        start = datetime.strptime(str(start), '%H:%M:%S' )
        end = datetime.strptime(str(end), '%H:%M:%S' )
        t = start

        time = []
        while t <= end :
            t = t + delta
            time.append(t)

        time = list(datetime.strftime(i,'%H:%M:%S') for i in time)
        # # min_gap

        data = {
            "labels_bar": labels_bar,
            "items_bar": items_bar,
            # "labels_pie": labels_pie,
            # "items_pie": items_pie,
            "labels_line": time,
            # "labels_line_early": labels_line_early,
            # "labels_line_late": labels_line_late,
            # "items_line_early": items_line_early,
            # "items_line_late": items_line_late,
        }
        return Response(data)


@login_required(login_url="login")
def student_feedback(request):
    feedback_list = StudentFeedback.objects.all().order_by("student_id")
    paginator = Paginator(feedback_list, 10)
    page_number = request.GET.get("page")
    student_feedback = paginator.get_page(page_number)
    context = {"student_feedback": student_feedback}
    return render(request, "dashboard/student_feedback.html", context)


@login_required(login_url="login")
def create_event(request):
    if request.method == "POST":
        event_form = EventScheduleForm(request.POST, request.FILES)
        if event_form.is_valid():
            messages.add_message(
                request, messages.SUCCESS, "A new event has been added!"
            )
            event_form.save()
            return redirect("create_event")
    else:
        event_form = EventScheduleForm()

    context = {"event_form": event_form}
    return render(request, "dashboard/event/create_event.html", context)


@login_required(login_url="login")
def view_event(request):
    is_active = False
    event_list = Event.objects.all().order_by("-event_name")
    paginator = Paginator(event_list, 8)
    page_number = request.GET.get("page")
    event_data = paginator.get_page(page_number)

    context = {
        "is_active": is_active,
        "event_list": event_list,
        "event_data": event_data,
    }
    return render(request, "dashboard/event/view_event.html", context)


def active_event_view(request, event_id):
    is_active = False
    event_info = get_object_or_404(Event, id=request.POST.get("id"))
    if event_info.event_active is False:
        event_info.event_active = True
        event_info.save()
        is_active = True
    else:
        is_active = False

    if request.is_ajax():
        html = render_to_string(
            "dashboard/event/view_event.html", context, request=request
        )
    return JsonResponse({"form": html})


@login_required(login_url="login")
def delete_event(request, event_id):
    Event.objects.get(id=event_id).delete()
    return HttpResponseRedirect("/dashboard/view-event")


@login_required(login_url="login")
def edit_event(request, event_id):
    try:
        event = Event.objects.get(pk=event_id)
        event_form = EventScheduleForm(instance=event)

        if request.method == "POST":
            event_form = EventScheduleForm(request.POST, instance=event)
            if event_form.is_valid():
                event_form.save()
                return redirect("view_event")
    except Event.DoesNotExist:
        raise Http404("Event does not exist")

    context = {
        "event": event,
        "event_form": event_form
    }
    return render(request, "dashboard/event/edit_event.html", context)

@login_required(login_url="login")
def event_details(request, event_id):
    event = Event.objects.filter(Q(event_active='True'))
    activity = EventDay.objects.filter(event_name=event[0]).filter(daily_active=True)[0]
    # user = User.objects.filter(event_name__event_day__isnull=False)

    context = {
        # "user": user,
        "event": event,
        "activity": activity,
    }
    return render(request, "dashboard/event/event_details.html")

# Buttons to disable/enable event
def active_event_view(request, event_id):
    event_info = Event.objects.get(pk=event_id)
    if event_info.event_active is False:
        event_info.event_active = True
        event_info.save()
    return HttpResponseRedirect(reverse("view_event"))


def inactive_event_view(request, event_id):
    event_info = Event.objects.get(pk=event_id)
    if event_info.event_active is True:
        event_info.event_active = False
        event_info.save()
    return HttpResponseRedirect(reverse("view_event"))


@login_required(login_url="login")
def create_activity(request):
    event_list = EventDay.objects.all().order_by("-event_name")
    paginator = Paginator(event_list, 8)
    page_number = request.GET.get("page")
    event_name_data = paginator.get_page(page_number)

    if request.method == "POST":
        event_daily_form = EventDailyActivity(request.POST)
        if event_daily_form.is_valid():
            messages.add_message(
                request, messages.SUCCESS, "A new activity has been added!"
            )
            event_daily_form.save()
            return redirect("create_activity")
    else:
        event_daily_form = EventDailyActivity()

    context = {"event_name_data": event_name_data, "event_daily_form": event_daily_form}
    return render(request, "dashboard/activity/create_activity.html", context)


@login_required(login_url="login")
def delete_activity(request, daily_event_id):
    EventDay.objects.filter(id=daily_event_id).delete()
    return HttpResponseRedirect("/dashboard/view-activity")


@login_required(login_url="login")
def edit_activity(request, daily_event_id):
    try:
        event_day = EventDay.objects.get(pk=daily_event_id)
        event_daily_form = EventDailyActivity(instance=event_day)
        if request.method == "POST":
            event_daily_form = EventDailyActivity(request.POST, instance=event_day)
            if event_daily_form.is_valid():
                event_daily_form.save()
                return redirect("view_activity")
    except EventDay.DoesNotExist:
        raise Http404("Event date does not exist")

    context = {
        "event_day": event_day,
        "event_daily_form": event_daily_form
        }
    return render(request, "dashboard/activity/edit_activity.html", context)


@login_required(login_url="login")
def view_activity(request):
    activity_list = EventDay.objects.all().order_by("-event_name")
    paginator = Paginator(activity_list, 9)
    page_number = request.GET.get("page")
    event_day_data = paginator.get_page(page_number)
    context = {"event_day_data": event_day_data}
    return render(request, "dashboard/activity/view_activity.html", context)


def active_activity_view(request, activity_id):
    activity_info = EventDay.objects.get(pk=activity_id)
    if activity_info.daily_active is False:
        activity_info.daily_active = True
        activity_info.save()
    return HttpResponseRedirect(reverse("view_activity"))


def inactive_active_view(request, activity_id):
    activity_info = EventDay.objects.get(pk=activity_id)
    if activity_info.daily_active is True:
        activity_info.daily_active = False
        activity_info.save()
    return HttpResponseRedirect(reverse("view_activity"))


@login_required(login_url="login")
def create_timetable(request, pk):
    event_day = EventDay.objects.get(id=pk)
    event_name = EventActivity.objects.filter(event_day=event_day)
    form = EventTimeTableForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            timetable = form.save(commit=False)
            timetable.event_day = event_day
            timetable.save()
            return redirect("detail_timetable", pk=timetable.id)
        else:
            return render(
                request,
                "dashboard/event/partials/timetable_form.html",
                {
                    "form": form,
                    "event_day": event_day,
                },
            )

    context = {"form": form, "event_day": event_day, "event_name": event_name}
    return render(request, "dashboard/event/create_timetable.html", context)


@login_required(login_url="login")
def update_timetable(request, pk):
    timetable = EventActivity.objects.get(id=pk)
    form = EventTimeTableForm(request.POST or None, instance=timetable)

    if request.method == "POST":
        if form.is_valid():
            timetable = form.save()
            return redirect("detail_timetable", pk=timetable.pk)

    context = {"form": form, "timetable": timetable}
    return render(request, "dashboard/event/partials/timetable_form.html", context)


@login_required(login_url="login")
def create_timetable_form(request):
    context = {"form": EventTimeTableForm()}
    return render(request, "dashboard/event/partials/timetable_form.html", context)

def remove_timetable_form(request):
    return HttpResponse("")
    
@login_required(login_url="login")
def detail_timetable(request, pk):
    timetable = get_object_or_404(EventActivity, id=pk)

    context = {"timetable": timetable}
    return render(request, "dashboard/event/partials/timetable_details.html", context)


@login_required(login_url="login")
@csrf_exempt
def delete_timetable(request, pk):
    timetable = get_object_or_404(EventActivity, id=pk)

    if request.method == "POST":
        timetable.delete()
        return HttpResponse("")
    return HttpResponseNotAllowed(
        [
            "POST",
        ]
    )

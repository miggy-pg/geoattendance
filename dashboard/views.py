import csv
from datetime import datetime, timedelta
import json
import os

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib import messages
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
    EventCategory,
    EventActivity,
)
from dashboard.forms import (
    EventScheduleForm,
    EventTimeTableForm,
    EventDailyActivity,
    CategoryForm,
    AdminForm,
)
from user.models import User
from dashboard.filters import StudentFilter


User = get_user_model()

@login_required(login_url="login")
def search_students(request):
    if request.method == "POST":
        search_str = json.loads(request.body).get("searchText")
        students = (
            User.objects.filter(user_fname__icontains=search_str)
            | User.objects.filter(user_lname__icontains=search_str)
            | User.objects.filter(user_idnumber__istartswith=search_str)
            | User.objects.filter(email__icontains=search_str)
        )
        data = students.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url="login")
def dashboard(request):
    event = Event.objects.all()
    event_day = EventDay.objects.all()
    daily_schedule = EventActivity.objects.all()
    context = {"event": event, "daily_schedule": daily_schedule, "event_day": event_day}
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
        qbar_first = User.objects.filter(yearlevel__icontains=1).count()
        qbar_second = User.objects.filter(yearlevel__icontains=2).count()
        qbar_third = User.objects.filter(yearlevel__icontains=3).count()
        qbar_fourth = User.objects.filter(yearlevel__icontains=4).count()
        qbar_others = User.objects.filter(yearlevel__icontains=5).count()
        labels_bar = ["First Year", "Second Year", "Third Year", "Fouth Year", "Others"]
        items_bar = [qbar_first, qbar_second, qbar_third, qbar_fourth, qbar_others]

        qpie_bsit = User.objects.filter(course__icontains="BSIT").count()
        qpie_bsis = User.objects.filter(yearlevel__icontains="BSIS").count()
        qpie_bsca = User.objects.filter(yearlevel__icontains="BSCA").count()
        qpie_bscs = User.objects.filter(yearlevel__icontains="BSCS").count()
        labels_pie = ["BSIT", "BSIS", "BSCA", "BSCS"]
        items_pie = [qpie_bsit, qpie_bsis, qpie_bsca, qpie_bscs]

        # qline_early = User.objects.filter(status__icontains="Early").count()
        # qline_late = User.objects.filter(status__icontains="Late").count()
        labels_line = ["Red", "Green", "Blue", "Orange"]
        labels_line_early = ["Early"]
        labels_line_late = ["Late"]
        items_line_early = [1,5,20,40,50,60]
        items_line_late = [10,20,1,15,20,30]
        

        # start = datetime.strptime("0 7:00:00", "%H:%M:%S")
        # end = datetime.strptime("17:00:00", "%H:%M:%S")
        
        # # min_gap
        # min_gap = 5

        # # compute datetime interval
        # arr = [(start + timedelta(hours=min_gap*i/60)).strftime("%H:%M:%S")
        #     for i in range(int((end-start).total_seconds() / 60.0 / min_gap))]
        # print(arr)

        if EventActivity.objects.filter(event_day__activity_active=True):
            event = EventDay.objects.filter(activity_active__icontains=True)
            for time in event:
                print(time.daily_login_time)
                print(time.daily_logout_time)
            print('this eventday', event)
        # EventDaydaily_logout_time

        data = {
            "labels_bar": labels_bar,
            "items_bar": items_bar,
            "labels_pie": labels_pie,
            "items_pie": items_pie,
            "labels_line": labels_line,
            "labels_line_early": labels_line_early,
            "labels_line_late": labels_line_late,
            "items_line_early": items_line_early,
            "items_line_late": items_line_late,
        }
        return Response(data)


@login_required(login_url="login")
def student_record(request):
    studentFilter = StudentFilter()

    user_list = User.objects.all().order_by("user_idnumber")
    paginator = Paginator(user_list, 10)
    page_number = request.GET.get("page")
    users = paginator.get_page(page_number)
    context = {"users": users, "studentFilter": studentFilter}
    return render(request, "dashboard/student-record.html", context)


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
def delete_event(event_id):
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

    context = {"event": event, "event_form": event_form}
    return render(request, "dashboard/event/edit_event.html", context)

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
def create_category(request):
    if request.method == "POST":
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            messages.add_message(
                request, messages.SUCCESS, "A new category has been added!"
            )
            category_form.save()
            return redirect("create_category")
    else:
        category_form = CategoryForm()

    context = {"category_form": category_form}
    return render(request, "dashboard/category/create_category.html", context)


@login_required(login_url="login")
def view_category(request):
    category_list = EventCategory.objects.all().order_by("-category_name")
    paginator = Paginator(category_list, 9)
    page_number = request.GET.get("page")
    category_data = paginator.get_page(page_number)
    context = {"category_data": category_data}
    return render(request, "dashboard/category/view_category.html", context)


@login_required(login_url="login")
def delete_category(request, category_id):
    EventCategory.objects.filter(id=category_id).delete()
    return HttpResponseRedirect("/dashboard/view-category")


@login_required(login_url="login")
def edit_category(request, category_id):
    try:
        category = EventCategory.objects.get(pk=category_id)
        category_form = CategoryForm(instance=category)

        if request.method == "POST":
            category_form = CategoryForm(request.POST, instance=category)
            if category_form.is_valid():
                category_form.save()
                return redirect("view_category")
    except EventCategory.DoesNotExist:
        raise Http404("Event does not exist")

    context = {"category": category, "category_form": category_form}
    return render(request, "dashboard/category/edit_category.html", context)


@login_required(login_url="login")
def create_admin(request):
    admin_context = AdminForm()

    if request.method == "POST":
        admin_context = AdminForm(request.POST)

        if admin_context.is_valid():
            admin_context.save()
            messages.success(request, "Admin has been added!")
            return redirect("create_admin")

    context = {
        "admin_context": admin_context
    }
    return render(request, "dashboard/admin/create_admin.html", context)


@login_required(login_url="login")
def view_admin(request):
    admin_list = User.objects.all().order_by("-date_joined")
    paginator = Paginator(admin_list, 10)
    page_number = request.GET.get("page")
    admin_data = paginator.get_page(page_number)
    context = {
        "admin_data": admin_data
    }
    return render(request, "dashboard/admin/view_admin.html", context)


@login_required(login_url="login")
def delete_admin(request,admin_id):
    User.objects.filter(id=admin_id).delete()
    return HttpResponseRedirect("/dashboard/view-admin-user/")


@login_required(login_url="login")
def edit_admin(request, admin_id):
    try:
        admin = User.objects.get(pk=admin_id)
        admin_form = AdminForm(instance=admin)

        if request.method == "POST":
            admin_form = AdminForm(request.POST, instance=admin)
            if admin_form.is_valid():
                admin_form.save()
                return redirect("view_admin")
    except admin.DoesNotExist:
        raise Http404("Admin does not exist")

    context = {
        "admin": admin, 
        "admin_form": admin_form
    }

    return render(request, "dashboard/admin/edit_admin.html", context)


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
                request, messages.SUCCESS, "A new event has been added!"
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

    context = {"event_day": event_day, "event_daily_form": event_daily_form}
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
    if activity_info.activity_active is False:
        activity_info.activity_active = True
        activity_info.save()
    return HttpResponseRedirect(reverse("view_activity"))


def inactive_active_view(request, activity_id):
    activity_info = EventDay.objects.get(pk=activity_id)
    if activity_info.activity_active is True:
        activity_info.activity_active = False
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

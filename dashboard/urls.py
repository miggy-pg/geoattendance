from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path

from dashboard import views
from dashboard.views import DataView
from dashboard.views import ChartData


urlpatterns = [
    url(r"^$", views.dashboard, name="dashboard"),
    url(r"^attendance/", views.attendance, name="attendance"),
    url(r"^data-presentation", DataView.as_view(), name="data_presentation"),
    url(r"^api/chart", ChartData.as_view()),
    url(r"^student-feedback/", views.student_feedback, name="student_feedback"),

    url(r"^create-event/", views.create_event, name="create_event"),
    url(r"^view-event/", views.view_event, name="view_event"),
    path("event-details/<int:event_id>/", views.event_details, name="event_details"),
    path("delete-event/<int:event_id>/", views.delete_event, name="delete_event"),
    path("edit-event/<int:event_id>/", views.edit_event, name="edit_event"),

    path("create-activity/", views.create_activity, name="create_activity"),
    path("delete-activity/<int:daily_event_id>",views.delete_activity,name="delete_activity"),
    path("edit-activity/<int:daily_event_id>", views.edit_activity, name="edit_activity"),
    path("view-activity/", views.view_activity, name="view_activity"),
    path("create-activity/<pk>/", views.create_timetable, name="create_timetable"),

    path("htmx/create-timetable/<pk>/", views.detail_timetable, name="detail_timetable"),
    path("htmx/create-timetable-form/", views.create_timetable_form, name="create_timetable_form"),
    path("htmx/remove-timetable-form/", views.remove_timetable_form, name="remove_timetable_form"),
    path("htmx/create-timetable/<pk>/delete/", views.delete_timetable, name="delete_timetable"),
    path("htmx/create-timetable/<pk>/update/", views.update_timetable, name="update_timetable"),

    path("active-event/<int:event_id>", views.active_event_view, name="active_event"),
    path("inactive-event/<int:event_id>", views.inactive_event_view, name="inactive_event"),
    path("active-activity/<int:activity_id>", views.active_activity_view, name="active_activity"),
    path("inactive-activity/<int:activity_id>", views.inactive_active_view, name="inactive_activity"),
]

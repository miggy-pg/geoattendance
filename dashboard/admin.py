from django.db.models.base import Model
from django.contrib import admin

from dashboard.models import (
    Event,
    EventActivity,
    EventDay,
    StudentFeedback
)


class EventScheduleAdmin(admin.ModelAdmin):
    list_display = [
        "event_photo",
        "event_name",
        "event_venue",
        "event_start",
        "event_end",
    ]


class EventActivityInLineAdmin(admin.TabularInline):
    model = EventActivity


class StudentFeedbackAdmin(admin.ModelAdmin):
    list_display = ["student_id", "student_sent", "student_feedback"]


class EventDayAdmin(admin.ModelAdmin):
    inlines = [EventActivityInLineAdmin]


admin.site.register(EventDay, EventDayAdmin)
admin.site.register(Event, EventScheduleAdmin)
admin.site.register(StudentFeedback, StudentFeedbackAdmin)

from django.db.models.base import Model
from django.contrib import admin

from dashboard.models import (
    Event,
    EventActivity,
    EventDay,
    EventCategory,
    StudentFeedback
)



class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ["category_name", "category_status"]


class EventScheduleAdmin(admin.ModelAdmin):
    list_display = [
        "event_photo",
        "event_name",
        "event_venue",
        "event_category",
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
admin.site.register(EventCategory, EventCategoryAdmin)
admin.site.register(Event, EventScheduleAdmin)
admin.site.register(StudentFeedback, StudentFeedbackAdmin)

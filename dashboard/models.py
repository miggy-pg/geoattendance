from django.contrib.auth.models import User
from django.db import models
from django.db.models.base import Model
from django.utils.safestring import mark_safe

from captiveportal import settings


class Event(models.Model):
    event_name = models.CharField(
        max_length=50, 
        verbose_name="Event Name", 
        blank=False
    )
    event_venue = models.CharField(
        max_length=75, 
        verbose_name="Location", 
        blank=False
    )
    event_logo = models.ImageField(
        verbose_name="Event Logo", 
        upload_to="mediafiles", 
        default="media/default_image.jpg"
    )
    event_start = models.DateField(
        auto_now_add=False, 
        auto_now=False, 
        verbose_name="Start Date", 
        blank=False
    )
    event_end = models.DateField(
        auto_now_add=False, 
        auto_now=False, 
        verbose_name="End Date", 
        blank=False
    )
    event_active = models.BooleanField(
        default=False,
        verbose_name="Enable"    
    )

    class Meta:
        verbose_name_plural = "Event"

    def __str__(self):
        return self.event_name

    def get_event_date(self):
        if self.event_start:
            return str(self.event_start) + " to " + str(self.event_end)

    def event_photo(self):
        return mark_safe(
            '<img src="{}" width="50" height="50" />'.format(self.event_logo.url)
        )

    event_photo.allow_tags = True

    def clean(self):
        self.event_name = self.event_name.upper()
        self.event_venue = self.event_venue.upper()


class EventDay(models.Model):
    event_name = models.ForeignKey(
        Event, 
        null=True, 
        on_delete=models.SET_NULL
    )
    event_day = models.DateField(
        auto_now_add=False, 
        auto_now=False, 
        null=True, 
        blank=False, 
        verbose_name="Date"
    )
    daily_login_time = models.TimeField(blank=False)
    daily_logout_time = models.TimeField(blank=False)
    daily_active = models.BooleanField(
        default=False,
        verbose_name="Enable"    
    )
    activity_active = models.BooleanField(
        default=False,
    )

    class Meta:
        verbose_name_plural = "Event Day"

    def __str__(self):
        return str(self.event_day) + " " + str(self.event_name) 


class EventActivity(models.Model):
    event_day = models.ForeignKey(
        EventDay, 
        null=True, 
        on_delete=models.SET_NULL
    )
    event_start_time = models.TimeField(blank=False)
    event_end_time = models.TimeField(blank=False)
    event_activity = models.CharField(
        max_length=40, 
        verbose_name="Activity", 
        blank=False
    )

    class Meta:
        verbose_name_plural = "Event Activity"

    def __str__(self):
        return str(self.event_day)


class StudentFeedback(models.Model):
    User = settings.AUTH_USER_MODEL
    student_id = models.OneToOneField(User, on_delete=models.CASCADE)
    student_sent = models.DateTimeField(auto_now_add=True)
    student_feedback = models.TextField(
        max_length=175, 
        blank=False
    )

    class Meta:
        verbose_name_plural = "Student Feedback"

    def __str__(self):
        return (
            str(self.student_id.user_idnumber) + " " + str(self.student_id.student_id)
        )

from django.db.models import fields
from django import forms
from django.db import models
from django.forms.widgets import DateInput
from django.forms import (
    inlineformset_factory, 
    ModelChoiceField
)

from user.models import User
from dashboard.models import (
    Event,
    StudentFeedback,
    EventActivity,
    EventDay,
    EventCategory,
)


STATUS_CHOICES = (
    (1, ("Disabled")),
    (2, ("Active")),
    (3, ("Deleted")),
    (4, ("Blocked")),
    (5, ("Completed")),
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = EventCategory
        fields = ["category_name", "category_status"]

    def clean(self):
        try:
            EventCategory.objects.get(category_name=self.cleaned_data["category_name"])
            raise forms.ValidationError(
                "This category name already exist. Please try another one!"
            )
        except EventCategory.DoesNotExist:
            pass
        return self.cleaned_data

    def clean_category_name(self):
        return self.cleaned_data["category_name"].capitalize()

    def __str__(self):
        return self.category_name

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)

        self.fields["category_name"].widget.attrs.update({"class": "choice-field"})
        self.fields["category_status"].widget.attrs.update({"class": "input-field"})


class EventScheduleForm(forms.ModelForm):
    event_category = ModelChoiceField(
        label="Category", queryset=EventCategory.objects.all()
    )
    event_start = forms.DateField(
        required=True, label="From", widget=DateInput(attrs={"type": "date"})
    )
    event_end = forms.DateField(
        required=True, label="End Date", widget=DateInput(attrs={"type": "date"})
    )

    class Meta:
        model = Event
        fields = (
            "event_category",
            "event_name",
            "event_venue",
            "event_start",
            "event_end",
            "event_logo",
        )

    def __str__(self):
        return self.event_name

    def clean(self):
        try:
            Event.objects.get(event_name=self.cleaned_data["event_name"])
            raise forms.ValidationError(
                "The Event Name already exist. Please try another one!"
            )
        except Event.DoesNotExist:
            pass
        return self.cleaned_data

    def clean_event_name(self):
        return self.cleaned_data["event_name"].capitalize()

    def __init__(self, *args, **kwargs):
        super(EventScheduleForm, self).__init__(*args, **kwargs)

        self.fields["event_category"].widget.attrs.update({"class": "choice-field"})
        self.fields["event_name"].widget.attrs.update({"class": "input-field"})
        self.fields["event_venue"].widget.attrs.update({"class": "input-field"})
        self.fields["event_start"].widget.attrs.update({"class": "start-field"})
        self.fields["event_end"].widget.attrs.update({"class": "end-field"})


class EventDailyActivity(forms.ModelForm):
    event_name = ModelChoiceField(label="Event Name", queryset=Event.objects.all())
    event_day = forms.DateField(
        required=True, label="Event Day", widget=DateInput(attrs={"type": "date"})
    )
    daily_login_time = forms.TimeField(
        required=True,
        label="Login Time",
        widget=forms.TimeInput(attrs={"placeholder": "00:00 am/pm"}, format="%I:%M %p"),
    )
    daily_logout_time = forms.TimeField(
        required=True,
        label="Logout Time",
        widget=forms.TimeInput(attrs={"placeholder": "00:00 am/pm"}, format="%I:%M %p"),
    )

    class Meta:
        model = EventDay
        fields = (
            "event_name",
            "event_day",
            "daily_login_time",
            "daily_logout_time",
        )

    def __init__(self, *args, **kwargs):
        super(EventDailyActivity, self).__init__(*args, **kwargs)

        self.fields["event_name"].widget.attrs.update({"class": "activity-name-field"})
        self.fields["event_day"].widget.attrs.update({"class": "activity-day-field"})
        self.fields["daily_login_time"].widget.attrs.update(
            {"class": "activity-login-field"}
        )
        self.fields["daily_logout_time"].widget.attrs.update(
            {"class": "activity-logout-field"}
        )


class EventTimeTableForm(forms.ModelForm):
    event_start_time = forms.TimeField(
        required=True,
        label="From time",
        widget=forms.TimeInput(attrs={"placeholder": "00:00 am/pm"}, format="%I:%M %p"),
    )
    event_end_time = forms.TimeField(
        required=True,
        label="End time",
        widget=forms.TimeInput(attrs={"placeholder": "00:00 am/pm"}, format="%I:%M %p"),
    )
    event_activity = forms.CharField(max_length=24, required=True, label="Activity")

    class Meta:
        model = EventActivity
        fields = ("event_start_time", "event_end_time", "event_activity")

    def __init__(self, *args, **kwargs):
        super(EventTimeTableForm, self).__init__(*args, **kwargs)

        self.fields["event_start_time"].widget.attrs.update(
            {"class": "from-time-field"}
        )
        self.fields["event_end_time"].widget.attrs.update({"class": "to-time-field"})
        self.fields["event_activity"].widget.attrs.update({"class": "activity-field"})


TimetableFormSet = inlineformset_factory(
    EventDay,
    EventActivity,
    EventTimeTableForm,
    can_delete=True,
    min_num=2,
    extra=0,
    max_num=15,
)


class AdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "user_idnumber",
            "email",
            "user_fname",
            "user_lname",
            "user_gender",
            "staff",
            "admin",
        )

    def __str__(self):
        return self.email

    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)
        self.fields["user_idnumber"].widget.attrs.update({"class": "input-field"})
        self.fields["email"].widget.attrs.update({"class": "input-field"})
        self.fields["user_fname"].widget.attrs.update({"class": "input-field"})
        self.fields["user_lname"].widget.attrs.update({"class": "input-field"})
        self.fields["user_gender"].widget.attrs.update({"class": "input-field"})

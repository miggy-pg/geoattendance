from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple    


from .forms import (
    UserAdminCreationForm, 
    UserAdminChangeForm,
)


User = get_user_model()

class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = []

    # Add the users field.
    users = forms.ModelMultipleChoiceField(
         queryset=User.objects.all(), 
         required=False,
         # Use the pretty 'filter_horizontal widget'.
         widget=FilteredSelectMultiple('users', False)
    )

    def __init__(self, *args, **kwargs):
        # Do the normal form initialisation.
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        # If it is an existing group (saved objects have a pk).
        if self.instance.pk:
            # Populate the users field with the current Group users.
            self.fields['users'].initial = self.instance.user_set.all()

    def save_m2m(self):
        # Add the users to the Group.
        self.instance.user_set.set(self.cleaned_data['users'])

    def save(self, *args, **kwargs):
        # Default save
        instance = super(GroupAdminForm, self).save()
        # Save many-to-many data
        self.save_m2m()
        return instance


# Unregister the original Group admin.
admin.site.unregister(Group)

# Create a new Group admin.
class GroupAdmin(admin.ModelAdmin):
    # Use our custom form.
    form = GroupAdminForm
    # Filter permissions horizontal as well.
    filter_horizontal = ['permissions']


class UserAdmin(BaseUserAdmin):

    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = [
        'ip',
        'user_idnumber',
        'email', 
        'user_lname', 
        'user_fname',
        'admin', 
        'staff', 
        'active',
        'timein',
        'timein_status',
        'timeout',
        'timeout_status',
        'prev_timeout',
        'status'
        ]
    list_filter = [
        'admin', 
        'active', 
        'staff'
        ]
    fieldsets = (
        (None, {'fields': ('user_idnumber','email','password','college', 'user_gender','yearlevel')}),
        ('Permissions', {'fields': ('active','admin', 'staff')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_idnumber', 'password', 'password_confirm', 'email', 'user_lname', 'user_fname', 'user_gender', 'admin', 'staff')}
        ),
    )

    search_fields = [
        'email', 
        'user_fname'
        ]
    ordering = ['email']
    filter_horizontal = (
        'user_permissions', 
        'groups'
        )

admin.site.register(Group, GroupAdmin)
admin.site.register(User, UserAdmin)
admin.site.site_header = "GeoAttendance Admin"

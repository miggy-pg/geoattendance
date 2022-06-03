from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib import messages
from django.db.models import fields
from django.http import (
    HttpResponse, 
    HttpResponseRedirect,
    JsonResponse
)
from django.shortcuts import render,redirect
from django.urls import reverse

from user.validators import validate_domainonly_email


User = get_user_model()

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'input'}))
    password_confirm = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class':'input'}))

    class Meta:
        model = User
        fields = ['user_idnumber',
        'user_fname',
        'user_lname',
        'user_gender',
        'email',
        'password',
        'password_confirm',
        'school',
        'yearlevel',    
        ]

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        
        self.fields['user_idnumber'].widget.attrs.update({'class':'input-field'})
        self.fields['email'].widget.attrs.update({'class':'input-field'})
        self.fields['password'].widget.attrs.update({'class':'input-field'})
        self.fields['password_confirm'].widget.attrs.update({'class':'input-field'})
        self.fields['user_fname'].widget.attrs.update({'class':'info-field'})
        self.fields['user_lname'].widget.attrs.update({'class':'info-field'})
        self.fields['user_gender'].widget.attrs.update({'class':'input-field'})
        self.fields['school'].widget.attrs.update({'class':'select-field'})
        self.fields['yearlevel'].widget.attrs.update({'class':'yearlevel-field'})
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password is not None and password != password_confirm:
            self.add_error("password_confirm", "Your passwords must match")
        return cleaned_data

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.user_idnumber = self.cleaned_data['user_idnumber']
        user.email = self.cleaned_data['email']
        user.user_fname = self.cleaned_data['user_fname']
        user.user_lname = self.cleaned_data['user_lname']
        user.school = self.cleaned_data['school']
        user.yearlevel = self.cleaned_data['yearlevel']
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
        return user


class UserAdminCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['user_idnumber']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password is not None and password != password_confirm:
            self.add_error("password_confirm", "Your passwords must match.")
        return cleaned_data

    def save(self, commit=True):
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['user_idnumber', 'password', 'active', 'admin',]

    def clean_password(self):
        return self.initial["password"]


class LoginForm(forms.Form):
    user_idnumber = forms.CharField(label="ID Number")
    password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        user_idnumber = self.cleaned_data.get('user_idnumber')
        password = self.cleaned_data.get('password')
        user = authenticate(user_idnumber=user_idnumber, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("Your Email and Password didn't match. Please try again.")
        return self.cleaned_data
        

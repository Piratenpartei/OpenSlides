#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    openslides.participant.forms
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Forms for the participant app.

    :copyright: 2011, 2012 by OpenSlides team, see AUTHORS.
    :license: GNU GPL, see LICENSE for more details.
"""

from django import forms
from django.contrib.auth.models import Permission
from django.utils.translation import ugettext_lazy as _

from openslides.utils.forms import (
    CssClassMixin, LocalizedModelMultipleChoiceField)

from openslides.participant.models import OpenSlidesUser, OpenSlidesGroup


class UserCreateForm(forms.ModelForm, CssClassMixin):
    first_name = forms.CharField(label=_("First name"))
    last_name = forms.CharField(label=_("Last name"))
    groups = forms.ModelMultipleChoiceField(
        queryset=OpenSlidesGroup.objects.exclude(name__iexact='anonymous'),
        label=_("User groups"), required=False)
    is_active = forms.BooleanField(
        label=_("Active"), required=False, initial=True)

    class Meta:
        model = OpenSlidesUser
        fields = ('first_name', 'last_name', 'is_active', 'groups', 'category',
                  'gender', 'type', 'committee', 'comment', 'firstpassword')


class UserUpdateForm(UserCreateForm):
    class Meta:
        model = OpenSlidesUser
        fields = ('username', 'first_name', 'last_name', 'is_active', 'groups',
                  'category', 'gender', 'type', 'committee', 'comment',
                  'firstpassword')


class GroupForm(forms.ModelForm, CssClassMixin):
    permissions = LocalizedModelMultipleChoiceField(
        queryset=Permission.objects.all(), label=_("Persmissions"),
        required=False)
    users = forms.ModelMultipleChoiceField(
        queryset=OpenSlidesUser.objects.all(),
        label=_("Users"), required=False)

    def __init__(self, *args, **kwargs):
        # Initial users
        if kwargs.get('instance', None) is not None:
            initial = kwargs.setdefault('initial', {})
            initial['users'] = [user.pk for user in kwargs['instance'].user_set.all()]

        super(GroupForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, False)

        old_save_m2m = self.save_m2m
        def save_m2m():
           old_save_m2m()

           instance.user_set.clear()
           for user in self.cleaned_data['users']:
               instance.user_set.add(user)
        self.save_m2m = save_m2m

        if commit:
            instance.save()
            self.save_m2m()

        return instance

    def clean_name(self):
        # Do not allow to change the name "anonymous" or give another group
        # this name
        data = self.cleaned_data['name']
        if self.instance.name.lower() == 'anonymous':
            # Editing the anonymous-user
            if self.instance.name.lower() != data.lower():
                raise forms.ValidationError(
                    _('You can not edit the name for the anonymous user'))
        else:
            if data.lower() == 'anonymous':
                raise forms.ValidationError(
                    _('Group name "%s" is reserved for internal use.') % data)
        return data

    class Meta:
        model = OpenSlidesGroup


class UsersettingsForm(forms.ModelForm, CssClassMixin):
    class Meta:
        model = OpenSlidesUser
        fields = ('username', 'first_name', 'last_name', 'email')


class UserImportForm(forms.Form, CssClassMixin):
    csvfile = forms.FileField(widget=forms.FileInput(attrs={'size': '50'}),
                              label=_("CSV File"))


class ConfigForm(forms.Form, CssClassMixin):
    participant_pdf_system_url = forms.CharField(
        widget=forms.TextInput(),
        required=False,
        label=_("System URL"),
        help_text=_("Printed in PDF of first time passwords only."))
    participant_pdf_welcometext = forms.CharField(
        widget=forms.Textarea(),
        required=False,
        label=_("Welcome text"),
        help_text=_("Printed in PDF of first time passwords only."))

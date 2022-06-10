#!/usr/bin/env python3
# coding: utf-8
from django import forms
from django.forms import BaseFormSet
from django.core.exceptions import ValidationError


class BaseCalendarFormSet(BaseFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['index'] = index
        return kwargs


class CalendarForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # initialize the form before creating fields
        super(CalendarForm, self).__init__(*args, **kwargs)
        print(kwargs)
        # index = kwargs.pop('index')
        if 'groups' in kwargs.keys():
            groups = kwargs.pop('groups')
            # create the dynamic fields
            group = groups[index]
            self.title = group["title"]
            self.id = group["id"]
            for module in group["modules"]:
                self.fields["module_aliases[" + str(module.id) + "]"] = forms.CharField(
                    label="", widget=forms.TextInput(
                        attrs={
                            "class": "form-control",
                            "data-form-type": "other",
                            "value": module.name,
                            "data-group": group["id"]
                        }
                    ))
            self.fields["group_id"] = forms.CharField(
                label="", widget=forms.HiddenInput(
                    attrs={"value": group["id"]}
                ))
        else:
            # create the dynamic fields
            group = {key.removeprefix(kwargs['prefix'] + "-"): kwargs['data'][key]
                     for key in kwargs['data'].keys() if key.startswith(kwargs['prefix'] + "-")}
            self.id = group.pop("group_id")
            for module in group:
                self.fields[module] = forms.CharField(
                    label="", widget=forms.TextInput(
                        attrs={
                            "class":          "form-control",
                            "data-form-type": "other",
                            "value":          group[module]
                        }
                    ))

    """def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        titles = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            title = form.cleaned_data.get('title')
            if title in titles:
                raise ValidationError("Articles in a set must have distinct titles.")
            titles.append(title)
    """
    # {{ form.field.as_hidden }}
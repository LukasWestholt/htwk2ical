#!/usr/bin/env python3
# coding: utf-8
from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, formset_factory, BaseFormSet


"""class MultiEmailField(forms.Field):
    def to_python(self, value):
        Normalize data to a list of strings.
        # Return an empty list if no input was given.
        if not value:
            return []
        return value.split(',')

    def validate(self, value):
        Check if value consists only of valid emails.
        # Use the parent's handling of required fields, etc.
        super().validate(value)
        for email in value:
            pass
"""

class CalendarItemForm(forms.Form):
    module_aliases = forms.CharField(
        label="", widget=forms.TextInput(
            attrs={
                "class":          "form-control",
                "data-form-type": "other"
            }
        ))


CalendarItemFormset = formset_factory(CalendarItemForm, extra=0)


class CalendarFormset(BaseFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        # save the formset in the 'nested' property
        form.nested = CalendarItemFormset(
            initial=[{'module_aliases': module.name} for module in form.modules])
            # initial=form.initial if form.is_bound else None)
            # prefix='address-%s-%s' % (
            # form.prefix,
            # CalendarFormset.get_default_prefix()))
        # print(form.nested)

class CalendarForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # initialize the form before creating fields
        super(CalendarForm, self).__init__(*args, **kwargs)
        # create the dynamic fields
        if 'initial' in kwargs:
            group = kwargs['initial']
            self.title = group["title"]
            self.id = group["group_id"]
            self.modules = group["modules"]
            """for module in group["modules"]:
                self.fields["module_aliases[" + str(module.id) + "]"] = forms.CharField(
                    label="", initial=module.name, widget=forms.TextInput(
                        attrs={
                            "class": "form-control",
                            "data-form-type": "other"
                        }
                    ))
            """
        else:
            """group = {key.removeprefix(kwargs['prefix'] + "-"): kwargs['data'][key]
                     for key in kwargs['data'] if key.startswith(kwargs['prefix'] + "-") and key != kwargs['prefix'] + "-group_id"}
            for module in group:
                self.fields[module] = forms.CharField(
                    label="", initial=group[module], widget=forms.TextInput(
                        attrs={
                            "class":          "form-control",
                            "data-form-type": "other"
                        }
                    ))"""
            pass
    group_id = forms.CharField(label="", widget=forms.HiddenInput())

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
            titles.append(title)"""

    # {{ form.field.as_hidden }}
#!/usr/bin/env python3
# coding: utf-8
from django import forms
from django.forms import formset_factory, BaseFormSet
from django.core.exceptions import ValidationError

from config import no_workgroup_str, all_workgroup_str
from myapp1.models import Module


class ModuleForm(forms.Form):
    module_aliases = forms.CharField(
        label="", required=False, widget=forms.TextInput(
            attrs={
                "class":          "form-control",
                "data-form-type": "other"
            }
        )
    )
    module_id = forms.IntegerField(label="", required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ModuleForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            module = kwargs['initial']
            if module['module_workgroups']:
                choices = [all_workgroup_str] + [
                    (workgroup, 'Gr. ' + workgroup) if workgroup != no_workgroup_str[0] else no_workgroup_str
                    for workgroup in sorted(module['module_workgroups'])
                ]
                self.fields['module_workgroups'] = forms.ChoiceField(
                    widget=forms.RadioSelect,
                    choices=choices
                )
                self.initial['module_workgroups'] = all_workgroup_str[0]
        elif 'data' in kwargs and 'prefix' in kwargs:
            data = kwargs['data']
            module = Module.objects.get(id=data[kwargs['prefix'] + "-module_id"])
            print(sorted(module.workgroups))
            choices = [all_workgroup_str] + [
                (workgroup, 'Gr. ' + workgroup) if workgroup != no_workgroup_str[0] else no_workgroup_str
                for workgroup in sorted(module.workgroups)
            ]
            self.fields['module_workgroups'] = forms.ChoiceField(
                widget=forms.RadioSelect,
                choices=choices,
                required=False
            )
        else:
            raise NotImplementedError

    def clean_module_id(self):
        data = self.cleaned_data['module_id']
        if not data:
            return data
        try:
            Module.objects.get(id=data)
        except Module.DoesNotExist:
            raise ValidationError("Module ID does not exist.")
        return data


class CalendarFormset(BaseFormSet):
    def add_fields(self, form, index):
        """
        nested: https://micropyramid.com/blog/how-to-use-nested-formsets-in-django/
        """
        super().add_fields(form, index)
        form.modules = ModuleFormset(
            data=form.data if form.is_bound else None,
            initial=[{
                'module_aliases': module.name,
                'module_id': module.id,
                'module_workgroups': module.workgroups
            } for module in form.group_modules]
            if not form.is_bound else None,
            prefix='module-%s-%s' % (
                form.prefix,
                CalendarFormset.get_default_prefix()
            )
        )

    def is_valid(self):
        if not super().is_valid():
            return False
        return all(
            [
                form.modules.is_valid()
                for form in self.forms
                if hasattr(form, 'modules')
            ]
        )

    def full_clean(self):
        if not self.is_bound:
            return
        for form in self.forms:
            if hasattr(form, 'modules'):
                for error in form.modules.errors:
                    if not error:
                        continue
                    form.add_error(None, str(error.as_data()))
                for error in form.modules.non_form_errors():
                    if not error:
                        continue
                    form.add_error(None, str(error))
        super().full_clean()

    def check_for_empty(self):
        for form in self.forms:
            modules = form.cleaned_data['modules']
            for module in modules:
                if module['module_aliases']:
                    return
        raise ValidationError("Empty Form")

    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        for form in self.forms:
            if hasattr(form, 'modules') and form.modules.is_valid():
                form.cleaned_data['modules'] = form.modules.cleaned_data

        # self.check_for_empty()


class CalendarForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs:
            group = kwargs['initial']
            self.group_title = group["title"]
            self.group_modules = group["modules"]
    group_id = forms.IntegerField(label="", widget=forms.HiddenInput())


# min_num=1 is required here, so there is an empty template module form if the group is empty
ModuleFormset = formset_factory(ModuleForm, extra=0, min_num=1, validate_min=True)
# min_num=1 is not really necessary here I think
CalendarFormset = formset_factory(CalendarForm, formset=CalendarFormset, extra=0, min_num=1, validate_min=True)

# TODO https://docs.djangoproject.com/en/4.0/topics/forms/formsets/#understanding-the-managementform-1
# form-#-DELETE

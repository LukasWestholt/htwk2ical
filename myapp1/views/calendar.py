#!/usr/bin/env python3
# coding: utf-8
import zoneinfo
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from myapp1.models import GroupCache, Group, Module, Calendar, ModuleAlias, ModuleWorkgroup
from config import group_id_divider, all_workgroup_str
from myapp1.forms import CalendarFormset
from myapp1 import iCalCreator


def choose_groups(request, group_ids):
    context = {
        "add_calendar_page": True,
        "divider":           group_id_divider
    }
    if group_ids:
        context["groups"] = Group.objects.filter(id__in=group_ids)
    return render(request, 'calendar/choose_groups.html', context=context)


def choose_modules(request, group_ids):
    groups = []
    for group_id in group_ids:
        try:
            group = Group.objects.filter(id=group_id).get()
        except Group.DoesNotExist:
            continue

        modules = list(group.module_set.all())
        for module in modules:
            module.default_workgroup = all_workgroup_str[0]
        groups.append({"group_id": group.id, "title": group.title, "modules": modules})

    if not groups:
        return send_to_groups_page(request)

    choose_groups_link = reverse('calendar', kwargs={'group_ids': group_id_divider.join(
        [str(group["group_id"]) for group in groups]
    )})
    formset = CalendarFormset(initial=groups)
    return render(request, 'calendar/choose_modules.html',
                  context={
                      "add_calendar_page": True,
                      "choose_groups_link": choose_groups_link,
                      "all_workgroup_str": all_workgroup_str,
                      "formset": formset
                  })


def calendar_edit(request, calendar_secret):
    try:
        calendar = Calendar.objects.filter(secret=calendar_secret).get()
    except Calendar.DoesNotExist:
        return send_to_groups_page(request)

    modules = list(calendar.modules.all())
    for module in modules:
        module.default_workgroup = all_workgroup_str[0]
        for module_workgroup in calendar.workgroups.all():
            if module_workgroup.module_id == module.id:
                module.default_workgroup = module_workgroup.workgroup
        for module_alias in calendar.aliases.all():
            if module_alias.module_id == module.id:
                module.name = module_alias.custom_name
    groups = []
    for group in calendar.groups.all():
        groups.append({"calendar_id": calendar.id, "group_id": group.id, "title": group.title, "modules": modules})

    choose_groups_link = reverse('calendar', kwargs={'group_ids': group_id_divider.join(
        [str(group["group_id"]) for group in groups]
    )})
    formset = CalendarFormset(initial=groups)
    return render(request, 'calendar/choose_modules.html',
                  context={
                      "add_calendar_page": True,
                      "choose_groups_link": choose_groups_link,
                      "all_workgroup_str": all_workgroup_str,
                      "formset": formset
                  })


def get_link(request):
    if request.method != 'POST':
        return send_to_groups_page(request)

    formset = CalendarFormset(request.POST)
    if not formset.is_valid():
        print(formset.errors)
        print(formset.non_form_errors().get_json_data())
        # TODO unterscheiden zwischen groups richtig -> modules pages und dem hier:
        return send_to_groups_page(request)
    else:
        print("Got cleaned data: " + str(formset.cleaned_data))

    cleaned_groups = [form['group_id'] for form in formset.cleaned_data]
    cleaned_modules = [module for form in formset.cleaned_data for module in form['modules'] if module['module_aliases']]
    cal = Calendar.objects.create()
    cal.groups.set(cleaned_groups)
    cal.modules.set([module['module_id'] for module in cleaned_modules])
    for cleaned_module in cleaned_modules:
        module = Module.objects.get(id=cleaned_module['module_id'])
        if module.name != cleaned_module['module_aliases']:
            print("Add alias: " + cleaned_module['module_aliases'] + " " + str(cleaned_module['module_id']))
            alias, _ = ModuleAlias.objects.get_or_create(custom_name=cleaned_module['module_aliases'],
                                                         module_id=cleaned_module['module_id'])
            cal.aliases.add(alias)
        if cleaned_module['module_workgroups'] and cleaned_module['module_workgroups'] != all_workgroup_str[0]:
            print("Add workgroup: " + cleaned_module['module_workgroups'] + " " + str(cleaned_module['module_id']))
            workgroup, _ = ModuleWorkgroup.objects.get_or_create(workgroup=cleaned_module['module_workgroups'],
                                                                 module_id=cleaned_module['module_id'])
            cal.workgroups.add(workgroup)

    return render(request, 'calendar/get_link.html',
                  context={
                      "add_calendar_page": True,
                      "secret": cal.secret
                  })


def get_groups(_):
    return JsonResponse({"groups": GroupCache.objects.get(key="groups").value})


def get_studium_generale(_):
    return JsonResponse({"studium_generale": GroupCache.objects.get(key="studium_generale").value})


def get(_, calendar_secret):
    try:
        cal = Calendar.objects.get(secret=calendar_secret)
    except Calendar.DoesNotExist:
        raise Http404("Calendar does not exist")

    cal.fetched_at = timezone.now()
    cal.save()
    current_tz = zoneinfo.ZoneInfo('Europe/Berlin')
    timezone.activate(current_tz)
    file_content = iCalCreator.create(cal.events(), cal.fetched_at, calendar_secret)
    response = HttpResponse(file_content, content_type='text/calendar')
    response['Content-Disposition'] = 'attachment; filename="HTWK2iCal.ics"'
    return response


def send_to_groups_page(request):
    return render(request, 'calendar/choose_groups.html',
                  context={
                      "add_calendar_page": True,
                      "notice":            'Bitte wähle einen gültigen Studiengang!'
                  }
                  )


def send_to_modules_page(request):
    return render(request, 'calendar/choose_modules.html',
                  context={
                      "add_calendar_page": True,
                      "notice":            'Bitte wähle Module, die dein Kalender beinhalten soll!'
                  }
                  )

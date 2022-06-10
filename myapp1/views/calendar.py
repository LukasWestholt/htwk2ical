#!/usr/bin/env python3
# coding: utf-8
import zoneinfo
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from myapp1.models import GroupCache, Group, Module, Calendar, ModuleAlias
from config import group_id_divider
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

    groups = [form['group_id'] for form in formset.cleaned_data]
    modules = [module for form in formset.cleaned_data for module in form['modules'] if module['module_aliases']]
    cal = Calendar.objects.create()
    cal.groups.set(groups)
    cal.modules.set([module['module_id'] for module in modules])
    for alias_set in modules:
        module = Module.objects.get(id=alias_set['module_id'])
        if module.name != alias_set['module_aliases']:
            print("Add alias: " + alias_set['module_aliases'] + " " + str(alias_set['module_id']))
            alias, _ = ModuleAlias.objects.get_or_create(custom_name=alias_set['module_aliases'],
                                                         module_id=alias_set['module_id'])
            cal.aliases.add(alias)

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

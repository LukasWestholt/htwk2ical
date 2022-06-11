#!/usr/bin/env python3
# coding: utf-8

import xml.etree.ElementTree as ElementTree
import re
from datetime import timedelta
import urllib.parse

from django.utils.html import strip_tags

from myapp1.models import Group, Module, GroupCache, Appointment
from config import all_groups_xml_url, all_modules_xml_url, studium_generale_fakultaet_id, \
    single_group_html_url, studium_generale_html_url, no_workgroup_str
from .fetch import fetch_contents_from_url


def rebuild_cache():
    sg_modules_dict = get_groups()
    get_cached_modules(sg_modules_dict)
    print("Done.")


def get_groups():
    sg_modules_dict = {}
    work_list = [
        {
            "is_sg_mode": False,
            "url": all_groups_xml_url,
            "xpath": "./fakultaet/studiengang"
        },
        {
            "is_sg_mode": True,
            "url": all_modules_xml_url,
            "xpath": "./fakultaet[@id=\"" + studium_generale_fakultaet_id + "\"]"
        }
    ]

    for work in work_list:
        groups_arr = []
        body = fetch_contents_from_url(*work["url"])

        for module in ElementTree.fromstring(body).findall(work["xpath"]):
            module_name = module.get("name")
            for group in module:
                group_name = group.get("name")
                if not work["is_sg_mode"] or group_name.startswith("Stud. gen."):
                    group_name = group_name.removeprefix("Stud. gen.").strip()
                    # print((module_name, group_name, group.get("id")))
                    group_object = log_write(Group.objects.get_or_create(
                        name=group_name
                    ))
                    if not work["is_sg_mode"] and group_object.title == "":
                        group_object.title = do_extended_title(group_name, module_name)
                        group_object.save()
                    elif work["is_sg_mode"] and group_object.sg_url == "":
                        group_object.sg_url = group.get("id").replace("%23", "#")
                        group_object.save()

                    groups_arr.append({"label": group_object.title, "id": group_object.id})
                    if work["is_sg_mode"]:
                        sg_modules_dict[group_object.id] = {}

                    print((module_name, group_name, group.get("id"), group_object.title, group_object.sg_url))
        # print(Group.objects.all())
        if not work["is_sg_mode"]:
            GroupCache.objects.get_or_create(key="groups", defaults={"value": groups_arr})

    return sg_modules_dict


# Replaces unnecessary information in title and category. Returns a hash
# formatted according to conventions of jQuery Autocomplete Plugin.
def do_extended_title(_group_name, _module_name):
    _faculty = re.sub(
        r"( \(.*\))* +\((Bachelor|Master|Diplom)?.*\)",
        r" (\2)",
        _module_name
    ).removesuffix("()").strip()  # https://regex101.com/r/2TSgP3/2
    return re.sub(r" *\((?!VZ|TZ).*\) *", '', _group_name) + (" – " + _faculty if _faculty != "" else "")


def get_cached_modules(sg_modules_dict):
    not_found = []
    for index, group_object in enumerate(Group.objects.all()):
        ordered_title = str(index+1) + " " + group_object.name
        url, default_encoding = \
            studium_generale_html_url if group_object.is_studium_generale() else single_group_html_url
        slug = group_object.sg_url or group_object.name
        url = url.replace("###SLUG###", urllib.parse.quote(slug.encode('utf8')))
        print(ordered_title + " url: " + url)
        try:
            body = fetch_contents_from_url(url, default_encoding, timeout=120)
        except FileNotFoundError:
            not_found.append(ordered_title + " (" + group_object.id + ")")
            continue
        extract_modules(body, group_object.id, sg_modules_dict)
        # schedule_arr = extract_modules(body, group_object.id, sg_modules_dict)  # TODO into groups?

        # cache extracted
        # Group.objects.get(group_object.id).update(cached_schedule=schedule_arr)

    # TODO DRY
    # TODO constantify
    GroupCache.objects.get_or_create(key="studium_generale", defaults={"value": sg_modules_dict})

    if len(not_found) > 0:
        print("groups not found:" + str(not_found))


def extract_modules(html, group_id, sg_modules_dict):
    """
    :type html: str
    :type group_id: int
    :type sg_modules_dict: dict
    """
    cmd_strip = "##STRIP-TAGS##"

    html_replacements = [
        (r"<!DOCTYPE.*<p><span class='labelone'>Mo", "<p><span class='labelone'>Mo", re.DOTALL),  # delete pre-table
        (r"\r\n<table class='footer-border-args.*html>", "", re.DOTALL),  # delete post-table
        (cmd_strip, "", 0),  # SPECIAL COMMAND strip tags
        (r"So$", "So\r\n\r\n\r\n\r\n", 0),  # handle "special" sundays
        (r"(Di|Mi|Do|Fr|Sa|So)(\r\n){4}", "###TRENN###", 0),  # mark day separations
        (r"(Mo)?(\r\n){4}", "", 0),  # delete 4x EOL
        (r"Planungswochen.+?am:", "", re.DOTALL),  # delete table head
    ]

    for old, new, flags in html_replacements:
        if old == cmd_strip:
            html = strip_tags(html).strip()
        else:
            html = re.sub(old, new, html, flags=flags)

    modules_split_by_days = html.split('###TRENN###')
    assert(len(modules_split_by_days) == 7)

    # converted_modules = []
    group = Group.objects.get(id=group_id)

    for weekday, modules_for_day in enumerate(modules_split_by_days):
        if re.match(r"^(\r\n)?$", modules_for_day):
            # converted_modules.append([])
            continue

        # day_modules_arr_with_hashes = []

        # fix breaking user input
        for phrase in [
        ]:
            modules_for_day = modules_for_day.replace(phrase + "\r\n\r\n\r\n", phrase + "\r\n")

        for module_str in modules_for_day.split("\r\n\r\n\r\n"):
            if module_str == "":
                continue

            # fix breaking user input
            for phrase in [
                "Informationsmanagement II: "
            ]:
                module_str = module_str.replace(phrase + "\r\n", phrase)

            module_arr = module_str.split("\r\n")
            assert(len(module_arr) == 9)

            module_title = module_arr[4]
            if module_title == "&nbsp;":
                module_title = "[Veranstaltung ohne Titel]"
            assert(module_title == module_title.strip())

            def check(text):
                return text if text != "&nbsp;" else None

            module, module_lecturer = get_module(group, module_title, sg_modules_dict)

            location = check(module_arr[3])
            appointment_type = check(module_arr[4 if group.is_studium_generale() else 5])
            lecturer = check(module_arr[5 if group.is_studium_generale() else 6] or module_lecturer)
            notes = check(module_arr[7])
            # https://regex101.com/r/dSS21T/1
            # https://regex101.com/r/IcZaPU/1
            regexes = [
                r'[Gg]r(?:uppe|\.)[\t ]+(\d+|[a-zA-Z])'
                r'(?:(?:\+|,[\t ]*)(\d+|[a-zA-Z]))?'
                r'(?:(?:\+|,[\t ]*)(\d+|[a-zA-Z]))?'
                r'(?:[\s,]|$)+',

                r'DWV[\t ]+(\d+|[a-zA-Z])(?:[\s,]|$)+'
            ]

            workgroups = []
            if notes:
                need_to_save = False
                regex_calc = [re.search(r, notes) for r in regexes]
                workgroups = [x for m in regex_calc if m for x in m.groups() if x]

                for workgroup in workgroups:
                    if workgroup not in module.workgroups:
                        module.add_workgroup(workgroup)
                        need_to_save = True
                if module.workgroups and all(x is None for x in regex_calc) and no_workgroup_str[0] not in module.workgroups:
                    module.add_workgroup(no_workgroup_str[0])
                    need_to_save = True
                if need_to_save:
                    log_write((module.save(), True))

            appointment_hash = {
                "weeks": string_to_week_array(module_arr[0]),
                "weekday": weekday,
                "start": timestring_to_seconds(module_arr[1]),
                "end": timestring_to_seconds(module_arr[2]),
                "location": location,
                "type": appointment_type,
                "lecturer": lecturer,
                "notes": notes,
                "workgroups": workgroups
            }
            appointment = log_write(Appointment.objects.get_or_create(**appointment_hash))
            appointment.modules.add(module)
            # day_modules_arr_with_hashes.append(appointment_hash)
        # converted_modules.append(day_modules_arr_with_hashes)
    # return converted_modules


def get_module(group, module_title, sg_modules_dict):
    lecturer = ""
    # TODO rückgängig (method) weil group sich beim aufruf nicht veröndert unnotig
    if group.is_studium_generale():
        # studium generale modules follow this pattern: name/lecturer[/lecturer] or name (lecturer[/lecturer])
        matches = re.match(r"^(.+?) *[/(] *(.+?) *\)?$", group.name)  # https://regex101.com/r/NRtzkU/2

        # ugly fix for '104  Was ist Recht?  RA Ralf Vogt & Prof. Bastian'
        if not matches:
            title = group.name
        else:
            title = matches[1]
            lecturer = matches[2]

        module = log_write(Module.objects.get_or_create(name=title, group_id=group.id))
        # group.modules << sg_module
        if sg_modules_dict.get(group.id) == {}:
            # TODO DRY (_make_autocomplete_hash)
            sg_modules_dict[group.id] = {
                "label":    title,
                "id":       module.id,
                "group_id": group.id
            }
    else:
        module = log_write(Module.objects.get_or_create(name=module_title, group_id=group.id))
    return module, lecturer


def timestring_to_seconds(time_str):
    """
    Convert a time string to duration in seconds.
    Example:
    timestring_to_seconds("8:30") -> 30600
    timestring_to_seconds("14:30") -> 52200
    :param time_str: string with time like '8:30'
    :type time_str: str
    :return: time in seconds
    :rtype: int
    """
    return int(timedelta(
        **{k: int(v) for k, v in re.match(r"(?P<hours>\d{1,2}):(?P<minutes>\d{2})", time_str)
            .groupdict().items()
           }).total_seconds())


def string_to_week_array(weeks_str):
    """
    Converts "12, 14, 17-20" into array of week integers
    """
    weeks_arr = []
    for week in weeks_str.split(","):
        match = re.match(r" *(\d{2})(-(\d{2}))?", week)
        weeks_arr.extend(range(int(match[1]), int(match[3]) if match[3] else int(match[1])+1))
    return weeks_arr


def log_write(data):
    # print if created
    if data[1]:
        print("Write: " + str(data[0]))
    return data[0]

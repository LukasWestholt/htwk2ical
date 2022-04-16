#!/usr/bin/env python3
# coding: utf-8

import urllib.request
import xml.etree.ElementTree as ElementTree
import re

from django.core.management import BaseCommand
from django.utils import timezone

from betterhtwk2ical.models import Group, Module, Appointment
from config import all_subjects_xml_url, all_courses_xml_url, studium_generale_fakultaet_id


class Command(BaseCommand):
    help = 'Rebuild cache'

    def handle(self, *args, **kwargs):

        # Replaces unnecessary information in title and category. Returns a hash
        # formatted according to conventions of jQuery Autocomplete Plugin.
        def _make_autocomplete_hash(_group_name, _course_name, _id):
            _category = re.sub(
                r"( \(.*\))* \((Bachelor|Master|Diplom)?.*\)",
                " (\2)",
                _course_name
            )
            label = re.sub(r"\((?!VZ|TZ).*\)", '', _group_name)
            label += " – #{category}" if _category != "" else ""

            return {"label": label, "id": _id}

        time = timezone.now().strftime('%X')
        self.stdout.write("It's now %s" % time)

        work_list = [
            {
                "is_sg_mode": False,
                "url": all_subjects_xml_url,
                "xpath": "./fakultaet/studiengang"
            },
            {
                "is_sg_mode": True,
                "url": all_courses_xml_url,
                "xpath": "./fakultaet[@id=\"" + studium_generale_fakultaet_id + "\"]"
            }
        ]

        for work in work_list:
            groups_arr = []
            with urllib.request.urlopen(work["url"]) as response:
                body = response.read().decode("utf8")

            for course in ElementTree.fromstring(body).findall(work["xpath"]):
                course_name = course.get("name")
                for group in course:
                    group_name = group.get("name")
                    if not work["is_sg_mode"] or group_name.startswith("Stud. gen. "):
                        group_name = group_name.removeprefix("Stud. gen.")
                        # print((course_name, group_name))
                        s, _ = Group.objects.get_or_create(
                            group_name=group_name
                        )
                        groups_arr.append(_make_autocomplete_hash(group_name, course_name, s.id))
        print(Group.objects.all())

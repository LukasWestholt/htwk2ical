#!/usr/bin/env python3
# coding: utf-8

from datetime import datetime
from django.utils import timezone
import zoneinfo
from dotenv import dotenv_values

SECRETS = dotenv_values(".env")

tz = zoneinfo.ZoneInfo('Europe/Berlin')

# maintenance mode
is_maintenance = False

# calendars created before this date will be told to update
latest_valid_date = timezone.make_aware(datetime(2022, 3, 31, 20), timezone=tz)

# date and week when semester started
start_date = timezone.make_aware(datetime(2022, 4, 4), timezone=tz)
start_week = 14

# path to XML files for groups and modules
all_groups_xml_url = ("https://stundenplan.htwk-leipzig.de/stundenplan/xml/public/semgrp_ss.xml", "utf-8")
all_modules_xml_url = ("https://stundenplan.htwk-leipzig.de/stundenplan/xml/public/modul_ss.xml", "utf-8")

# ID of XML node in 'all_modules_xml_url' that contains all studium generale
# modules
studium_generale_fakultaet_id = '%23SPLUS905495'

# base path for single schedule per group and studium generale
single_group_html_url = ("https://stundenplan.htwk-leipzig.de/ss/Berichte/Text-Listen;Studenten-Sets;name;"
                         "###SLUG###?template=UNEinzelGru&weeks=14-35", "ISO-8859-1")
studium_generale_html_url = ("https://stundenplan.htwk-leipzig.de/ss/Berichte/Text-Listen;Module;id;" 
                             "###SLUG###?template=UNEinzelLV&weeks=14-35", "ISO-8859-1")
group_id_divider = '-'
no_workgroup_str = ('NO', 'Keine Gruppe')
all_workgroup_str = ('ALL', 'alle')

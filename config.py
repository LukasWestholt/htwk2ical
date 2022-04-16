#!/usr/bin/env python3
# coding: utf-8

import datetime

from dotenv import dotenv_values

SECRETS = dotenv_values(".env")

# maintenance mode
is_maintenance = False

# calendars created before this date will be told to update
latest_valid_date = datetime.datetime(2022, 3, 31, 20)

# date and week when semester started
start_date = datetime.datetime(2022, 4, 4)
start_week = 14

# path to XML files for subjects and courses
all_subjects_xml_url = "https://stundenplan.htwk-leipzig.de/stundenplan/xml/public/semgrp_ss.xml"
all_courses_xml_url = "https://stundenplan.htwk-leipzig.de/stundenplan/xml/public/modul_ss.xml"

# ID of XML node in 'all_courses_xml_url' that contains all studium generale
# modules
studium_generale_fakultaet_id = '%23SPLUS905495'

# base path for single schedule per subject and studium generale
single_subjects_html_url = "https://stundenplan.htwk-leipzig.de/ss/Berichte/Text-Listen;Studenten-Sets;name;" \
                           "###SLUG###?template=UNEinzelGru&weeks=14-35"
studium_generales_html_url = "https://stundenplan.htwk-leipzig.de/ss/Berichte/Text-Listen;Module;id;" \
                             "###SLUG###?template=UNEinzelLV&weeks=14-35"

#!/usr/bin/env python3
# coding: utf-8

import icalendar
import datetime
import pytz


def create(events, now, secret):
    new_cal = icalendar.Calendar()
    for event in events:
        copied_event = icalendar.Event()
        copied_event.add("dtstamp", timezone_to_pytz(now))
        copied_event.add("dtstart", timezone_to_pytz(event["start"]))
        copied_event.add("dtend", timezone_to_pytz(event["end"]))
        copied_event.add("summary", event["summary"])
        if event["location"]:
            copied_event.add("location", event["location"])
        copied_event.add("sequence", 0)
        copied_event.add("description", event["description"])
        copied_event.add("uid", event["uid"])
        new_cal.add_component(copied_event)

    new_cal.add_component(icalendar_timezone())
    new_cal.add('X-WR-CALDESC', secret)
    new_cal.add('X-WR-CALNAME', secret)
    new_cal.add('X-WR-TIMEZONE', 'Europe/Berlin')
    new_cal.add('PRODID', '-//htwk-stundenplan.de//ENNOCAL 2.1//DE')
    new_cal.add('CALSCALE', 'GREGORIAN')
    new_cal.add('VERSION', '2.0')

    return new_cal.to_ical()


def icalendar_timezone():
    tzc = icalendar.Timezone()
    tzc.add('tzid', 'Europe/Berlin')
    tzc.add('x-lic-location', 'Europe/Berlin')
    tzs = icalendar.TimezoneStandard()
    tzs.add('tzname', 'CET')
    tzs.add('dtstart', datetime.datetime(1970, 10, 25, 3, 0, 0))
    tzs.add('rrule', {'freq': 'yearly', 'bymonth': 10, 'byday': '-1su'})
    tzs.add('TZOFFSETFROM', datetime.timedelta(hours=2))
    tzs.add('TZOFFSETTO', datetime.timedelta(hours=1))
    tzd = icalendar.TimezoneDaylight()
    tzd.add('tzname', 'CEST')
    tzd.add('dtstart', datetime.datetime(1970, 3, 29, 2, 0, 0))
    tzd.add('rrule', {'freq': 'yearly', 'bymonth': 3, 'byday': '-1su'})
    tzd.add('TZOFFSETFROM', datetime.timedelta(hours=1))
    tzd.add('TZOFFSETTO', datetime.timedelta(hours=2))

    tzc.add_component(tzs)
    tzc.add_component(tzd)
    return tzc


def timezone_to_pytz(dt):
    """
    Hotfix for https://github.com/collective/icalendar/issues/333
    :param dt: datetime with tzinfo
    :return: datetime with pytz tzinfo
    """
    assert(isinstance(dt, datetime.datetime))
    return dt.replace(tzinfo=pytz.timezone(str(dt.tzinfo)))

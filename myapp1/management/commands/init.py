#!/usr/bin/env python3
# coding: utf-8

import os
from django.core.management import BaseCommand, call_command
from htwk2ical.settings import STATIC_ROOT


class Command(BaseCommand):
    help = 'Init htwk2ical'

    def handle(self, *args, **kwargs):
        print("-- check for migrations --")
        call_command('migrate', interactive=False)
        if not os.path.isdir(STATIC_ROOT) or not os.listdir(STATIC_ROOT):
            print("-- first run detected, start initialization --")
            print("-- collect static files --")
            call_command('collectstatic', clear=True, interactive=False)
            print("-- set_donate_amount to zero --")
            call_command('set_donate_amount', '0.0')
            print("-- rebuild cache --")
            call_command('rebuild_cache')
        else:
            print("-- no initialization --")

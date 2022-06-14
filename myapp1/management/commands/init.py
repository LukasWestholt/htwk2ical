#!/usr/bin/env python3
# coding: utf-8

import os
from django.core.management import BaseCommand, call_command
from htwk2ical.settings import STATIC_ROOT


class Command(BaseCommand):
    help = 'Init htwk2ical'

    def handle(self, *args, **kwargs):
        if not os.path.isdir(STATIC_ROOT) or not os.listdir(STATIC_ROOT):
            call_command('collectstatic', clear=True, interactive=False)
            call_command('set_donate_amount', '0.0')
            call_command('rebuild_cache')

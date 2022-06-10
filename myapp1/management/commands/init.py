#!/usr/bin/env python3
# coding: utf-8

from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'Init htwk2ical'

    def handle(self, *args, **kwargs):
        call_command('set_donate_amount', '0.0')
        call_command('rebuild_cache')

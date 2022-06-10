#!/usr/bin/env python3
# coding: utf-8

from django.core.management import BaseCommand
from django.utils import timezone
from myapp1.helpers.rebuild_cache import rebuild_cache


class Command(BaseCommand):
    help = 'Rebuild cache'

    def handle(self, *args, **kwargs):
        time = timezone.now().strftime('%X')
        self.stdout.write("It's now %s" % time)
        rebuild_cache()

#!/usr/bin/env python3
# coding: utf-8

from django.core.management import BaseCommand
from myapp1.models import GroupCache


class Command(BaseCommand):
    help = 'Sets current donation amount'

    def add_arguments(self, parser):
        parser.add_argument('amount', type=float)

    def handle(self, *args, **kwargs):
        GroupCache.objects.update_or_create(key="donate_amount", defaults={"value": kwargs['amount']})
        print("donation amount updated to " + format(round(kwargs['amount'], 2), '.2f') + " €")

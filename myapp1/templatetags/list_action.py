#!/usr/bin/env python3
# coding: utf-8
from django import template

register = template.Library()


@register.simple_tag
def empty_list(i=None):
    return [0] * int(i)

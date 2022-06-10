#!/usr/bin/env python3
# coding: utf-8
from config import group_id_divider


class GroupIdsConverter:
    regex = '(?:' + group_id_divider + '?\d+)*'

    def to_python(self, value):
        if not value:
            return []
        return [int(group_id) for group_id in str(value).split(group_id_divider)]

    def to_url(self, value):
        if isinstance(value, list):
            value = group_id_divider.join([str(a) for a in value])
        # Muss django.utils.safestring.SafeString bleiben.
        return value

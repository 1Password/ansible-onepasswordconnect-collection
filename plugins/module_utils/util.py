from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import unicodedata
from ansible.module_utils.six import text_type


def utf8_normalize(raw):
    """Normalizes a utf-8 string for safe use in comparisons"""
    if not raw:
        return None

    unicode_normalized = unicodedata.normalize("NFKD", text_type(raw))
    return unicode_normalized.strip()

#!/usr/bin/env python3
# coding: utf-8

import urllib.request
from urllib.error import URLError
import socket


def fetch_contents_from_url(url, default_encoding, timeout=10, max_try=3, debug=False):
    """
    :param default_encoding:
    :type url: str
    :type timeout: int
    :type max_try: int
    :type debug: bool
    :rtype: str
    """
    if debug:
        print(str(max_try) + (" tries left" if max_try > 1 else " try left"))
    try:
        req = urllib.request.urlopen(url, timeout=timeout)
        encoding = req.headers.get_content_charset(failobj=default_encoding)
        return req.read().decode(encoding)
    except socket.timeout as e:
        print("Timeout: " + str(e))
        if max_try > 1:
            return fetch_contents_from_url(url, default_encoding, timeout=timeout, max_try=max_try-1, debug=True)
        raise
    except urllib.error.HTTPError as e:
        if e.code == 503:
            print("aborted because of 503 error")
            raise
        if e.code in (400, 404):
            print("not found")
            raise FileNotFoundError
        print(e)
        raise
    except ConnectionRefusedError as e:
        print("2")
        print(e)
        print(e.errno)
        print(e.args)
        raise
    except URLError as e:
        print("3")
        print(e)
        print(e.args)
        print(e.reason)
        raise

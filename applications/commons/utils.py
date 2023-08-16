import base64
import datetime
import time


def datetime2timestamp(d):
    return time.mktime(d.timetuple())


def timestamp2datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


def base64decode2binary(base64_str):
    return base64.b64decode(base64_str)

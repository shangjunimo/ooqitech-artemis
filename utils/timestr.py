# -*- coding: utf-8 -*-

import datetime
import os
import time


def get_time_now():
    return (datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S')


def format_time(timestring):
    if not isinstance(timestring, datetime.datetime):
        return None
    return (timestring).strftime('%Y-%m-%d %H:%M:%S')


def get_file_create_time(file_path):
    assert os.path.exists(file_path)
    file_time = time.localtime(os.stat(file_path).st_ctime)
    return time.strftime('%Y-%m-%d %H:%M:%S', file_time)


def get_file_modify_time(file_path):
    assert os.path.exists(file_path)
    file_time = time.localtime(os.stat(file_path).st_mtime)
    return time.strftime('%Y-%m-%d %H:%M:%S', file_time)


def json_datatime_converter(o):
    if isinstance(o, datetime.datetime):
        return o.strftime('%Y-%m-%d %H:%M:%S').__str__()


def format_str_to_datetime(timestr):
    return datetime.datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S')


def get_befor_year_month(day=2):
    return (datetime.datetime.now() - datetime.timedelta(days=day)).strftime('%Y-%m')


def get_befor_day(day=2):
    return (datetime.datetime.now() - datetime.timedelta(days=day)).strftime('%Y-%m-%d')


def get_tomorrow():
    return (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y%m%d')

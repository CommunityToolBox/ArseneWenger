#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime


def getTimestamp():
    """
    Utility function to get a nicely formatted timestamp
    :return: Returns date and time in the following format "DD/MM [HH:MM]"
    """
    dt = str(datetime.datetime.now().month) + '/' + str(datetime.datetime.now().day) + ' '
    hr = str(datetime.datetime.now().hour) if len(str(datetime.datetime.now().hour)) > 1 else '0' + str(datetime.datetime.now().hour)
    min = str(datetime.datetime.now().minute) if len(str(datetime.datetime.now().minute)) > 1 else '0' + str(datetime.datetime.now().minute)
    t = '[' + hr + ':' + min + '] '
    return dt + t


def clamp_int(value, minimum, maximum):
    """
    Clamp integer between 2 values
    :param value: Current value
    :param minimum: Minimum value
    :param maximum: Maximum value
    :return: Current value, clamped to between min and max
    """
    if value < minimum:
        value = minimum
    elif value > maximum:
        value = maximum
    return value

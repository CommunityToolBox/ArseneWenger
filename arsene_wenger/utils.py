#!/usr/bin/env python
import datetime


def get_timestamp():
    """
    Utility function to get a nicely formatted timestamp
    :return: Returns date and time in the following format "DD/MM [HH:MM]"
    """
    dt = str(datetime.datetime.now().month) + "/" + str(datetime.datetime.now().day) + " "
    hr = (
        str(datetime.datetime.now().hour)
        if len(str(datetime.datetime.now().hour)) > 1
        else "0" + str(datetime.datetime.now().hour)
    )
    min = (
        str(datetime.datetime.now().minute)
        if len(str(datetime.datetime.now().minute)) > 1
        else "0" + str(datetime.datetime.now().minute)
    )
    t = "[" + hr + ":" + min + "] "
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


def current_season() -> str:
    """
    Returns a season string i.e. 2022-2023, 2023-2024

    We check whether we are in a season typically between August and May
    """
    now = datetime.datetime.now()
    if now.month >= 8 or now.month <= 5:
        return f"{now.year}-{now.year + 1}"
    else:
        return f"{now.year - 1}-{now.year}"

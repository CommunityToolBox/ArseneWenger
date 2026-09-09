import datetime


def getTimestamp():
    """
    Utility function to get a nicely formatted timestamp
    :return: Returns date and time in the following format "DD/MM [HH:MM]"
    """
    now = datetime.datetime.now(tz=datetime.UTC)
    dt = str(now.month) + "/" + str(now.day) + " "
    hr = str(now.hour) if len(str(now.hour)) > 1 else "0" + str(now.hour)
    min = str(now.minute) if len(str(now.minute)) > 1 else "0" + str(now.minute)
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
    """
    now = datetime.datetime.now(tz=datetime.UTC)
    start = now.year if now.month >= 7 else now.year - 1
    return f"{start}-{start + 1}"


def make_discord_timestamp(value: datetime.datetime) -> str:
    """
    Build a Discord timestamp string from a datetime object
    This is a unix timestamp that displays a dattime to a Discord
    user in their localized timezone.
    """
    return f"<t:{int(value.timestamp())}:F>"  # F = Full Date Time

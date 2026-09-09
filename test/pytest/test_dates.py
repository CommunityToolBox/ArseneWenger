import datetime

from cogs.fixtures import clean_date_string, parse_date
from freezegun import freeze_time
from utils import current_season


class FakeDateTag:
    def __init__(self, text):
        self.text = text

    def find(self, *args, **kwargs):
        return self


def parse(date_text):
    return parse_date(FakeDateTag(date_text))


@freeze_time("2026-09-09")
def test_parse_date_autumn():
    assert parse("Sat Sept 12 - 19:00") == datetime.datetime(
        2026, 9, 12, 19, 0, tzinfo=datetime.UTC
    )
    assert parse("Wed Feb 3 - 20:00") == datetime.datetime(
        2027, 2, 3, 20, 0, tzinfo=datetime.UTC
    )


@freeze_time("2027-01-15")
def test_parse_date_after_new_year():
    assert parse("Sat Sept 12 - 19:00") == datetime.datetime(
        2026, 9, 12, 19, 0, tzinfo=datetime.UTC
    )
    assert parse("Wed Feb 3 - 20:00") == datetime.datetime(
        2027, 2, 3, 20, 0, tzinfo=datetime.UTC
    )


@freeze_time("2027-05-24")
def test_parse_date_end_of_season():
    assert parse("Sun May 24 - 15:00") == datetime.datetime(
        2027, 5, 24, 15, 0, tzinfo=datetime.UTC
    )


@freeze_time("2026-07-20")
def test_parse_date_preseason():
    assert parse("Sat Aug 1 - 18:00") == datetime.datetime(
        2026, 8, 1, 18, 0, tzinfo=datetime.UTC
    )


def test_clean_date_string_uk_abbreviations():
    assert clean_date_string("Wed Sept 9 - 19:00") == "Wed Sep 9 - 19:00"
    assert clean_date_string("Sat Aug 1 - 18:00") == "Sat Aug 1 - 18:00"


@freeze_time("2026-09-09")
def test_current_season_autumn():
    assert current_season() == "2026-2027"


@freeze_time("2027-01-15")
def test_current_season_after_new_year():
    assert current_season() == "2026-2027"


@freeze_time("2027-06-10")
def test_current_season_just_after_season_ends():
    assert current_season() == "2026-2027"

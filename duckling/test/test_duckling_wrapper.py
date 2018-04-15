import pytest
from datetime import time, date, timedelta, datetime
from dateutil import parser
from dateutil.tz import tzlocal
from duckling import DucklingWrapper, Dim


@pytest.fixture(scope='module')
def duckling_wrapper():
    return DucklingWrapper()


@pytest.fixture(scope='module')
def duckling_wrapper_with_datetime():
    return DucklingWrapper(parse_datetime=True)


@pytest.fixture
def today_evening():
    return datetime.today().replace(
        hour=18, minute=0, second=0, microsecond=0, tzinfo=tzlocal())


@pytest.fixture
def tomorrow():
    return datetime.today().replace(
        hour=0, minute=0, second=0, microsecond=0, tzinfo=tzlocal()) \
        + timedelta(days=1)


def test_parse_time(duckling_wrapper):
    result = duckling_wrapper.parse_time(
        u'Let\'s meet at 11:45am')
    assert len(result) == 1
    assert time(11, 45) == parser.parse(result[0][u'value'][u'value']).time()


def test_parse_time_with_datetime(duckling_wrapper_with_datetime):
    result = duckling_wrapper_with_datetime.parse_time(
        u'Let\'s meet at 11:45am')
    assert len(result) == 1
    assert time(11, 45) == result[0][u'value'][u'value'].time()


def test_parse_time_with_reference_time(duckling_wrapper):
    result = duckling_wrapper.parse_time(
        u'Let\'s meet tomorrow', reference_time=u'1990-12-30')
    assert len(result) == 1
    assert parser.parse(u'1990-12-30').date() + \
        timedelta(days=1) == parser.parse(result[0][u'value'][u'value']).date()


def test_parse_time_with_reference_time_and_datetime(duckling_wrapper_with_datetime):
    result = duckling_wrapper_with_datetime.parse_time(
        u'Let\'s meet tomorrow', reference_time=u'1990-12-30')
    assert len(result) == 1
    assert parser.parse(u'1990-12-30').date() + \
        timedelta(days=1) == result[0][u'value'][u'value'].date()


def test_parse_time_with_reference_time_and_weird_timezone(duckling_wrapper):
    result = duckling_wrapper.parse_time(
        u'Tomorrow at 5pm', reference_time='2017-04-11T08:26:07.470413-07:00')
    assert len(result) == 1
    assert parser.parse(u'2017-04-11').date() + \
        timedelta(days=1) == parser.parse(result[0][u'value'][u'value']).date()
    assert time(17, 00) == parser.parse(result[0][u'value'][u'value']).time()
    assert timedelta(hours=-7) == parser.parse(result[0][u'value'][u'value']).utcoffset()

def test_parse_time_with_reference_time_and_timezone(duckling_wrapper):
    result = duckling_wrapper.parse_time(
        u'Let\'s meet tomorrow at 12pm', reference_time=u'1990-12-30 15:30:00-8:00')
    assert len(result) == 1
    assert parser.parse(u'1990-12-30').date() + \
        timedelta(days=1) == parser.parse(result[0][u'value'][u'value']).date()
    assert time(12, 00) == parser.parse(result[0][u'value'][u'value']).time()
    assert timedelta(hours=-8) == parser.parse(result[0][u'value'][u'value']).utcoffset()


def test_parse_time_with_reference_time_and_datetime_and_negative_timezone(duckling_wrapper_with_datetime):
    result = duckling_wrapper_with_datetime.parse_time(
        u'Let\'s meet tomorrow at 12pm', reference_time=u'1990-12-30 15:30:00-8:00')
    assert len(result) == 1
    assert parser.parse(u'1990-12-30').date() + \
        timedelta(days=1) == result[0][u'value'][u'value'].date()
    assert time(12, 00) == result[0][u'value'][u'value'].time()
    assert timedelta(hours=-8) == result[0][u'value'][u'value'].utcoffset()

def test_parse_time_with_reference_time_and_datetime_and_positive_timezone(duckling_wrapper_with_datetime):
    result = duckling_wrapper_with_datetime.parse_time(
        u'Let\'s meet tomorrow at 12pm', reference_time=u'1990-12-30 15:30:00+8:00')
    assert len(result) == 1
    assert parser.parse(u'1990-12-30').date() + \
        timedelta(days=1) == result[0][u'value'][u'value'].date()
    assert time(12, 00) == result[0][u'value'][u'value'].time()
    assert timedelta(hours=8) == result[0][u'value'][u'value'].utcoffset()


def test_parse_times(duckling_wrapper):
    result = duckling_wrapper.parse_time(
        u'Let\'s meet at 11:45am or tomorrow')
    assert len(result) == 2
    assert date.today() + \
        timedelta(days=1) == parser.parse(result[0][u'value'][u'value']).date()
    assert time(11, 45) == parser.parse(result[1][u'value'][u'value']).time()


def test_parse_times_with_datetime(duckling_wrapper_with_datetime):
    result = duckling_wrapper_with_datetime.parse_time(
        u'Let\'s meet at 11:45am or tomorrow')
    assert len(result) == 2
    assert date.today() + \
        timedelta(days=1) == result[0][u'value'][u'value'].date()
    assert time(11, 45) == result[1][u'value'][u'value'].time()


def test_parse_timezone(duckling_wrapper):
    result = duckling_wrapper.parse_timezone(
        u'my timezone is pdt')
    assert len(result) == 1
    assert u'PDT' == result[0][u'value'][u'value']


def test_parse_timezones(duckling_wrapper):
    result = duckling_wrapper.parse_timezone(
        u'what timezone works for you? pdt or wit')
    assert len(result) == 2
    assert u'PDT' == result[0][u'value'][u'value']
    assert u'WIT' == result[1][u'value'][u'value']


def test_parse_temperature(duckling_wrapper):
    result = duckling_wrapper.parse_temperature(
        u'it\'s 65 degrees in here')
    assert len(result) == 1
    assert 65.0 == result[0][u'value'][u'value']
    assert isinstance(result[0][u'value'][u'value'], float)
    assert u'degree' == result[0][u'value'][u'unit']


def test_parse_temperatures(duckling_wrapper):
    result = duckling_wrapper.parse_temperature(
        u'let\'s change the temperatur from thirty two celsius to 65 degrees')
    assert len(result) == 2
    assert 65.0 == result[0][u'value'][u'value']
    assert isinstance(result[0][u'value'][u'value'], float)
    assert u'degree' == result[0][u'value'][u'unit']
    assert 32.0 == result[1][u'value'][u'value']
    assert isinstance(result[1][u'value'][u'value'], float)
    assert u'celsius' == result[1][u'value'][u'unit']


def test_parse_number(duckling_wrapper):
    result = duckling_wrapper.parse_number(
        u'I\'m 25 years old')
    assert len(result) == 1
    assert 25.0 == result[0][u'value'][u'value']
    assert isinstance(result[0][u'value'][u'value'], float)


def test_parse_numbers(duckling_wrapper):
    result = duckling_wrapper.parse_number(
        u'lucky number seven or 42 as answer for everything?')
    assert len(result) == 2
    assert 7.0 == result[0][u'value'][u'value']
    assert isinstance(result[0][u'value'][u'value'], float)
    assert 42.0 == result[1][u'value'][u'value']
    assert isinstance(result[1][u'value'][u'value'], float)


def test_parse_ordinal(duckling_wrapper):
    result = duckling_wrapper.parse_ordinal(
        u'I\'m first')
    assert len(result) == 1
    assert 1 == result[0][u'value'][u'value']
    assert isinstance(result[0][u'value'][u'value'], int)


def test_parse_ordinals(duckling_wrapper):
    result = duckling_wrapper.parse_ordinal(
        u'I\'m first, you\'re 2nd')
    assert len(result) == 2
    assert 1 == result[0][u'value'][u'value']
    assert isinstance(result[0][u'value'][u'value'], int)
    assert 2 == result[1][u'value'][u'value']
    assert isinstance(result[1][u'value'][u'value'], int)


def test_parse_distance(duckling_wrapper):
    result = duckling_wrapper.parse_distance(
        u'I commute 5 miles everyday')
    assert len(result) == 1
    assert 5.0 == result[0][u'value'][u'value']
    assert isinstance(result[0][u'value'][u'value'], float)
    assert u'mile' == result[0][u'value'][u'unit']


def test_parse_distances(duckling_wrapper):
    result = duckling_wrapper.parse_distance(
        u'4km are 2.5 miles')
    assert len(result) == 2
    assert 4.0 == result[0][u'value'][u'value']
    assert isinstance(result[0][u'value'][u'value'], float)
    assert u'kilometre' == result[0][u'value'][u'unit']
    assert 2.5 == result[1][u'value'][u'value']
    assert isinstance(result[1][u'value'][u'value'], float)
    assert u'mile' == result[1][u'value'][u'unit']


def test_parse_volume(duckling_wrapper):
    result = duckling_wrapper.parse_volume(
        u'You should drink 2 liters everyday')
    assert len(result) == 1
    assert 2.0 == result[0][u'value'][u'value']
    assert isinstance(result[0][u'value'][u'value'], float)
    assert u'litre' == result[0][u'value'][u'unit']
    assert result[0][u'value'][u'latent'] is False

    result2 = duckling_wrapper.parse_volume(
        u'You should drink 2 something everyday')
    assert result2[0][u'value'][u'latent'] is True


def test_parse_volumes(duckling_wrapper):
    result = duckling_wrapper.parse_volume(
        u'1 gallon is 3785ml')
    assert len(result) == 2
    assert 3785.0 == result[0][u'value'][u'value']
    assert isinstance(result[0][u'value'][u'value'], float)
    assert u'millilitre' == result[0][u'value'][u'unit']
    assert 1.0 == result[1][u'value'][u'value']
    assert isinstance(result[1][u'value'][u'value'], float)
    assert u'gallon' == result[1][u'value'][u'unit']


def test_parse_money(duckling_wrapper):
    result = duckling_wrapper.parse_money(
        u'you owe me 10 dollars')
    assert len(result) == 1
    assert 10.0 == result[0][u'value'][u'value']
    assert isinstance(result[0][u'value'][u'value'], float)
    assert u'$' == result[0][u'value'][u'unit']


def test_parse_moneys(duckling_wrapper):
    result = duckling_wrapper.parse_money(
        u'20 bucks are $20')
    assert len(result) == 2
    assert 20.0 == result[0][u'value'][u'value']
    assert isinstance(result[0][u'value'][u'value'], float)
    assert u'$' == result[0][u'value'][u'unit']
    assert 20.0 == result[1][u'value'][u'value']
    assert isinstance(result[1][u'value'][u'value'], float)
    assert result[1][u'value'][u'unit'] is None


def test_parse_duration(duckling_wrapper):
    result = duckling_wrapper.parse_duration(
        u'I ran for 2 hours today')
    assert len(result) == 1
    assert 2.0 == result[0][u'value'][u'value']
    assert isinstance(result[0][u'value'][u'value'], float)
    assert u'hour' == result[0][u'value'][u'unit']


def test_parse_durations(duckling_wrapper):
    result = duckling_wrapper.parse_duration(
        u'2 hours are 120 min')
    assert len(result) == 2
    assert 2.0 == result[0][u'value'][u'value']
    assert isinstance(result[0][u'value'][u'value'], float)
    assert u'hour' == result[0][u'value'][u'unit']
    assert 120.0 == result[1][u'value'][u'value']
    assert isinstance(result[0][u'value'][u'value'], float)
    assert u'minute' == result[1][u'value'][u'unit']


def test_parse_email(duckling_wrapper):
    result = duckling_wrapper.parse_email(
        u'shoot me an email at contact@frank-blechschmidt.com')
    assert len(result) == 1
    assert u'contact@frank-blechschmidt.com' == result[0][u'value'][u'value']


def test_parse_emails(duckling_wrapper):
    result = duckling_wrapper.parse_email(
        u'contact@frank-blechschmidt.com is my email, or use frank.blechschmidt@sap.com')
    assert len(result) == 2
    assert u'contact@frank-blechschmidt.com' == result[0][u'value'][u'value']
    assert u'frank.blechschmidt@sap.com' == result[1][u'value'][u'value']


def test_parse_url(duckling_wrapper):
    result = duckling_wrapper.parse_url(
        u'frank-blechschmidt.com is under construction')
    assert len(result) == 1
    assert u'frank-blechschmidt.com' == result[0][u'value'][u'value']


def test_parse_urls(duckling_wrapper):
    result = duckling_wrapper.parse_url(
        u'frank-blechschmidt.com is under construction, but you can check my github github.com/FraBle')
    assert len(result) == 2
    assert {u'frank-blechschmidt.com', u'github.com/FraBle'} == \
        {result[0][u'value'][u'value'], result[1][u'value'][u'value']}


def test_parse_phone_number(duckling_wrapper):
    result = duckling_wrapper.parse_phone_number(
        u'424-242-4242 is obviously a fake number')
    assert len(result) == 1
    assert u'424-242-4242 ' == result[0][u'value'][u'value']


def test_parse_phone_numbers(duckling_wrapper):
    result = duckling_wrapper.parse_phone_number(
        u'try 424-242-4242 or (650)-650-6500 ext 650')
    assert len(result) == 2
    assert u'424-242-4242 ' == result[0][u'value'][u'value']
    assert u'(650)-650-6500 ext 650' == result[1][u'value'][u'value']


def test_parse(duckling_wrapper):
    result = duckling_wrapper.parse(
        u'You owe me twenty bucks, please call me today')
    assert len(result) == 7
    for entry in result:
        if entry['dim'] in (
                Dim.NUMBER,
                Dim.AMOUNTOFMONEY,
                Dim.DISTANCE,
                Dim.VOLUME,
                Dim.TEMPERATURE):
            assert 20 == result[0][u'value'][u'value']
            assert result[0][u'value'].get(u'unit', None) is None
            assert result[0][u'value'].get(u'latent', True) is True
        if entry[u'dim'] == Dim.TIME and entry[u'text'] == u'today':
            assert date.today() == parser.parse(
                entry[u'value'][u'value']).date()


def test_parse_with_reference_time(duckling_wrapper):
    result = duckling_wrapper.parse(
        u'Let\'s meet tomorrow', reference_time=u'1990-12-30')
    assert len(result) == 1
    assert parser.parse(u'1990-12-30').date() + \
        timedelta(days=1) == parser.parse(result[0][u'value'][u'value']).date()


def test_parse_with_reference_time_and_datetime(duckling_wrapper_with_datetime):
    result = duckling_wrapper_with_datetime.parse(
        u'Let\'s meet tomorrow', reference_time=u'1990-12-30')
    assert len(result) == 1
    assert parser.parse(u'1990-12-30').date() + \
        timedelta(days=1) == result[0][u'value'][u'value'].date()


def test_parse_with_reference_time_and_timezone(duckling_wrapper):
    result = duckling_wrapper.parse(
        u'Let\'s meet tomorrow at 12pm', reference_time=u'1990-12-30 15:30:00-8:00')
    assert len(result) == 5
    assert parser.parse(u'1990-12-30').date() + \
        timedelta(days=1) == parser.parse(result[4][u'value'][u'value']).date()
    assert time(12, 00) == parser.parse(result[4][u'value'][u'value']).time()


def test_parse_with_reference_time_and_datetime_and_timezone(duckling_wrapper_with_datetime):
    result = duckling_wrapper_with_datetime.parse(
        u'Let\'s meet tomorrow at 12pm', reference_time=u'1990-12-30 15:30:00-8:00')
    assert len(result) == 5
    assert parser.parse(u'1990-12-30').date() + \
        timedelta(days=1) == result[4][u'value'][u'value'].date()
    assert time(12, 00) == result[4][u'value'][u'value'].time()


def test_interval(duckling_wrapper, today_evening, tomorrow):
    result = duckling_wrapper.parse_time(
        u'a night away')
    assert len(result) == 1
    assert tomorrow == parser.parse(result[0][u'value'][u'value'][u'to'])
    assert today_evening == parser.parse(
        result[0][u'value'][u'value'][u'from'])


def test_interval_with_datetime(duckling_wrapper_with_datetime, today_evening, tomorrow):
    result = duckling_wrapper_with_datetime.parse_time(
        u'a night away')
    assert len(result) == 1
    assert tomorrow == result[0][u'value'][u'value'][u'to']
    assert today_evening == result[0][u'value'][u'value'][u'from']


def test_interval_only_from(duckling_wrapper, today_evening):
    result = duckling_wrapper.parse_time(
        u'after tonight')
    assert len(result) == 1
    assert today_evening == parser.parse(
        result[0][u'value'][u'value'][u'from'])


def test_interval_only_from_with_datetime(duckling_wrapper_with_datetime, today_evening):
    result = duckling_wrapper_with_datetime.parse_time(
        u'after tonight')
    assert len(result) == 1
    assert today_evening == result[0][u'value'][u'value'][u'from']


def test_parse_product(duckling_wrapper):
    result = duckling_wrapper.parse(u'5 cups of sugar')
    assert len(result) == 8
    assert u'leven-unit' == result[0][u'dim']
    assert u'cup' == result[0][u'value'][u'value']
    assert u'leven-product' == result[1][u'dim']
    assert u'sugar' == result[1][u'value'][u'value']
    assert u'quantity' == result[7][u'dim']
    assert u'sugar' == result[7][u'value'][u'product']


def test_parse_leven_product(duckling_wrapper):
    result = duckling_wrapper.parse_leven_product(u'5 cups of sugar')
    assert len(result) == 1
    assert u'sugar' == result[0][u'value'][u'value']


def test_parse_leven_unit(duckling_wrapper):
    result = duckling_wrapper.parse_leven_unit(u'two pounds of meat')
    assert len(result) == 1
    assert u'pound' == result[0][u'value'][u'value']


def test_parse_quantity(duckling_wrapper):
    result = duckling_wrapper.parse_quantity(u'5 cups of sugar')
    assert len(result) == 1
    assert 5 == result[0][u'value'][u'value']
    assert u'cup' == result[0][u'value'][u'unit']
    assert u'sugar' == result[0][u'value'][u'product']


# TODO: Find good examples for parse_cycle(), parse_unit(),
#       and parse_unit_of_duration(). The utterances used below return no
#       results from Duckling itself.

# def test_parse_cycle(duckling_wrapper):
#     result = duckling_wrapper.parse_cycle(u'coming week')
#     assert len(result) == 1


# def test_parse_unit(duckling_wrapper):
#     result = duckling_wrapper.parse_unit(u'6 degrees outside')
#     assert len(result) == 1


# def test_parse_unit_of_duration(duckling_wrapper):
#     result = duckling_wrapper.parse_unit_of_duration(u'1 second')
#     assert len(result) == 1

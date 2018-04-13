import pytest
import jpype
from datetime import datetime, timedelta
from dateutil import parser
from dateutil.tz import tzlocal
from duckling import Duckling, Dim, Language


@pytest.fixture
def test_input():
    return '2pm'


@pytest.fixture
def test_time_input():
    return 'Let\'s meet tomorrow'


@pytest.fixture
def dec_30():
    return '1990-12-30'


@pytest.fixture
def answer_to_the_ultimate_question_of_life_the_universe_and_everything():
    return 42


@pytest.fixture
def two_pm():
    return datetime.now(tzlocal()).replace(
        hour=14, minute=0, second=0, microsecond=0)


@pytest.fixture
def two_pm_str(two_pm):
    return two_pm.strftime('%Y-%m-%dT%H:%M:%S%z')


@pytest.fixture(scope='module')
def clojure():
    return jpype.JClass('clojure.java.api.Clojure')


@pytest.fixture
def java_symbol():
    return jpype.JClass('clojure.lang.Symbol')


@pytest.fixture
def java_boolean():
    return jpype.JClass('java.lang.Boolean')


@pytest.fixture
def java_string():
    return jpype.JClass('java.lang.String')


@pytest.fixture
def java_long():
    return jpype.JClass('java.lang.Long')


@pytest.fixture
def java_int():
    return jpype.JClass('java.lang.Integer')


@pytest.fixture
def java_arrays():
    return jpype.JClass('java.util.Arrays')


@pytest.fixture
def java_persistant_array_map():
    return jpype.JClass('clojure.lang.PersistentArrayMap')


@pytest.fixture
def java_map_entry():
    return jpype.JClass('clojure.lang.MapEntry')


@pytest.fixture
def java_keyword():
    return jpype.JClass('clojure.lang.Keyword')


@pytest.fixture
def java_hash_map():
    return jpype.JClass('java.util.HashMap')


@pytest.fixture(scope='module')
def clojure_loaded(clojure):
    duckling_load = clojure.var("duckling.core", "load!")
    duckling_load.invoke()
    return clojure


@pytest.fixture
def clojure_parse(clojure_loaded):
    return clojure_loaded.var("duckling.core", "parse")


@pytest.fixture(scope='module')
def duckling():
    return Duckling()


@pytest.fixture(scope='module')
def duckling_loaded(duckling):
    duckling.load()
    return duckling


def test_load(duckling):
    duckling.load()
    assert duckling._is_loaded is True


def test_not_load():
    duckling = Duckling()
    assert duckling._is_loaded is False
    with pytest.raises(RuntimeError):
        duckling.parse('')


def test_parse(duckling_loaded, test_input):
    result = duckling_loaded.parse(test_input)
    assert len(result) == 5


def test_parse_with_reference_time(duckling_loaded, test_time_input, dec_30):
    result = duckling_loaded.parse(test_time_input, reference_time=dec_30)
    assert parser.parse(u'1990-12-30').date() + timedelta(days=1) == parser.parse(
        result[0][u'value'][u'values'][0][u'value']).date()


def test_parse_with_filter(duckling_loaded, test_input, two_pm):
    result = duckling_loaded.parse(test_input, dim_filter=Dim.TIME)

    assert len(result) == 1
    assert result[0][u'dim'] == Dim.TIME

    result_val = result[0][u'value'][u'values'][0][u'value']
    result_datetime = parser.parse(result_val)

    assert result_datetime.time() == two_pm.time()


def test_parse_result(clojure_parse, duckling, test_input):
    result = clojure_parse.invoke(Language.ENGLISH, test_input)
    duckling_result = duckling._parse_result(result)

    assert type(duckling_result) == list
    assert len(duckling_result) == 5


def test_parse_dict(duckling, java_symbol, java_keyword, java_map_entry, java_persistant_array_map, two_pm_str):
    input_symbol_type = java_symbol.create(u'type')
    input_keyword_type = java_keyword.intern(input_symbol_type)

    input_symbol_value = java_symbol.create(u'value')
    input_keyword_value = java_keyword.intern(input_symbol_value)

    input_symbol_grain = java_symbol.create(u'grain')
    input_keyword_grain = java_keyword.intern(input_symbol_grain)
    input_symbol_hour = java_symbol.create(u'hour')
    input_keyword_hour = java_keyword.intern(input_symbol_hour)

    test_array_map = java_persistant_array_map([
        input_keyword_type, 'value',
        input_keyword_value, two_pm_str,
        input_keyword_grain, input_keyword_hour
    ])

    result = duckling._parse_dict(test_array_map)

    assert type(result) == dict
    assert len(result) == 3


def test_parse_list(duckling, java_arrays, java_persistant_array_map, java_symbol, java_keyword):
    input_symbol = java_symbol.create(u'type')
    input_keyword = java_keyword.intern(input_symbol)

    test_array_map = java_persistant_array_map([input_keyword, 'value'])
    test_list = java_arrays.asList([test_array_map])

    result = duckling._parse_list(test_list)

    assert type(result) == list
    assert len(result) == 1


def test_parse_value(duckling, two_pm_str, java_long, java_string):
    assert duckling._parse_value(two_pm_str, Dim.TIME) == two_pm_str

    number_dims = {Dim.TEMPERATURE, Dim.NUMBER, Dim.ORDINAL,
                   Dim.DISTANCE, Dim.VOLUME, Dim.AMOUNTOFMONEY, Dim.DURATION}
    for dim in number_dims:
        assert duckling._parse_value(java_long(2), dim) == 2

    string_dims = {Dim.EMAIL, Dim.URL, Dim.PHONENUMBER}
    for dim in string_dims:
        assert duckling._parse_value(java_string(u'test'), dim) == u'test'

    assert duckling._parse_value(java_string(u'test')) == u'test'


def test_parse_float(duckling, java_long):
    assert duckling._parse_float(java_long(2)) == 2


def test_parse_int(duckling, java_int):
    assert duckling._parse_int(java_int(2)) == 2


def test_parse_time(duckling, two_pm, two_pm_str):
    assert duckling._parse_time(two_pm_str) == two_pm_str
    duckling.parse_datetime = True
    assert duckling._parse_time(two_pm_str) == two_pm
    duckling.parse_datetime = False


def test_parse_string(duckling, java_string):
    assert duckling._parse_string(java_string(u'test')) == u'test'


def test_parse_symbol(duckling, java_symbol):
    input_symbol = java_symbol.create(u':test')
    assert duckling._parse_symbol(input_symbol) == u'test'


def test_parse_boolean(duckling, java_boolean):
    assert duckling._parse_boolean(java_boolean(True)) is True
    assert duckling._parse_boolean(java_boolean(False)) is False


def test_parse_time_input(duckling_loaded):
    result = duckling_loaded.parse(
        'the day before labor day 2020', dim_filter=Dim.TIME)

    assert len(result) == 2
    assert result[0][u'dim'] == Dim.TIME

    result_val = result[0][u'value'][u'values'][0][u'value']
    result_datetime = parser.parse(result_val)

    assert result_datetime == datetime(
        2020, 9, 6, 0, 0, 0, 0, tzinfo=tzlocal())


def test_parse_temperature_input(duckling_loaded,
                                 answer_to_the_ultimate_question_of_life_the_universe_and_everything):
    result = duckling_loaded.parse(
        '42 degrees', dim_filter=Dim.TEMPERATURE)

    assert len(result) == 1
    assert result[0][u'dim'] == Dim.TEMPERATURE

    result_val = result[0][u'value']['value']
    assert result_val == answer_to_the_ultimate_question_of_life_the_universe_and_everything


def test_parse_number_input(duckling_loaded,
                            answer_to_the_ultimate_question_of_life_the_universe_and_everything):
    result = duckling_loaded.parse(
        'forty-two', dim_filter=Dim.NUMBER)

    assert len(result) == 1
    assert result[0][u'dim'] == Dim.NUMBER

    result_val = result[0][u'value']['value']
    assert result_val == answer_to_the_ultimate_question_of_life_the_universe_and_everything


def test_parse_ordinal_input(duckling_loaded,
                             answer_to_the_ultimate_question_of_life_the_universe_and_everything):
    result = duckling_loaded.parse('second', dim_filter=Dim.ORDINAL)

    assert len(result) == 1
    assert result[0][u'dim'] == Dim.ORDINAL

    result_val = result[0][u'value']['value']
    assert result_val == 2


def test_parse_distance_input(duckling_loaded,
                              answer_to_the_ultimate_question_of_life_the_universe_and_everything):
    result = duckling_loaded.parse(
        '42km', dim_filter=Dim.DISTANCE)

    assert len(result) == 1
    assert result[0][u'dim'] == Dim.DISTANCE

    result_val = result[0][u'value']['value']
    assert result_val == answer_to_the_ultimate_question_of_life_the_universe_and_everything


def test_parse_volume_input(duckling_loaded,
                            answer_to_the_ultimate_question_of_life_the_universe_and_everything):
    result = duckling_loaded.parse(
        '42liters', dim_filter=Dim.VOLUME)

    assert len(result) == 1
    assert result[0][u'dim'] == Dim.VOLUME

    result_val = result[0][u'value']['value']
    assert result_val == answer_to_the_ultimate_question_of_life_the_universe_and_everything


def test_parse_amount_of_money_input(duckling_loaded,
                                     answer_to_the_ultimate_question_of_life_the_universe_and_everything):
    result = duckling_loaded.parse(
        '$42', dim_filter=Dim.AMOUNTOFMONEY)

    assert len(result) == 1
    assert result[0][u'dim'] == Dim.AMOUNTOFMONEY

    result_val = result[0][u'value']['value']
    assert result_val == answer_to_the_ultimate_question_of_life_the_universe_and_everything


def test_parse_duration_input(duckling_loaded,
                              answer_to_the_ultimate_question_of_life_the_universe_and_everything):
    result = duckling_loaded.parse(
        '42 days', dim_filter=Dim.DURATION)

    assert len(result) == 1
    assert result[0][u'dim'] == Dim.DURATION

    result_val = result[0][u'value']['value']
    assert result_val == answer_to_the_ultimate_question_of_life_the_universe_and_everything


def test_parse_email_input(duckling_loaded):
    test_input = 'contact@frank-blechschmidt.com'
    result = duckling_loaded.parse(
        'contact me at {input}'.format(input=test_input),
        dim_filter=Dim.EMAIL
    )

    assert len(result) == 1
    assert result[0][u'dim'] == Dim.EMAIL

    result_val = result[0][u'value']['value']
    assert result_val == test_input


def test_parse_url_input(duckling_loaded):
    test_input = 'sap.com'
    result = duckling_loaded.parse(
        'website under construction: {input}'.format(input=test_input),
        dim_filter=Dim.URL
    )

    assert len(result) == 1
    assert result[0][u'dim'] == Dim.URL

    result_val = result[0][u'value']['value']
    assert result_val == test_input


def test_parse_phone_number_input(duckling_loaded):
    test_input = '(650)-424-4242 '
    result = duckling_loaded.parse(
        '{input}is a random phone number'.format(input=test_input),
        dim_filter=Dim.PHONENUMBER
    )

    assert len(result) == 1
    assert result[0][u'dim'] == Dim.PHONENUMBER

    result_val = result[0][u'value']['value']
    assert result_val == test_input

def test_multiple_dims(duckling_loaded):
    test_input = '42'
    result = duckling_loaded.parse(
        'it will be ready in {input} weeks'.format(input=test_input),
        dim_filter=[Dim.DISTANCE, Dim.NUMBER]
    )

    assert len(result) == 2
    assert result[0][u'value']['value'] == float(test_input)
    assert result[1][u'value']['value'] == float(test_input)

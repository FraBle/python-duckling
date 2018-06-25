# duckling
*Python wrapper for wit.ai's [Duckling](https://github.com/wit-ai/duckling) Clojure library*

#### Build Status

![CircleCi Build Status](https://circleci.com/gh/FraBle/python-duckling.svg?style=shield&circle-token=ce50d3fb4d377c59a8eb1a25f3467dd0ebe9457a)

#### Pypi Version

[![PyPI version](https://badge.fury.io/py/duckling.svg)](https://badge.fury.io/py/duckling)

#### Introduction

This library is inspired by [Edward Stone](https://github.com/eadmundo)'s [Python wrapper for natty](https://github.com/eadmundo/python-natty).

It provides a low-level access to Duckling's `parse()` function as well as a wrapper for easy access.

#### Requirements

`python-duckling` requires an installed JVM (either plain JRE or JDK) to run since Duckling itself is implemented in Clojure (which is leveraging the JVM).

#### Examples
##### High-level (DucklingWrapper)
```python
    d = DucklingWrapper()
    print(d.parse_time(u'Let\'s meet at 11:45am'))
    # [{u'dim': u'time', u'end': 21, u'start': 11, u'value': {u'value': u'2016-10-14T11:45:00.000-07:00', u'others': [u'2016-10-14T11:45:00.000-07:00', u'2016-10-15T11:45:00.000-07:00', u'2016-10-16T11:45:00.000-07:00']}, u'text': u'at 11:45am'}]
    print(d.parse_temperature(u'Let\'s change the temperatur from thirty two celsius to 65 degrees'))
    # [{u'dim': u'temperature', u'end': 65, u'start': 55, u'value': {u'unit': u'degree', u'value': 65.0}, u'text': u'65 degrees'}, {u'dim': u'temperature', u'end': 51, u'start': 33, u'value': {u'unit': u'celsius', u'value': 32.0}, u'text': u'thirty two celsius'}]
```
##### Low-level (Duckling)
```python
    d = Duckling()
    d.load() # always load the model first
    print(d.parse('tomorrow'))
    # [{u'body': u'tomorrow', u'dim': u'time', u'end': 8, u'value': {u'values': [{u'grain': u'day', u'type': u'value', u'value': u'2016-10-10T00:00:00.000-07:00'}], u'grain': u'day', u'type': u'value', u'value': u'2016-10-10T00:00:00.000-07:00'}, u'start': 0}]
```
Other examples can be found in the [test](https://github.com/FraBle/python-duckling/tree/master/duckling/test) directory.

#### Functions
##### High-level (DucklingWrapper)
```python
DucklingWrapper(jvm_started=False, parse_datetime=False, language=Language.ENGLISH, minimum_heap_size='128m', maximum_heap_size='2048m'):

    """Simplified Python wrapper for Duckling by wit.ai.

    Attributes:
        jvm_started: Optional attribute to specify if the JVM has already been
            started (with all Java dependencies loaded).
        parse_datetime: Optional attribute to specify if datetime string should
            be parsed with datetime.strptime(). Default is False.
        language: Optional attribute to specify language to be used with
            Duckling. Default is Language.ENGLISH.
        minimum_heap_size: Optional attribute to set initial and minimum heap
            size. Default is 128m.
        maximum_heap_size: Optional attribute to set maximum heap size. Default
            is 2048m.
    """

duckling_wrapper.parse(self, input_str, reference_time=''):
        """Parses input with Duckling for all dims.

        Args:
            input_str: An input string, e.g. 'You owe me twenty bucks, please
                call me today'.
            reference_time: Optional reference time for Duckling.

        Returns:
            A preprocessed list of results (dicts) from Duckling output.
        """

duckling_wrapper.parse_time(self, input_str, reference_time=''):
        """Parses input with Duckling for occurences of times.

        Args:
            input_str: An input string, e.g. 'Let's meet at 11:45am'.
            reference_time: Optional reference time for Duckling.

        Returns:
            A preprocessed list of results (dicts) from Duckling output.
        """

duckling_wrapper.parse_timezone(self, input_str):
        """Parses input with Duckling for occurences of timezones.

        Args:
            input_str: An input string, e.g. 'My timezone is pdt'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output.
        """

duckling_wrapper.parse_temperature(self, input_str):
        """Parses input with Duckling for occurences of temperatures.

        Args:
            input_str: An input string, e.g. 'Let's change the temperature from
                thirty two celsius to 65 degrees'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output.
        """

duckling_wrapper.parse_number(self, input_str):
        """Parses input with Duckling for occurences of numbers.

        Args:
            input_str: An input string, e.g. 'I'm 25 years old'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output.
        """

duckling_wrapper.parse_ordinal(self, input_str):
        """Parses input with Duckling for occurences of ordinals.

        Args:
            input_str: An input string, e.g. 'I'm first, you're 2nd'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output.
        """

duckling_wrapper.parse_distance(self, input_str):
        """Parses input with Duckling for occurences of distances.

        Args:
            input_str: An input string, e.g. 'I commute 5 miles everyday'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output.
        """

duckling_wrapper.parse_volume(self, input_str):
        """Parses input with Duckling for occurences of volumes.

        Args:
            input_str: An input string, e.g. '1 gallon is 3785ml'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output.
        """

duckling_wrapper.parse_money(self, input_str):
        """Parses input with Duckling for occurences of moneys.

        Args:
            input_str: An input string, e.g. 'You owe me 10 dollars'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output.
        """

duckling_wrapper.parse_duration(self, input_str):
        """Parses input with Duckling for occurences of durations.

        Args:
            input_str: An input string, e.g. 'I ran for 2 hours today'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output.
        """

duckling_wrapper.parse_email(self, input_str):
        """Parses input with Duckling for occurences of emails.

        Args:
            input_str: An input string, e.g. 'Shoot me an email at
                contact@frank-blechschmidt.com'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output.
        """

duckling_wrapper.parse_url(self, input_str):
        """Parses input with Duckling for occurences of urls.

        Args:
            input_str: An input string, e.g. 'http://frank-blechschmidt.com is
                under construction, but you can check my github
                github.com/FraBle'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output.
        """

duckling_wrapper.parse_phone_number(self, input_str):
        """Parses input with Duckling for occurences of phone numbers.

        Args:
            input_str: An input string, e.g. '424-242-4242 is obviously a fake
                number'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output.
        """
```

##### Low-level (Duckling)
```python
Duckling(jvm_started=False, parse_datetime=False, minimum_heap_size='128m', maximum_heap_size='2048m'):

    """Python wrapper for Duckling by wit.ai.

    Attributes:
        jvm_started: Optional attribute to specify if the JVM has already been
            started (with all Java dependencies loaded).
        parse_datetime: Optional attribute to specify if datetime string 
            should be parsed with datetime.strptime(). Default is False.
        minimum_heap_size: Optional attribute to set initial and minimum heap
            size. Default is 128m.
        maximum_heap_size: Optional attribute to set maximum heap size. Default
            is 2048m.
    """

duckling.load(self, languages=[]):
        """Loads the Duckling corpus.

        Languages can be specified, defaults to all.

        Args:
            languages: Optional parameter to specify languages,
                e.g. [Duckling.ENGLISH, Duckling.FRENCH] or supported ISO 639-1 Codes (e.g. ["en", "fr"])
        """

duckling.parse(self, input_str, language=Language.ENGLISH, dim_filter=None, reference_time=''):
        """Parses datetime information out of string input.

        It invokes the Duckling.parse() function in Clojure.
        A language can be specified, default is English.

        Args:
            input_str: The input as string that has to be parsed.
            language: Optional parameter to specify language,
                e.g. Duckling.ENGLISH.
            dim_filter: Optional parameter to specify a single filter or
                list of filters for dimensions in Duckling.
            reference_time: Optional reference time for Duckling.

        Returns:
            A list of dicts with the result from the Duckling.parse() call.

        Raises:
            RuntimeError: An error occurres when Duckling model is not loaded
                via load().
        """
```

#### Future Work
- Support new Haskell version of Duckling (probably in new repo)
    + [Blog post](https://wit.ai/blog/2017/05/01/new-duckling)
    + [Github](https://github.com/facebookincubator/duckling)

#### Credit
- [wit.ai](https://wit.ai/) for their awesome work and tools for the NLP community
- [Edward Stone](https://github.com/eadmundo) for the inspiration to write a python wrapper for library from a different programming language

#### Contributors
- [Tom Bocklisch (tmbo)](https://github.com/tmbo)
- [Laurent Valette (LaurentValette)](https://github.com/LaurentValette)
- [oziee](https://github.com/oziee)

#### License
- Apache License 2.0 (check the LICENSE file)

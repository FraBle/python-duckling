# duckling
*Python wrapper for wit.ai's [Duckling](https://github.com/wit-ai/duckling) Clojure library*

#### Build Status

![CircleCi Build Status](https://circleci.com/gh/FraBle/python-duckling.svg?style=shield&circle-token=ce50d3fb4d377c59a8eb1a25f3467dd0ebe9457a)

#### Introduction

This library is inspired by [Edward Stone](https://github.com/eadmundo)'s [Python wrapper for natty](https://github.com/eadmundo/python-natty).

It provides a low-level access to Duckling's `parse()` function as well as a wrapper for easy access.

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

#### Future Work
- fixing all upcoming bug reports and issues.

#### Credit
- [wit.ai](https://wit.ai/) for their awesome work and tools for the NLP community
- [Edward Stone](https://github.com/eadmundo) for the inspiration to write a python wrapper for library from a different programming language

#### License
- Apache License 2.0 (check the LICENSE file)

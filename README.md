# duckling
*Python wrapper for wit.ai's [Duckling](https://github.com/wit-ai/duckling) Clojure library*

#### Build Status

![CircleCi Build Status](https://circleci.com/gh/FraBle/python-duckling.svg?style=shield&circle-token=ce50d3fb4d377c59a8eb1a25f3467dd0ebe9457a)

#### Introduction

This library is inspired by [Edward Stone](https://github.com/eadmundo)'s [Python wrapper for natty](https://github.com/eadmundo/python-natty).

It provides a low-level access to Duckling's `parse()` function.

#### Example
```python
    d = Duckling()
    d.load() # always load the model first
    print(d.parse('tomorrow'))
    # [{u'body': u'tomorrow', u'dim': u'time', u'end': 8, u'value': {u'values': [{u'grain': u'day', u'type': u'value', u'value': u'2016-10-10T00:00:00.000-07:00'}], u'grain': u'day', u'type': u'value', u'value': u'2016-10-10T00:00:00.000-07:00'}, u'start': 0}]
```
Other examples can be found in the test directory.

#### Future Work
- provide simplified second interface to directly prodiving entities from input instead if Duckling's result dict.
- fixing all upcoming bug reports and issues.

#### Credit
- [wit.ai](https://wit.ai/) for their awesome work and tools for the NLP community
- [Edward Stone](https://github.com/eadmundo) for the inspiration to write a python wrapper for library from a different programming language

#### Credit
- Apache License 2.0 (check the LICENSE file)

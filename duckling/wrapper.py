from .duckling import Duckling
from .language import Language
from .dim import Dim


class DucklingWrapper(object):

    """Simplified Python wrapper for Duckling by wit.ai.

    Attributes:
        jvm_started: Optional attribute to specify if the JVM has already been
            started (with all Java dependencies loaded).
        parse_datetime: Optional attribute to specify if datetime string should
            be parsed with datetime.strptime(). Default is False.
        language: Optional attribute to specify language to be used with
            Duckling. Default is Language.ENGLISH.
    """

    def __init__(self, jvm_started=False, parse_datetime=False, language=Language.ENGLISH):
        super(DucklingWrapper, self).__init__()
        self.language = language
        self.duckling = Duckling(
            jvm_started=jvm_started, parse_datetime=parse_datetime)
        self.duckling.load()
        self._dims = {
            Dim.TIME:           self._parse_time,
            Dim.TEMPERATURE:    self._parse_number_with_unit,
            Dim.NUMBER:         self._parse_basic_info,
            Dim.ORDINAL:        self._parse_basic_info,
            Dim.DISTANCE:       self._parse_number_with_unit,
            Dim.VOLUME:         self._parse_volume,
            Dim.AMOUNTOFMONEY:  self._parse_number_with_unit,
            Dim.DURATION:       self._parse_duration,
            Dim.EMAIL:          self._parse_basic_info,
            Dim.URL:            self._parse_basic_info,
            Dim.PHONENUMBER:    self._parse_basic_info,
            Dim.TIMEZONE:       self._parse_basic_info
        }

    def _parse(self, input_str, dim=None):
        result = []
        duckling_result = self.duckling.parse(
            input_str, self.language, dim_filter=dim)
        for entry in duckling_result:
            result_entry = self._dims[entry[u'dim']](entry)
            result.append(result_entry)
        return result

    def _parse_basic_info(self, duckling_result_entry):
        result_entry = {
            u'dim': duckling_result_entry[u'dim'],
            u'text': duckling_result_entry[u'body'],
            u'start': duckling_result_entry[u'start'],
            u'end': duckling_result_entry[u'end'],
            u'value': {
                u'value': duckling_result_entry[u'value'].get(u'value', None)
            }
        }
        return result_entry

    def _parse_number_with_unit(self, duckling_result_entry):
        result_entry = self._parse_basic_info(duckling_result_entry)
        result_entry[u'value'].update({
            u'unit': duckling_result_entry[u'value'].get(u'unit', None)
        })
        return result_entry

    def _is_interval(self, duckling_result_entry):
        return u'from' in duckling_result_entry[u'value'] or \
            u'to' in duckling_result_entry[u'value']

    def _parse_interval(self, result_entry, duckling_result_entry):
        result_entry[u'value'].update({
            u'value': {
                u'to': duckling_result_entry[u'value'].get(u'to', {}).get(u'value', None),
                u'from': duckling_result_entry[u'value'].get(u'from', {}).get(u'value', None)
            },
            u'others': []
        })
        for value in duckling_result_entry[u'value'][u'values']:
            result_entry[u'value'][u'others'].append({
                u'to': value.get(u'to', {}).get(u'value', None),
                u'from': value.get(u'from', {}).get(u'value', None)
            })
        return result_entry

    def _parse_time(self, duckling_result_entry):
        result_entry = self._parse_basic_info(duckling_result_entry)
        if self._is_interval(duckling_result_entry):
            return self._parse_interval(result_entry, duckling_result_entry)
        result_entry[u'value'].update({
            u'others': []
        })
        for value in duckling_result_entry[u'value'][u'values']:
            result_entry[u'value'][u'others'].append(value[u'value'])
        return result_entry

    def _parse_volume(self, duckling_result_entry):
        result_entry = self._parse_basic_info(duckling_result_entry)
        result_entry[u'value'].update({
            u'unit': duckling_result_entry[u'value'][u'unit']
            if u'unit' in duckling_result_entry[u'value'] else None,
            u'latent': duckling_result_entry[u'latent']
            if u'latent' in duckling_result_entry else False
        })
        return result_entry

    def _parse_duration(self, duckling_result_entry):
        result_entry = self._parse_basic_info(duckling_result_entry)
        result_entry[u'value'].update({
            u'unit': duckling_result_entry[u'value'][u'unit']
            if u'unit' in duckling_result_entry[u'value'] else None,
            u'year': duckling_result_entry[u'value'][u'year']
            if u'year' in duckling_result_entry[u'value'] else None,
            u'month': duckling_result_entry[u'value'][u'month']
            if u'month' in duckling_result_entry[u'value'] else None,
            u'day': duckling_result_entry[u'value'][u'day']
            if u'day' in duckling_result_entry[u'value'] else None,
            u'hour': duckling_result_entry[u'value'][u'hour']
            if u'hour' in duckling_result_entry[u'value'] else None,
            u'minute': duckling_result_entry[u'value'][u'minute']
            if u'minute' in duckling_result_entry[u'value'] else None,
            u'second': duckling_result_entry[u'value'][u'second']
            if u'second' in duckling_result_entry[u'value'] else None
        })
        return result_entry

    # Public API

    def parse(self, input_str):
        """Parses input with Duckling for all dims.

        Args:
            input_str: An input string, e.g. 'You owe me twenty bucks, please
                call me today'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output. For
            example:

            [
               {
                  "dim":"number",
                  "end":17,
                  "start":11,
                  "value":{
                     "value":20.0
                  },
                  "text":"twenty"
               },
               {
                  "dim":"time",
                  "end":45,
                  "start":40,
                  "value":{
                     "value":"2016-10-10T00:00:00.000-07:00",
                     "others":[
                        "2016-10-10T00:00:00.000-07:00"
                     ]
                  },
                  "text":"today"
               },
               {
                  "dim":"amount-of-money",
                  "end":23,
                  "start":11,
                  "value":{
                     "unit":null,
                     "value":20.0
                  },
                  "text":"twenty bucks"
               },
               {
                  "dim":"distance",
                  "end":17,
                  "start":11,
                  "value":{
                     "unit":null,
                     "value":20.0
                  },
                  "text":"twenty"
               },
               {
                  "dim":"volume",
                  "end":17,
                  "start":11,
                  "value":{
                     "latent":true,
                     "unit":null,
                     "value":20.0
                  },
                  "text":"twenty"
               },
               {
                  "dim":"temperature",
                  "end":17,
                  "start":11,
                  "value":{
                     "unit":null,
                     "value":20.0
                  },
                  "text":"twenty"
               },
               {
                  "dim":"time",
                  "end":17,
                  "start":11,
                  "value":{
                     "value":"2020-01-01T00:00:00.000-08:00",
                     "others":[
                        "2020-01-01T00:00:00.000-08:00"
                     ]
                  },
                  "text":"twenty"
               }
            ]
        """
        return self._parse(input_str)

    def parse_time(self, input_str):
        """Parses input with Duckling for occurences of times.

        Args:
            input_str: An input string, e.g. 'Let's meet at 11:45am'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output. For
            example:

            [
               {
                  "dim":"time",
                  "end":21,
                  "start":11,
                  "value":{
                     "value":"2016-10-11T11:45:00.000-07:00",
                     "others":[
                        "2016-10-11T11:45:00.000-07:00",
                        "2016-10-12T11:45:00.000-07:00",
                        "2016-10-13T11:45:00.000-07:00"
                     ]
                  },
                  "text":"at 11:45am"
               }
            ]
        """
        return self._parse(input_str, dim=Dim.TIME)

    def parse_timezone(self, input_str):
        """Parses input with Duckling for occurences of timezones.

        Args:
            input_str: An input string, e.g. 'My timezone is pdt'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output. For
            example:

            [
               {
                  "dim":"timezone",
                  "end":18,
                  "start":15,
                  "value":{
                     "value":"PDT"
                  },
                  "text":"pdt"
               }
            ]
        """
        return self._parse(input_str, dim=Dim.TIMEZONE)

    def parse_temperature(self, input_str):
        """Parses input with Duckling for occurences of temperatures.

        Args:
            input_str: An input string, e.g. 'Let's change the temperature from
                thirty two celsius to 65 degrees'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output. For
            example:

            [
               {
                  "dim":"temperature",
                  "end":65,
                  "start":55,
                  "value":{
                     "unit":"degree",
                     "value":65.0
                  },
                  "text":"65 degrees"
               },
               {
                  "dim":"temperature",
                  "end":51,
                  "start":33,
                  "value":{
                     "unit":"celsius",
                     "value":32.0
                  },
                  "text":"thirty two celsius"
               }
            ]
        """
        return self._parse(input_str, dim=Dim.TEMPERATURE)

    def parse_number(self, input_str):
        """Parses input with Duckling for occurences of numbers.

        Args:
            input_str: An input string, e.g. 'I'm 25 years old'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output. For
            example:

            [
               {
                  "dim":"number",
                  "end":6,
                  "start":4,
                  "value":{
                     "value":25.0
                  },
                  "text":"25"
               }
            ]
        """
        return self._parse(input_str, dim=Dim.NUMBER)

    def parse_ordinal(self, input_str):
        """Parses input with Duckling for occurences of ordinals.

        Args:
            input_str: An input string, e.g. 'I'm first, you're 2nd'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output. For
            example:

            [
               {
                  "dim":"ordinal",
                  "end":9,
                  "start":4,
                  "value":{
                     "value":1
                  },
                  "text":"first"
               },
               {
                  "dim":"ordinal",
                  "end":21,
                  "start":18,
                  "value":{
                     "value":2
                  },
                  "text":"2nd"
               }
            ]
        """
        return self._parse(input_str, dim=Dim.ORDINAL)

    def parse_distance(self, input_str):
        """Parses input with Duckling for occurences of distances.

        Args:
            input_str: An input string, e.g. 'I commute 5 miles everyday'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output. For
            example:

            [
               {
                  "dim":"distance",
                  "end":17,
                  "start":10,
                  "value":{
                     "unit":"mile",
                     "value":5.0
                  },
                  "text":"5 miles"
               }
            ]
        """
        return self._parse(input_str, dim=Dim.DISTANCE)

    def parse_volume(self, input_str):
        """Parses input with Duckling for occurences of volumes.

        Args:
            input_str: An input string, e.g. '1 gallon is 3785ml'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output. For
            example:

            [
               {
                  "dim":"volume",
                  "end":18,
                  "start":12,
                  "value":{
                     "latent":false,
                     "unit":"millilitre",
                     "value":3785.0
                  },
                  "text":"3785ml"
               },
               {
                  "dim":"volume",
                  "end":8,
                  "start":0,
                  "value":{
                     "latent":false,
                     "unit":"gallon",
                     "value":1.0
                  },
                  "text":"1 gallon"
               }
            ]
        """
        return self._parse(input_str, dim=Dim.VOLUME)

    def parse_money(self, input_str):
        """Parses input with Duckling for occurences of moneys.

        Args:
            input_str: An input string, e.g. 'You owe me 10 dollars'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output. For
            example:

            [
               {
                  "dim":"amount-of-money",
                  "end":21,
                  "start":11,
                  "value":{
                     "unit":"$",
                     "value":10.0
                  },
                  "text":"10 dollars"
               }
            ]
        """
        return self._parse(input_str, dim=Dim.AMOUNTOFMONEY)

    def parse_duration(self, input_str):
        """Parses input with Duckling for occurences of durations.

        Args:
            input_str: An input string, e.g. 'I ran for 2 hours today'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output. For
            example:

            [
               {
                  "dim":"duration",
                  "end":17,
                  "start":10,
                  "value":{
                     "hour":2,
                     "value":2.0,
                     "month":null,
                     "second":null,
                     "minute":null,
                     "year":null,
                     "day":null,
                     "unit":"hour"
                  },
                  "text":"2 hours"
               }
            ]
        """
        return self._parse(input_str, dim=Dim.DURATION)

    def parse_email(self, input_str):
        """Parses input with Duckling for occurences of emails.

        Args:
            input_str: An input string, e.g. 'Shoot me an email at
                contact@frank-blechschmidt.com'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output. For
            example:

            [
               {
                  "dim":"email",
                  "end":51,
                  "start":21,
                  "value":{
                     "value":"contact@frank-blechschmidt.com"
                  },
                  "text":"contact@frank-blechschmidt.com"
               }
            ]
        """
        return self._parse(input_str, dim=Dim.EMAIL)

    def parse_url(self, input_str):
        """Parses input with Duckling for occurences of urls.

        Args:
            input_str: An input string, e.g. 'http://frank-blechschmidt.com is
                under construction, but you can check my github
                github.com/FraBle'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output. For
            example:

            [
               {
                  "dim":"url",
                  "end":98,
                  "start":81,
                  "value":{
                     "value":"github.com/FraBle"
                  },
                  "text":"github.com/FraBle"
               },
               {
                  "dim":"url",
                  "end":29,
                  "start":0,
                  "value":{
                     "value":"http://frank-blechschmidt.com"
                  },
                  "text":"http://frank-blechschmidt.com"
               }
            ]
        """
        return self._parse(input_str, dim=Dim.URL)

    def parse_phone_number(self, input_str):
        """Parses input with Duckling for occurences of phone numbers.

        Args:
            input_str: An input string, e.g. '424-242-4242 is obviously a fake
                number'.

        Returns:
            A preprocessed list of results (dicts) from Duckling output. For
            example:

            [
               {
                  "dim":"phone-number",
                  "end":13,
                  "start":0,
                  "value":{
                     "value":"424-242-4242 "
                  },
                  "text":"424-242-4242 "
               }
            ]
        """
        return self._parse(input_str, dim=Dim.PHONENUMBER)

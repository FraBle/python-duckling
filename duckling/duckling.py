import os
import imp
import jpype
import socket
import threading
from distutils.util import strtobool
from dateutil import parser
from .dim import Dim
from .language import Language

if jpype.isJVMStarted() is not 1:
    jars = []
    for top, dirs, files in os.walk(imp.find_module('duckling')[1] + '/jars'):
        for nm in files:
            jars.append(os.path.join(top, nm))
    jpype.startJVM(
        jpype.getDefaultJVMPath(),
        "-Djava.class.path=%s" % os.pathsep.join(jars)
    )

socket.setdefaulttimeout(15)
lock = threading.Lock()

Clojure = jpype.JClass('clojure.java.api.Clojure')


class Duckling(object):

    """Python wrapper for Duckling by wit.ai.

    Attributes:
        parse_datetime: Optional attribute to specify if datetime string should 
            be parsed with datetime.strptime(). Default is False.
    """

    def __init__(self, parse_datetime=False):
        """Initializes Duckling.
        """

        self.parse_datetime = parse_datetime
        self._is_loaded = False

        try:
            # make it thread-safe
            if threading.activeCount() > 1:
                if jpype.isThreadAttachedToJVM() is not 1:
                    jpype.attachThreadToJVM()
            lock.acquire()
            # require the duckling Clojure lib
            require = Clojure.var("clojure.core", "require")
            require.invoke(Clojure.read("duckling.core"))
        finally:
            lock.release()

    def load(self):
        """Loads the Duckling corpus"""
        duckling_load = Clojure.var("duckling.core", "load!")
        duckling_load.invoke()
        self._is_loaded = True

    def parse(self, input_str, language=Language.ENGLISH, dim_filter=None):
        """Parses datetime information out of string input.

        It invokes the Duckling.parse() function in Clojure.
        A language can be specified, default is English.

        Args:
            input_str: The input as string that has to be parsed.
            language: Optional parameter to specify language,
                e.g. Duckling.ENGLISH.
            filter: Optional parameter to specify list of filters for
                dimensions in Duckling.

        Returns:
            A list of dicts with the result from Duckling.parse() call.

        Raises:
            RuntimeError: An error occurred when Duckling model is not loaded
                via load().
        """
        if self._is_loaded is False:
            raise RuntimeError(
                'Please load the model first by calling load()')
        duckling_parse = Clojure.var("duckling.core", "parse")

        filter_str = '[]'
        if dim_filter:
            filter_str = '[:{filter}]'.format(filter=dim_filter)

        duckling_result = duckling_parse.invoke(
            language, input_str, Clojure.read(filter_str))

        return self._parse_result(duckling_result)

    def _parse_result(self, duckling_result):
        _functions = {
            u'dim':    self._parse_symbol,
            u'body':   self._parse_string,
            u'start':  self._parse_number,
            u'end':    self._parse_number,
            u'latent': self._parse_boolean
        }

        result = []
        for duckling_entry in duckling_result.iterator():
            entry = {}
            for field in duckling_entry.iterator():
                key = field.getKey().toString()[1:]
                if key == u'value':
                    entry[key] = self._parse_dict(
                        field.getValue(), entry[u'dim'])
                else:
                    entry[key] = _functions[key](field.getValue())
            result.append(entry)
        return result

    def _parse_dict(self, java_dict, dim=None):
        _functions = {
            u'type':   self._parse_string,
            u'unit':   self._parse_string,
            u'day':   self._parse_string,
            u'grain':  self._parse_symbol,
            u'normalized':  self._parse_dict,
            u'values': self._parse_list
        }

        result = {}
        for field in java_dict.iterator():
            key = field.getKey().toString()[1:]
            if key == u'value':
                result[key] = self._parse_value(field.getValue(), dim)
            else:
                result[key] = _functions[key](field.getValue())
        return result

    def _parse_list(self, java_list):
        result = []
        for entry in java_list.iterator():
            result.append(self._parse_dict(entry))
        return result

    def _parse_number(self, java_number):
        return int(java_number.toString())

    def _parse_value(self, java_value, dim=None):
        _dims = {
            Dim.TIME:           self._parse_time,
            Dim.TEMPERATURE:    self._parse_number,
            Dim.NUMBER:         self._parse_number,
            Dim.ORDINAL:        self._parse_number,
            Dim.DISTANCE:       self._parse_number,
            Dim.VOLUME:         self._parse_number,
            Dim.AMOUNTOFMONEY:  self._parse_number,
            Dim.DURATION:       self._parse_number,
            Dim.EMAIL:          self._parse_string,
            Dim.URL:            self._parse_string,
            Dim.PHONENUMBER:    self._parse_string,
        }
        if not dim:
            return self._parse_string(java_value)
        return _dims[dim](java_value)

    def _parse_time(self, time):
        if self.parse_datetime:
            return parser.parse(time)
        else:
            return self._parse_string(time)

    def _parse_string(self, java_string):
        return java_string

    def _parse_symbol(self, java_symbol):
        return java_symbol.toString()[1:]

    def _parse_boolean(self, java_boolean):
        return bool(strtobool(java_boolean.toString()))

import os
import imp
import jpype
import socket
import threading
from six import string_types
from distutils.util import strtobool
from dateutil import parser
from .dim import Dim
from .language import Language

socket.setdefaulttimeout(15)


class Duckling(object):

    """Python wrapper for Duckling by wit.ai.

    Attributes:
        jvm_started: Optional attribute to specify if the JVM has already been
            started (with all Java dependencies loaded).
        parse_datetime: Optional attribute to specify if datetime string should 
            be parsed with datetime.strptime(). Default is False.
    """

    def __init__(self, jvm_started=False, parse_datetime=False):
        """Initializes Duckling.
        """

        self.parse_datetime = parse_datetime
        self._is_loaded = False
        self._lock = threading.Lock()

        if not jvm_started:
            self._classpath = self._create_classpath()
            self._start_jvm()

        try:
            # make it thread-safe
            if threading.activeCount() > 1:
                if jpype.isThreadAttachedToJVM() is not 1:
                    jpype.attachThreadToJVM()
            self._lock.acquire()

            self.clojure = jpype.JClass('clojure.java.api.Clojure')
            # require the duckling Clojure lib
            require = self.clojure.var("clojure.core", "require")
            require.invoke(self.clojure.read("duckling.core"))
        finally:
            self._lock.release()

    def _start_jvm(self):
        if jpype.isJVMStarted() is not 1:
            jpype.startJVM(
                jpype.getDefaultJVMPath(),
                '-Djava.class.path={classpath}'.format(
                    classpath=self._classpath)
            )

    def _create_classpath(self):
        jars = []
        for top, dirs, files in os.walk(os.path.join(imp.find_module('duckling')[1], 'jars')):
            for file_name in files:
                if file_name.endswith('.jar'):
                    jars.append(os.path.join(top, file_name))
        return os.pathsep.join(jars)

    def load(self):
        """Loads the Duckling corpus"""
        duckling_load = self.clojure.var("duckling.core", "load!")
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
            dim_filter: Optional parameter to specify list of filters for
                dimensions in Duckling.

        Returns:
            A list of dicts with the result from the Duckling.parse() call.

        Raises:
            RuntimeError: An error occurres when Duckling model is not loaded
                via load().
        """
        if self._is_loaded is False:
            raise RuntimeError(
                'Please load the model first by calling load()')
        duckling_parse = self.clojure.var("duckling.core", "parse")

        filter_str = '[]'
        if dim_filter:
            filter_str = '[:{filter}]'.format(filter=dim_filter)

        duckling_result = duckling_parse.invoke(
            language, input_str, self.clojure.read(filter_str))

        return self._parse_result(duckling_result)

    def _parse_result(self, duckling_result):
        _functions = {
            u'dim':    self._parse_symbol,
            u'body':   self._parse_string,
            u'start':  self._parse_int,
            u'end':    self._parse_int,
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
            u'day':   self._parse_string,
            u'grain':  self._parse_symbol,
            u'values': self._parse_list,
            u'second': self._parse_int,
            u'minute': self._parse_int,
            u'hour': self._parse_int,
            u'day': self._parse_int,
            u'month': self._parse_int,
            u'year': self._parse_int,
        }
        _functions_with_dim = {
            u'value':   self._parse_value,
            u'values':   self._parse_list,
            u'normalized':  self._parse_dict,
            u'unit': self._parse_keyword
        }

        result = {}
        for field in java_dict.iterator():
            key = field.getKey().toString()[1:]
            if key in _functions_with_dim.keys():
                result[key] = _functions_with_dim[key](field.getValue(), dim)
            else:
                result[key] = _functions[key](field.getValue())
        return result

    def _parse_list(self, java_list, dim=None):
        result = []
        for entry in java_list.iterator():
            result.append(self._parse_dict(entry, dim))
        return result

    def _parse_float(self, java_number):
        return float(java_number.toString())

    def _parse_int(self, java_number):
        return int(java_number.toString())

    def _parse_value(self, java_value, dim=None):
        _dims = {
            Dim.TIME:           self._parse_time,
            Dim.TEMPERATURE:    self._parse_float,
            Dim.NUMBER:         self._parse_float,
            Dim.ORDINAL:        self._parse_int,
            Dim.DISTANCE:       self._parse_float,
            Dim.VOLUME:         self._parse_float,
            Dim.AMOUNTOFMONEY:  self._parse_float,
            Dim.DURATION:       self._parse_float,
            Dim.EMAIL:          self._parse_string,
            Dim.URL:            self._parse_string,
            Dim.PHONENUMBER:    self._parse_string,
            Dim.TIMEZONE:       self._parse_string
        }
        if not dim:
            return self._parse_string(java_value)
        return _dims[dim](java_value)

    def _parse_time(self, time):
        if self.parse_datetime:
            try:
                return parser.parse(time)
            except ValueError:
                return None
        else:
            return self._parse_string(time)

    def _parse_string(self, java_string):
        return java_string

    def _parse_keyword(self, java_keyword, dim=None):
        if dim == Dim.DURATION:
            if isinstance(java_keyword, string_types):
                return self._parse_string(java_keyword)
            return self._parse_symbol(java_keyword)
        else:
            return self._parse_string(java_keyword)

    def _parse_symbol(self, java_symbol):
        return java_symbol.toString()[1:]

    def _parse_boolean(self, java_boolean):
        return bool(strtobool(java_boolean.toString()))

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
        minimum_heap_size: Optional attribute to set initial and minimum heap
            size. Default is 128m.
        maximum_heap_size: Optional attribute to set maximum heap size. Default
            is 2048m.
    """

    def __init__(self,
                 jvm_started=False,
                 parse_datetime=False,
                 minimum_heap_size='128m',
                 maximum_heap_size='2048m'):
        """Initializes Duckling.
        """

        self.parse_datetime = parse_datetime
        self._is_loaded = False
        self._lock = threading.Lock()

        if not jvm_started:
            self._classpath = self._create_classpath()
            self._start_jvm(minimum_heap_size, maximum_heap_size)

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

    def _start_jvm(self, minimum_heap_size, maximum_heap_size):
        jvm_options = [
            '-Xms{minimum_heap_size}'.format(minimum_heap_size=minimum_heap_size),
            '-Xmx{maximum_heap_size}'.format(maximum_heap_size=maximum_heap_size),
            '-Djava.class.path={classpath}'.format(
                classpath=self._classpath)
        ]
        if jpype.isJVMStarted() is not 1:
            jpype.startJVM(
                jpype.getDefaultJVMPath(),
                *jvm_options
            )

    def _create_classpath(self):
        jars = []
        for top, dirs, files in os.walk(os.path.join(imp.find_module('duckling')[1], 'jars')):
            for file_name in files:
                if file_name.endswith('.jar'):
                    jars.append(os.path.join(top, file_name))
        return os.pathsep.join(jars)

    def load(self, languages=[]):
        """Loads the Duckling corpus.

        Languages can be specified, defaults to all.

        Args:
            languages: Optional parameter to specify languages,
                e.g. [Duckling.ENGLISH, Duckling.FRENCH] or supported ISO 639-1 Codes (e.g. ["en", "fr"])
        """
        duckling_load = self.clojure.var("duckling.core", "load!")
        clojure_hashmap = self.clojure.var("clojure.core", "hash-map")
        clojure_list = self.clojure.var("clojure.core", "list")

        if languages:
            # Duckling's load function expects ISO 639-1 Language Codes (e.g. "en")
            iso_languages = [Language.convert_to_iso(lang) for lang in languages]

            duckling_load.invoke(
                clojure_hashmap.invoke(
                    self.clojure.read(':languages'),
                    clojure_list.invoke(*iso_languages)
                )
            )
        else:
            duckling_load.invoke()

        self._is_loaded = True

    def parse(self, input_str, language=Language.ENGLISH, dim_filter=None, reference_time=''):
        """Parses datetime information out of string input.

        It invokes the Duckling.parse() function in Clojure.
        A language can be specified, default is English.

        Args:
            input_str: The input as string that has to be parsed.
            language: Optional parameter to specify language,
                e.g. Duckling.ENGLISH or supported ISO 639-1 Code (e.g. "en")
            dim_filter: Optional parameter to specify a single filter or
                list of filters for dimensions in Duckling.
            reference_time: Optional reference time for Duckling.

        Returns:
            A list of dicts with the result from the Duckling.parse() call.

        Raises:
            RuntimeError: An error occurres when Duckling model is not loaded
                via load().
        """
        if self._is_loaded is False:
            raise RuntimeError(
                'Please load the model first by calling load()')
        if threading.activeCount() > 1:
            if jpype.isThreadAttachedToJVM() is not 1:
                jpype.attachThreadToJVM()
        language = Language.convert_to_duckling_language_id(language)
        duckling_parse = self.clojure.var("duckling.core", "parse")
        duckling_time = self.clojure.var("duckling.time.obj", "t")
        clojure_hashmap = self.clojure.var("clojure.core", "hash-map")

        filter_str = '[]'
        if isinstance(dim_filter, string_types):
            filter_str = '[:{filter}]'.format(filter=dim_filter)
        elif isinstance(dim_filter, list):
            filter_str = '[{filter}]'.format(filter=' :'.join(dim_filter))
        if reference_time:
            duckling_result = duckling_parse.invoke(
                language,
                input_str,
                self.clojure.read(filter_str),
                clojure_hashmap.invoke(
                    self.clojure.read(':reference-time'),
                    duckling_time.invoke(
                        *self._parse_reference_time(reference_time))
                )
            )
        else:
            duckling_result = duckling_parse.invoke(
                language, input_str, self.clojure.read(filter_str))

        return self._parse_result(duckling_result)

    def _parse_reference_time(self, reference_time):
        date_info = parser.parse(reference_time)
        utc_offset = int(date_info.utcoffset().total_seconds()) // 3600 if date_info.utcoffset() else 0
        return (utc_offset, date_info.year,
                date_info.month, date_info.day,
                date_info.hour, date_info.minute,
                date_info.second)

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
            u'grain':  self._parse_symbol,
            u'values': self._parse_list,
            u'second': self._parse_int,
            u'minute': self._parse_int,
            u'hour': self._parse_int,
            u'day': self._parse_int,
            u'week': self._parse_int,
            u'month': self._parse_int,
            u'quarter': self._parse_int,
            u'year': self._parse_int,
        }
        _functions_with_dim = {
            u'value':   self._parse_value,
            u'values':   self._parse_list,
            u'normalized':  self._parse_dict,
            u'unit': self._parse_keyword,
            u'from':  self._parse_dict,
            u'to':  self._parse_dict
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
        if not dim or dim not in _dims:
            return self._parse_string(java_value)
        try:
            return _dims[dim](java_value)
        except AttributeError:
            return 'ERROR: {msg}'.format(msg=self._parse_string(java_value))

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

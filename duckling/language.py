class Language(object):

    """Helper class containing all supported languages
    """

    ARABIC = 'ar$core'
    DANISH = 'da$core'
    GERMAN = 'de$core'
    ENGLISH = 'en$core'
    SPANISH = 'es$core'
    ESTONIAN = 'et$core'
    FRENCH = 'fr$core'
    IRISH = 'ga$core'
    HEBREW = 'he$core'
    CROATIAN = 'hr$core'
    INDONESIAN = 'id$core'
    ITALIAN = 'it$core'
    JAPANESE = 'ja$core'
    KOREAN = 'ko$core'
    BIRMAN = 'my$core'
    NORVEGIAN = 'nb$core'
    DUTCH = 'nl$core'
    POLISH = 'pl$core'
    PORTUGUESE = 'pt$core'
    ROMANIAN = 'ro$core'
    RUSSIAN = 'ru$core'
    SWEDISH = 'sv$core'
    TURKISH = 'tr$core'
    UKRAINIAN = 'uk$core'
    VIETNAMESE = 'vi$core'
    CHINESE = 'zh$core'

    SUPPORTED_LANGUAGES = {
        ARABIC,
        DANISH,
        GERMAN,
        ENGLISH,
        SPANISH,
        ESTONIAN,
        FRENCH,
        IRISH,
        HEBREW,
        CROATIAN,
        INDONESIAN,
        ITALIAN,
        JAPANESE,
        KOREAN,
        BIRMAN,
        NORVEGIAN,
        DUTCH,
        POLISH,
        PORTUGUESE,
        ROMANIAN,
        RUSSIAN,
        SWEDISH,
        TURKISH,
        UKRAINIAN,
        VIETNAMESE,
        CHINESE,
    }

    @classmethod
    def is_supported(cls, lang):
        """Check if a language is supported by the current duckling version."""

        return lang in cls.SUPPORTED_LANGUAGES

    @classmethod
    def convert_to_duckling_language_id(cls, lang):
        """Ensure a language identifier has the correct duckling format and is supported."""

        if lang is not None and cls.is_supported(lang):
            return lang
        elif lang is not None and cls.is_supported(lang + "$core"):   # Support ISO 639-1 Language Codes (e.g. "en")
            return lang + "$core"
        else:
            raise ValueError("Unsupported language '{}'. Supported languages: {}".format(
                lang, ", ".join(cls.SUPPORTED_LANGUAGES)))

    @classmethod
    def convert_to_iso(cls, lang):
        return cls.convert_to_duckling_language_id(lang)[:2]

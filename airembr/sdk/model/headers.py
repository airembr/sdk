from typing import Optional
from user_agents import parse
from user_agents.parsers import UserAgent
from urllib.parse import urlparse, ParseResult

from airembr.sdk.dictionary.languages import language_codes_dict


class Headers(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_agent = None
        self._skips = None
        self._no_queue = None

    def get_ip(self) -> Optional[str]:
        try:
            forwarded_id = self['x-forwarded-for']

            if ',' not in forwarded_id:
                return forwarded_id

            all_ips = forwarded_id.split(',')
            return all_ips[0]  # First IP should be correct, other ips could be vpns or cloudflare
        except Exception:
            return None

    def get_origin(self) -> str:
        return self.get('origin', '')

    def _set_user_agent(self):
        if self._user_agent is None:
            try:
                user_agent = self['user-agent']
                self._user_agent = parse(user_agent)
            except Exception as e:
                pass

    @staticmethod
    def _parse_accept_language(accept_language_header):
        parsed_languages = []
        if accept_language_header:
            # Remove any whitespace and split the header into individual language tags
            language_tags = accept_language_header.replace(" ", "").split(",")

            # Parse each language tag and extract the language and quality values
            for tag in language_tags:
                parts = tag.split(";")
                language = parts[0]
                quality = 1.0  # Default quality value is 1.0

                # Extract the quality value if present
                for part in parts[1:]:
                    if part.startswith("q="):
                        quality = float(part[2:])

                if quality > 1:
                    quality = 1

                if quality < 0:
                    quality = 0

                parsed_languages.append((language, quality))

        return parsed_languages

    def get_languages(self):

        spoken_languages = []
        language_codes = []

        if 'accept-language' in self:
            languages = self._parse_accept_language(self['accept-language'])
            if languages:
                spoken_lang_codes = [language for (language, _) in languages if len(language) == 2]
                for lang_code in spoken_lang_codes:
                    if lang_code in language_codes_dict:
                        spoken_languages += language_codes_dict[lang_code]
                        language_codes.append(lang_code)

        return language_codes, spoken_languages

    def get_user_agent(self) -> Optional[UserAgent]:
        self._set_user_agent()
        return self._user_agent

    def is_bot(self) -> bool:
        if self.get_origin() == 'https://gtm-msr.appspot.com':
            return True
        _user_agent = self.get_user_agent()
        if _user_agent:
            return _user_agent.is_bot
        return False

    def get_origin_or_referer(self) -> Optional[ParseResult]:
        try:

            origin: str = self.get('origin', "")
            referer: str = self.get('referer', "")

            origin = origin.strip()
            referer = referer.strip()

            if not origin and not referer:
                return None

            available_sources = [item for item in [origin, referer] if item]

            if not available_sources:
                return None

            url = urlparse(available_sources[0])
            if not url.scheme or not url.netloc:
                return None
            return url

        except KeyError:
            return None

    def _get_skipped(self):
        if self._skips is None:
            _values = self.get('x-skip', None)
            if _values is None:
                self._skips = []
            else:
                self._skips = [item.strip() for item in _values.split(',')]
        return self._skips

    def should_process(self, service) -> bool:
        return service not in self._get_skipped()

    def _get_no_queue(self):
        if self._no_queue is None:
            _values = self.get('x-realtime', None)
            if _values is None:
                self._no_queue = []
            else:
                self._no_queue = [item.strip() for item in _values.split(',')]

        return self._no_queue

    def should_queue(self, service) -> bool:
        return service not in self._get_no_queue()

    def has_no_queue_services(self) -> bool:
        return len(self._get_no_queue()) > 0

    def should_identify_people(self) -> bool:
        return self.get('x-identify-people', '0').lower() == '1'
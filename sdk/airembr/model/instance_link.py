import re
from pydantic import ValidationInfo

class InstanceLink(str):
    _pattern = re.compile(r"""
        ^\s*                           # leading whitespace
        (?P<link>[A-Za-z0-9*\-_]+)      # link (added escape for hyphen and numbers)
        \s*                            # whitespace after link
        (?:
            :                          # colon separator
            \s*                        # whitespace after colon
            (?P<role>[A-Za-z0-9_\-]+)  # role (added escape for hyphen and numbers)
        )?                             # role is optional
        \s*$                           # trailing whitespace
        """, re.VERBOSE)

    # ── walidacja pydantic ─────────────────────────────────────
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: str, info: ValidationInfo | None = None):
        if v is None:
            raise ValueError(f"Instance has none value.")
        if not isinstance(v, str):
            raise ValueError(f"Invalid Instance format: {v!r}")

        if not cls._pattern.match(v):
            raise ValueError(f"Invalid Instance string format: {v!r}")
        return cls(v)

    def _parse_once(self):

        m = self._pattern.match(self)
        if not m:  # nie powinno się zdarzyć,
            raise ValueError("Invalid Instance")  # bo validate już sprawdza

        link = m.group("link").strip()

        role = m.group("role")
        role = role.strip() if role else None

        self._parsed_parts = (link, role)

    # ── semantics helpers ──────────────────────────────────────
    def parts(self) -> tuple[str | None, str | None]:
        """
        Zwraca (kind, role, id, actor_flag).
        Jeśli to pierwsze wywołanie, parsuje i cache’uje wynik;
        kolejne odczyty korzystają z cache’u.
        """
        if not hasattr(self, "_parsed_parts"):
            self._parse_once()
        return self._parsed_parts

    @property
    def link(self) -> str:
        return self.parts()[0]

    @property
    def role(self) -> str | None:
        return self.parts()[1]


    def to_dict(self):
        return {
            "link": self.link,
            "role": self.role
        }
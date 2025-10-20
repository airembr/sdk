import hashlib
import re
from uuid import uuid4

from durable_dot_dict.dotdict import DotDict
from pydantic import ValidationInfo
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler

# Compile the regex pattern once
OBJECT_TAG_PATTERN = re.compile(
    r'\$\(\s*([a-zA-Z0-9_-]+)\s*#\s*([a-zA-Z0-9_-]+)\s*\)'
)

class Instance(str):
    """
    Akceptowane formy
      *kind:role #id
      *kind:role #$id
      *kind:role #$id.#  itd.

    Części:
      *         – opcjonalna gwiazdka (aktor)
      kind      – wymagany typ
      :role     – opcjonalna rola
      #id[.#]   – opcjonalny identyfikator
                  $…   → reference = True
                  ….# → hashed_reference = True
    """

    _pattern = re.compile(r"""
        ^\s*
        (?P<actor>\*)?                     # gwiazdka
        \s*
        (?P<type>[A-Za-z_-]+)              # kind
        \s*
        (?: : \s* (?P<role>[A-Za-z_-]+) )? # :role
        \s*
        (?: \# \s* (?P<id>[^\s#]+) \s* \#? )? # #id (bez spacji i kolejnych #)
        \s*$
    """, re.VERBOSE)

    _split = re.compile(r'[:#]')

    # ── walidacja pydantic ─────────────────────────────────────
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: str, info: ValidationInfo | None = None):
        if v is None:
            raise ValueError(f"Instance has none value.")
        if not re.match(cls._pattern, v):
            raise ValueError(f"Invalid Instance string format: {v!r}")
        return cls(v)

    # ── podstawowe pola ────────────────────────────────────────
    # ── internal cache helpers ──────────────────────────────────
    def _parse_once(self):
        """
        Parsuje string dokładnie raz i zapisuje wynik w atrybucie
        `_parsed_parts`.  Wywołuj tylko z `parts()`.
        """
        m = self._pattern.match(self)
        if not m:  # nie powinno się zdarzyć,
            raise ValueError("Invalid Instance")  # bo validate już sprawdza

        kind = m.group("type").strip()

        role = m.group("role")
        role = role.strip() if role else None

        raw_id = m.group("id")
        if raw_id:
            raw_id = raw_id.strip()
            if raw_id.endswith('.'):  # obetnij trailing '.'
                raw_id = raw_id[:-1]

        actor_flag = bool(m.group("actor"))

        # zapisz tuple, żeby już nie parsować ponownie
        self._parsed_parts = (kind, role, raw_id, actor_flag)

    # ── semantics helpers ──────────────────────────────────────
    def parts(self) -> tuple[str | None, str | None, str | None, bool]:
        """
        Zwraca (kind, role, id, actor_flag).
        Jeśli to pierwsze wywołanie, parsuje i cache’uje wynik;
        kolejne odczyty korzystają z cache’u.
        """
        if not hasattr(self, "_parsed_parts"):
            self._parse_once()
        return self._parsed_parts

    # ── właściwości użytkowe ───────────────────────────────────
    @property
    def kind(self) -> str:
        return self.parts()[0]

    @property
    def role(self) -> str | None:
        return self.parts()[1]

    @property
    def actor(self) -> bool:
        return self.parts()[3]

    @property
    def id(self) -> str | None:
        """Zwraca oczyszczone ID – bez końcowej kropki, ale z ew. ‘$’."""
        raw = self.parts()[2]
        if raw and raw.endswith('.'):
            return raw[:-1]
        return raw

    @property
    def reference(self) -> bool:
        """True, jeśli ID zaczyna się od ‘$’."""
        return bool(self.id) and self.id.startswith('$')

    @property
    def hashed_reference(self) -> bool:
        """True, jeśli oryginalny napis kończy się ‘.#’."""
        return self.rstrip().endswith('.#')

    # ── pozostałe ──────────────────────────────────────────────
    def is_abstract(self) -> bool:
        return '#' not in self

    @staticmethod
    def _strip(val):
        return None if val is None else val.strip()

    def canonical(self) -> str:
        """Usuwa wszystkie spacje (wygodne jako klucz słownikowy)."""
        return self.replace(' ', '')

    def __str__(self):
        return self.canonical()

    def resolve_id(self, properties, generate_id=False) -> str:
        if not self.reference:
            if not self.hashed_reference:
                return self.id
            return hashlib.md5(self.id.encode()).hexdigest()

        # Reference

        properties = DotDict(properties)
        id_path = self.id[1:]

        if id_path not in properties:
            if not generate_id:
                raise ValueError(f"Path `{id_path}` not available in properties {list(properties.flat())}")
            else:
                return str(uuid4())

        id_value = properties[id_path]

        if not isinstance(id_value, (str, float, int)):
            raise ValueError(
                f"Path `{id_path}` in properties {properties.to_dict()} does not point to (str, float, int) and can not be used as id.")

        if not self.hashed_reference:
            return id_value

        return hashlib.md5(str(id_value).encode()).hexdigest()

    def pointer(self, properties=None):
        if self.reference and properties is None:
            raise ValueError(f"I need properties to hash instance that has id as reference to property value.")

        if self.is_abstract():
            return self.kind

        return f"{self.kind}#{self.resolve_id(properties)}"

    def link(self):
        if self.is_abstract():
            if self.role:
                return f"{self.kind}:{self.role}"
            return self.kind
        if self.role:
            return f"{self.kind}:{self.role}#{self.id}"
        return f"{self.kind}#{self.id}"

    def label(self):
        if self.role:
            return self.role
        return self.kind


    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler: GetCoreSchemaHandler):
        """
        Tells Pydantic how to validate and serialize this custom type.
        """
        return core_schema.no_info_after_validator_function(
            cls.validate,  # your existing validate() function
            core_schema.str_schema(),  # base schema
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler: GetJsonSchemaHandler):
        """
        Defines how it should appear in JSON Schema (for OpenAPI docs).
        """
        json_schema = handler(core_schema)
        json_schema.update(
            type="string",
            title="Instance",
            description="Custom string pattern: *kind:role#id or variants",
            examples=[
                "*user:author#$id",
                "task:owner#123",
                "project#abc.#",
            ],
        )
        return json_schema

